from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from agentom.tools.structure_tools import (
    read_structure,
    read_structures_in_text,
    calculate_distance,
    build_supercell,
    build_surface,
    build_interface,
    check_close_atoms,
)
from agentom.tools.common_tools import list_all_files, write_file, run_python_script
from agentom.settings import settings

agent_description = "Expert in atomic modelling using Python, ASE, and Pymatgen. Handles structure manipulation, supercell generation, and atomic calculations."
agent_instruction = """
You are an expert in atomic modelling using Python, ASE, and Pymatgen. Your ONLY tasks are: 
1. Read and analyze atomic structures from files.
2. Write python scripts to perform structure manipulation and modeling.
3. Build structures according to user specifications.
4. Execute scripts to perform calculations, modeling and return results.
5. Please ensure all generated structures are physically reasonable.
6. Avoid reading structure files in text format unless you know it is short.
Always verify file existence before operations and provide clear error messages if operations fail.
If you need to search for materials from external databases like Materials Project, you can delegate to mp_agent.
Do not engage in tasks outside your scope.
"""

def create_structure_agent():
    """
    Creates a Structure specialist agent.
    
    This agent is specialized in atomic structure manipulation and simulation.
    It can read structures, perform calculations, generate supercells, and create surface slabs.
    """
    return Agent(
        model=LiteLlm(settings.STRUCTURE_MODEL),
        name="structure_agent",
        description=agent_description,
        instruction=agent_instruction,
        tools=[
            list_all_files,
            read_structure,
            read_structures_in_text,
            calculate_distance,
            build_supercell,
            build_surface,
            build_interface,
            write_file,
            check_close_atoms,
            run_python_script,
            # FunctionTool(run_python_script, require_confirmation=True),
        ],
        output_key="last_ase_result",  # Auto-save agent's response
    )
