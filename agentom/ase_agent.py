import asyncio  
from tools.ase_tools import *

from agent_framework import ChatAgent  
from agent_framework.openai import OpenAIChatClient  
import os
from pathlib import Path

# the current workspace directory
# WORKSPACE_DIR = Path(__file__).parent / "workspace"


agent = OpenAIChatClient(  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_id="qwen-turbo",
    env_file_path=".env"
).create_agent(
    instructions="You are a helpful assistant that manages files with ASE. Use the appropriate tools for this purpose. Before performing any file operations, always check the available files first.",
    name="ase_agent",
    tools=[list_all_files, read_structure, read_structures_in_text, calculate_distance, supercell_generation, create_surface_slab],
)



thread = agent.get_new_thread()  
async def main():
      
    while True:  
        user_input = input("\nUser (or 'exit' to quit): ")  
        if user_input.lower() == 'exit':  
            break  
              
        print("Agent: ", end="", flush=True)  
        async for update in agent.run_stream(user_input, thread=thread):  
            if update.text:  
                print(update.text, end="", flush=True)  
        print()  


asyncio.run(main())