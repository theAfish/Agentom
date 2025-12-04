from typing import List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom.settings import settings
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
        # Create all specialized sub-agents
        structure_agent = create_structure_agent()
        mp_agent = create_mp_agent()
        vision_agent = create_vision_agent()
        wiki_agent = create_wiki_agent()
        
        # Enable direct communication between structure_agent and mp_agent
        structure_agent.sub_agents = [vision_agent]
        
        return Agent(
            model=LiteLlm(settings.DEFAULT_MODEL),
            name="coordinator_agent",
            description="Root coordinator agent that manages a specialized team of agents for materials science tasks.",
            instruction=(
                "You are the Coordinator Agent orchestrating a specialized team for materials science research. "
                "You have four specialist sub-agents available: "
                "1. 'mp_agent': Searches and downloads material structures from Materials Project. "
                "2. 'structure_agent': Performs atomic simulations and structure manipulations using ASE. "
                "3. 'wiki_agent': Provides information about materials science concepts and properties. "
                "\n"
                "Your job is to understand user requests and delegate them to the most appropriate agent(s). "
                "Analyze what the user is asking for and route the request accordingly. "
                "If multiple agents are needed, you can request information from multiple agents sequentially. "
                "Provide clear, synthesized responses to the user based on the agents' results."
            ),
            tools=[list_all_files],
            sub_agents=[structure_agent, mp_agent, wiki_agent],  # Enable auto-delegation
            output_key="last_coordination_result",  # Auto-save coordinator's response
        )
