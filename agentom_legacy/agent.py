from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom_legacy.tools.ase_tools import *
from google.adk.code_executors import gke_code_executor


root_agent = Agent(
    model=LiteLlm('openai/qwen-turbo-2025-04-28'),
    name='ase_agent',
    description="Checks and manages files related to Atomic Simulation Environment (ASE).",
    instruction="You are a helpful assistant that manages files with ASE. Use the appropriate tools for this purpose. Before performing any file operations, always check the available files first.",
    tools=[
        list_all_files,
        read_structure,
        calculate_distance,
        read_structures_in_text,
        supercell_generation,
        create_surface_slab,
    ],
)




