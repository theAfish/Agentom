from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom.tools.mp_tools import (
    download_materials_info_by_formula,
    download_materials_info_by_chemical_system,
    download_materials_info_by_symmetry,
    download_materials_info_by_mpid,
    view_data_file,
    convert_all_data_to_structure_files,
    convert_one_datus_to_structure_file,
    sample_data_from_json
)
from agentom.tools.common_tools import list_files
from agentom.settings import settings

agent_description = "MP specialist for Materials Project. Searches and downloads material structures."
agent_instruction = """
You are an MP Agent specializing in the Materials Project database. Your ONLY tasks are: 
1. Search for materials using various criteria (formula, chemical system, structure). 
2. Download structure files for found materials.
3. List available files.
4. If you need to analyze or manipulate atomic structures, you can delegate to structure_agent.
5. Do not perform simulations or other tasks.
6. Always provide the user with clear information about search results and download status.
Please avoid directly reading through the entire dataset whenever possible, as it may contain a large number of tokens.
"""


def create_mp_agent():
    """
    Creates an MP specialist agent for Materials Project.
    
    This agent specializes in searching and downloading material structures
    from external databases like Materials Project.
    """
    return Agent(
        model=LiteLlm(settings.MP_MODEL),
        name="mp_agent",
        description=agent_description,
        instruction=agent_instruction,
        tools=[
            download_materials_info_by_formula,
            download_materials_info_by_chemical_system,
            download_materials_info_by_symmetry,
            download_materials_info_by_mpid,
            view_data_file,
            convert_all_data_to_structure_files,
            convert_one_datus_to_structure_file,
            sample_data_from_json,
            list_files,
        ],
        output_key="last_mp_result",  # Auto-save agent's response
    )
