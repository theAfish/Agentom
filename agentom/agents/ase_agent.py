from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from tools.ase_tools import (
    list_all_files,
    read_structure,
    read_structures_in_text,
    calculate_distance,
    supercell_generation,
    create_surface_slab,
    run_python_script,
)
from tools.common_tools import write_file


def create_ase_agent():
    """
    Creates an ASE (Atomic Simulation Environment) specialist agent.
    
    This agent is specialized in atomic structure manipulation and simulation.
    It can read structures, perform calculations, generate supercells, and create surface slabs.
    """
    return Agent(
        model=LiteLlm("openai/qwen3-max"),
        name="ase_agent",
        description="Expert in atomic simulation using ASE. Handles structure manipulation, supercell generation, and atomic calculations.",
        instruction=(
            "You are an expert in atomic simulation using ASE (Atomic Simulation Environment). "
            "Your ONLY tasks are: "
            "1. Read and analyze atomic structures from files. "
            "2. Calculate distances between atoms. "
            "3. Generate supercells from structures. "
            "4. Create surface slabs. "
            "5. Write structures to files. "
            "6. Execute Python scripts for complex simulations. "
            "Always verify file existence before operations and provide clear error messages if operations fail. "
            "Do not engage in tasks outside your scope."
        ),
        tools=[
            list_all_files,
            read_structure,
            read_structures_in_text,
            calculate_distance,
            supercell_generation,
            create_surface_slab,
            write_file,
            FunctionTool(run_python_script, require_confirmation=True),
        ],
        output_key="last_ase_result",  # Auto-save agent's response
    )
