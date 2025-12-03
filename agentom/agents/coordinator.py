from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .ase_agent import create_ase_agent
from .data_access import create_data_agent
from .vision_agent import create_vision_agent
from .wiki_agent import create_wiki_agent


def create_coordinator_agent():
    """
    Creates the Coordinator/Root agent that manages the multi-agent team.
    
    This agent acts as the orchestrator, automatically delegating tasks to
    specialized sub-agents based on the user's request and each agent's description.
    Uses ADK's automatic delegation (auto-flow) mechanism via sub_agents parameter.
    """
    # Create all specialized sub-agents
    ase_agent = create_ase_agent()
    data_agent = create_data_agent()
    vision_agent = create_vision_agent()
    wiki_agent = create_wiki_agent()
    
    return Agent(
        model=LiteLlm("openai/qwen3-max"),
        name="coordinator_agent",
        description="Root coordinator agent that manages a specialized team of agents for materials science tasks.",
        instruction=(
            "You are the Coordinator Agent orchestrating a specialized team for materials science research. "
            "You have four specialist sub-agents available: "
            "1. 'data_access_agent': Searches and downloads material structures from Materials Project. "
            "2. 'ase_agent': Performs atomic simulations and structure manipulations using ASE. "
            "3. 'vision_agent': Visually analyzes and inspects atomic structure images. "
            "4. 'wiki_agent': Provides information about materials science concepts and properties. "
            "\n"
            "Your job is to understand user requests and delegate them to the most appropriate agent(s). "
            "Analyze what the user is asking for and route the request accordingly. "
            "If multiple agents are needed, you can request information from multiple agents sequentially. "
            "Provide clear, synthesized responses to the user based on the agents' results."
        ),
        tools=[],  # Coordinator uses delegation, not direct tools
        sub_agents=[ase_agent, data_agent, vision_agent, wiki_agent],  # Enable auto-delegation
        output_key="last_coordination_result",  # Auto-save coordinator's response
    )
