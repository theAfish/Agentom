import asyncio
from google.adk import Runner
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import UnsafeLocalCodeExecutor, ContainerCodeExecutor
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.genai import types


AGENT_NAME = "ase_coding_agent"
USER_ID = "test_user"
SESSION_ID = "ase_coding_session"
APP_NAME = "ase_coding_app"

container_executor_instance = ContainerCodeExecutor(image="atom-op-space")

root_agent = Agent(
    model=LiteLlm('openai/qwen-turbo-2025-04-28'),  #qwen3-max   qwen-turbo-2025-04-28
    name=AGENT_NAME,
    description="Checks and manages files related to Atomic Simulation Environment (ASE).",
    instruction="You are a helpful assistant that manages files with ASE. Please write codes to handle users' requirements.",
    code_executor=container_executor_instance
)
