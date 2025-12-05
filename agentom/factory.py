from typing import List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom.settings import settings
from agentom.agents.coordinator import create_coordinator_agent as _create_coordinator_agent
from agentom.agents.structure_agent import create_structure_agent
from agentom.agents.mp_agent import create_mp_agent
from agentom.agents.vision_agent import create_vision_agent
from agentom.agents.wiki_agent import create_wiki_agent
from agentom.tools.common_tools import list_all_files

class AgentFactory:
    @staticmethod
    def create_coordinator_agent() -> Agent:
        """
        Creates the Coordinator/Root agent that manages the multi-agent team.
        """
        # Delegate to the canonical coordinator implementation in agents
        return _create_coordinator_agent()
