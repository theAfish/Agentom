from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from tools.ase_tools import list_all_files, read_structure, read_structures_in_text, calculate_distance, supercell_generation, create_surface_slab, run_python_script
from tools.common_tools import write_file
from logging_utils import AgentLoggingMiddleware, FunctionLoggingMiddleware

def create_ase_agent():
    return ChatAgent(
        chat_client=OpenAIChatClient(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_id="qwen3-max",
            env_file_path=".env"
        ),
        instructions="You are an expert in atomic simulation using ASE. You can read structures, calculate distances, generate supercells, and create surface slabs. You can also write and execute Python scripts to perform complex modelling tasks not covered by other tools. Always verify file existence before operations.",
        tools=[list_all_files, read_structure, read_structures_in_text, calculate_distance, supercell_generation, create_surface_slab, write_file, run_python_script],
        middleware=[AgentLoggingMiddleware(), FunctionLoggingMiddleware()]
    )
