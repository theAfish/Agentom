import shutil
import sys
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from agentom.settings import settings


def create_wiki_agent():
    """
    Creates a Wiki/Information specialist agent.
    
    This agent can search for and provide information from knowledge bases
    like Wikipedia about chemical concepts and materials properties.
    """
    # Determine command and args for wikipedia-mcp
    mcp_command = shutil.which("wikipedia-mcp")
    mcp_args = []
    
    if not mcp_command:
        mcp_command = sys.executable
        mcp_args = ["-m", "wikipedia_mcp"]

    wiki_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=mcp_command,
                args=mcp_args,
            ),
        ),
    )

    return Agent(
        model=LiteLlm(settings.WIKI_MODEL),
        name="wiki_agent",
        description="Information specialist for chemical and materials science concepts. Searches knowledge bases.",
        instruction=(
            "You are an Information Specialist Agent focused on materials science and chemistry. "
            "Your tasks are to help explain concepts, properties, and information about materials and atoms. "
            "You can search for and retrieve conceptual information to help other agents understand their work. "
            "Use the available tools to find information requested by the user."
        ),
        tools=[wiki_toolset],
        output_key="last_wiki_result",  # Auto-save agent's response
    )
