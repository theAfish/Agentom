from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom.settings import settings
from .structure_agent import create_structure_agent
from .mp_agent import create_mp_agent
from .vision_agent import create_vision_agent
from .wiki_agent import create_wiki_agent
from agentom.tools.common_tools import list_all_files, write_file
from agentom.tools.transfer_tools import (
    select_workspace_files_for_transfer,
)


agent_description = "Root agent that manages a specialized team of agents for materials science tasks."
agent_instruction = """
You are the Coordinator Agent orchestrating a specialized team for materials science research. You have four specialist sub-agents available:
1. 'mp_agent': Searches and downloads material structures from Materials Project. 
2. 'structure_agent': Performs atomic simulations and structure manipulations using ASE. 
3. 'vision_agent': Visually analyzes and inspects atomic structure images. 
4. 'wiki_agent': Provides information about materials science concepts and properties. 

Your job is to understand user requests and delegate them to the most appropriate agent(s).
Analyze what the user is asking for and route the request accordingly. 
If multiple agents are needed, you can request information from multiple agents sequentially. 
For complex tasks, please write a clear TODO list and guide the sub-agents for handling them. 
Provide clear, synthesized responses to the user based on the agents' results.
The user may provide structure files or other inputs inside the 'inputs' directory. So you can check there if needed.
If you are working as a downstream agent, always select the desired final results and transfer back.

When asked to share files with remote callers or provide files for transfer:
- Use 'select_workspace_files_for_transfer' with paths to files generated during the session
- File paths can be relative to the current workspace (e.g., "outputs/file.cif")
- The tool will return downloadable HTTP URIs for remote access
"""


def create_coordinator_agent():
    """
    Create the canonical coordinator/root agent for the agentom team.

    This function centralizes coordinator creation and uses values from
    `agentom.settings.settings` so the model and other defaults can be
    configured from environment or a single settings source.
    """
    # Create all specialist sub-agents
    structure_agent = create_structure_agent()
    mp_agent = create_mp_agent()
    vision_agent = create_vision_agent()
    wiki_agent = create_wiki_agent()

    # Keep the structure agent able to delegate to vision (existing behaviour)
    structure_agent.sub_agents = [vision_agent]

    return Agent(
        model=LiteLlm(settings.AGENTOM_MODEL),
        name="agentom",
        description=agent_description,
        instruction=agent_instruction,
        tools=[
            list_all_files,
            write_file,
            select_workspace_files_for_transfer,
        ],
        sub_agents=[structure_agent, mp_agent, wiki_agent],
        output_key="last_coordination_result",
    )
