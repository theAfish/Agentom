import asyncio
import os
from dataclasses import dataclass
from typing import Any, Literal
from uuid import uuid4

from typing_extensions import Never

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    Case,
    Default,
)
from agent_framework.openai import OpenAIChatClient
from pydantic import BaseModel


class DetectionResultAgent(BaseModel):
    """Structured output returned by the spam detection agent."""

    # The agent classifies the email into one of three categories
    spam_decision: Literal["NotSpam", "Spam", "Uncertain"]
    reason: str

class EmailResponse(BaseModel):
    """Structured output returned by the email assistant agent."""

    response: str

@dataclass
class DetectionResult:
    """Internal typed payload used for routing and downstream handling."""

    spam_decision: str
    reason: str
    email_id: str

@dataclass
class Email:
    """In memory record of the email content stored in shared state."""

    email_id: str
    email_content: str


def get_case(expected_decision: str):
    """Factory that returns a predicate matching a specific spam_decision value."""

    def condition(message: Any) -> bool:
        # Only match when the upstream payload is a DetectionResult with the expected decision
        return isinstance(message, DetectionResult) and message.spam_decision == expected_decision

    return condition


EMAIL_STATE_PREFIX = "email:"
CURRENT_EMAIL_ID_KEY = "current_email_id"

@executor(id="store_email")
async def store_email(email_text: str, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    """Store email content once and pass around a lightweight ID reference."""

    # Persist the raw email content in shared state
    new_email = Email(email_id=str(uuid4()), email_content=email_text)
    await ctx.set_shared_state(f"{EMAIL_STATE_PREFIX}{new_email.email_id}", new_email)
    await ctx.set_shared_state(CURRENT_EMAIL_ID_KEY, new_email.email_id)

    # Forward email to spam detection agent
    await ctx.send_message(
        AgentExecutorRequest(messages=[ChatMessage(Role.USER, text=new_email.email_content)], should_respond=True)
    )

@executor(id="to_detection_result")
async def to_detection_result(response: AgentExecutorResponse, ctx: WorkflowContext[DetectionResult]) -> None:
    """Transform agent response into a typed DetectionResult with email ID."""

    # Parse the agent's structured JSON output
    parsed = DetectionResultAgent.model_validate_json(response.agent_run_response.text)
    email_id: str = await ctx.get_shared_state(CURRENT_EMAIL_ID_KEY)

    # Create typed message for switch-case routing
    await ctx.send_message(DetectionResult(
        spam_decision=parsed.spam_decision,
        reason=parsed.reason,
        email_id=email_id
    ))

@executor(id="submit_to_email_assistant")
async def submit_to_email_assistant(detection: DetectionResult, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    """Handle NotSpam emails by forwarding to the email assistant."""

    # Guard against misrouting
    if detection.spam_decision != "NotSpam":
        raise RuntimeError("This executor should only handle NotSpam messages.")

    # Retrieve original email content from shared state
    email: Email = await ctx.get_shared_state(f"{EMAIL_STATE_PREFIX}{detection.email_id}")
    await ctx.send_message(
        AgentExecutorRequest(messages=[ChatMessage(Role.USER, text=email.email_content)], should_respond=True)
    )

@executor(id="finalize_and_send")
async def finalize_and_send(response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]) -> None:
    """Parse email assistant response and yield final output."""

    parsed = EmailResponse.model_validate_json(response.agent_run_response.text)
    await ctx.yield_output(f"Email sent: {parsed.response}")

@executor(id="handle_spam")
async def handle_spam(detection: DetectionResult, ctx: WorkflowContext[Never, str]) -> None:
    """Handle confirmed spam emails."""

    if detection.spam_decision == "Spam":
        await ctx.yield_output(f"Email marked as spam: {detection.reason}")
    else:
        raise RuntimeError("This executor should only handle Spam messages.")

@executor(id="handle_uncertain")
async def handle_uncertain(detection: DetectionResult, ctx: WorkflowContext[Never, str]) -> None:
    """Handle uncertain classifications that need manual review."""

    if detection.spam_decision == "Uncertain":
        # Include original content for human review
        email: Email | None = await ctx.get_shared_state(f"{EMAIL_STATE_PREFIX}{detection.email_id}")
        await ctx.yield_output(
            f"Email marked as uncertain: {detection.reason}. Email content: {getattr(email, 'email_content', '')}"
        )
    else:
        raise RuntimeError("This executor should only handle Uncertain messages.")


async def main():
    # Create agents
    chat_client = OpenAIChatClient(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="qwen-turbo",
        env_file_path=".env"
    )

    # Enhanced spam detection agent with three-way classification
    spam_detection_agent = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You are a spam detection assistant that identifies spam emails. "
                "Be less confident in your assessments. "
                "Always return JSON with fields 'spam_decision' (one of NotSpam, Spam, Uncertain) "
                "and 'reason' (string)."
            ),
            response_format=DetectionResultAgent,
        ),
        id="spam_detection_agent",
    )

    # Email assistant remains the same
    email_assistant_agent = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You are an email assistant that helps users draft responses to emails with professionalism."
            ),
            response_format=EmailResponse,
        ),
        id="email_assistant_agent",
    )

    # Build workflow using switch-case for cleaner three-way routing
    workflow = (
        WorkflowBuilder()
        .set_start_executor(store_email)
        .add_edge(store_email, spam_detection_agent)
        .add_edge(spam_detection_agent, to_detection_result)
        .add_switch_case_edge_group(
            to_detection_result,
            [
                # Explicit cases for specific decisions
                Case(condition=get_case("NotSpam"), target=submit_to_email_assistant),
                Case(condition=get_case("Spam"), target=handle_spam),
                # Default case catches anything that doesn't match above
                Default(target=handle_uncertain),
            ],
        )
        .add_edge(submit_to_email_assistant, email_assistant_agent)
        .add_edge(email_assistant_agent, finalize_and_send)
        .build()
    )


    # Use ambiguous email content that might trigger uncertain classification
    email = (
        "Hey there, I noticed you might be interested in our latest offer—no pressure, but it expires soon. "
        "Let me know if you'd like more details."
    )

    # Execute and display results
    events = await workflow.run(email)
    outputs = events.get_outputs()
    if outputs:
        for output in outputs:
            print(f"Workflow output: {output}")


if __name__ == "__main__":
    asyncio.run(main())
