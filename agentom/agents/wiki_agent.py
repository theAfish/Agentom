from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_wiki_agent():
    """
    Creates a Wiki/Information specialist agent.
    
    This agent can search for and provide information from knowledge bases
    like Wikipedia about chemical concepts and materials properties.
    """
    return Agent(
        model=LiteLlm("openai/qwen3-max"),
        name="wiki_agent",
        description="Information specialist for chemical and materials science concepts. Searches knowledge bases.",
        instruction=(
            "You are an Information Specialist Agent focused on materials science and chemistry. "
            "Your tasks are to help explain concepts, properties, and information about materials and atoms. "
            "You can search for and retrieve conceptual information to help other agents understand their work. "
            "Note: You currently have limited direct tool access. Please provide your best knowledge-based responses."
        ),
        tools=[],  # Add Wikipedia or knowledge base tools here when available
        output_key="last_wiki_result",  # Auto-save agent's response
    )
