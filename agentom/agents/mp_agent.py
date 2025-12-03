from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.mp_tools import (
    search_materials_project,
    search_materials_by_formula,
    search_materials_by_chemical_system,
    search_materials_by_structure,
)
from tools.common_tools import list_files


def create_mp_agent():
    """
    Creates an MP specialist agent for Materials Project.
    
    This agent specializes in searching and downloading material structures
    from external databases like Materials Project.
    """
    return Agent(
        model=LiteLlm("openai/qwen-turbo"),
        name="mp_agent",
        description="MP specialist for Materials Project. Searches and downloads material structures.",
        instruction=(
            "You are an MP Agent specializing in the Materials Project database. "
            "Your ONLY tasks are: "
            "1. Search for materials using various criteria (formula, chemical system, structure). "
            "2. Download structure files for found materials. "
            "3. List available files. "
            "Do not perform simulations or other tasks. "
            "Always provide the user with clear information about search results and download status."
        ),
        tools=[
            search_materials_project,
            search_materials_by_formula,
            search_materials_by_chemical_system,
            search_materials_by_structure,
            list_files,
        ],
        output_key="last_mp_result",  # Auto-save agent's response
    )
