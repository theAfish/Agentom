from agent_framework import ChatAgent, ai_function, ChatMessage, DataContent, Role, TextContent
from agent_framework.openai import OpenAIChatClient
from typing import Annotated
from pathlib import Path
from .ase_agent import create_ase_agent
from .data_access import create_data_agent
from .vision_agent import create_vision_agent
from .wiki_agent import create_wiki_agent
from tools.common_tools import read_file, write_file, list_files, execute_code
from tools.ase_tools import generate_structure_image
from logging_utils import AgentLoggingMiddleware, FunctionLoggingMiddleware

# Instantiate agents
ase_agent = create_ase_agent()
data_agent = create_data_agent()
vision_agent = create_vision_agent()
wiki_agent = create_wiki_agent()

@ai_function
async def ask_ase_agent(task: Annotated[str, "Task for the ASE agent"]) -> str:
    """Delegates a task to the ASE Agent (Atomic Simulation Environment)."""
    try:
        return await ase_agent.run(task)
    except Exception as e:
        return f"Error calling ASE Agent: {e}"

@ai_function
async def ask_data_agent(task: Annotated[str, "Task for the Data Access Agent"]) -> str:
    """Delegates a task to the Data Access Agent."""
    try:
        return await data_agent.run(task)
    except Exception as e:
        return f"Error calling Data Access Agent: {e}"

@ai_function
async def ask_wiki_agent(task: Annotated[str, "Task for the Wiki Agent"]) -> str:
    """Delegates a task to the Wiki Agent to search Wikipedia."""
    try:
        return await wiki_agent.run(task)
    except Exception as e:
        return f"Error calling Wiki Agent: {e}"

@ai_function
async def visually_inspect_structure(
    file_name: Annotated[str, "The name of the structure file (e.g., .cif) to inspect"],
    query: Annotated[str, "The question or query about the structure"]
) -> str:
    """Generates an image of the structure and asks the Vision Agent to inspect it."""
    try:
        # Generate image
        image_name = f"vision_check_{file_name}.png"
        # Try to generate image assuming file is in root of workspace
        # Note: generate_structure_image is synchronous
        result = generate_structure_image(folder=".", file_name=file_name, output_image_name=image_name)
        
        if "error" in result:
            return f"Error generating image: {result['error']}"
        
        image_rel_path = result["output_image_file"]
        
        # Resolve workspace path
        base_dir = Path(__file__).resolve().parent.parent
        workspace_dir = base_dir / "workspace"
        image_path = workspace_dir / image_rel_path
        
        if not image_path.exists():
            return f"Error: Generated image not found at {image_path}"
            
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        # Create message with image
        message = ChatMessage(
            role=Role.USER,
            contents=[
                TextContent(text=f"Structure: {file_name}. Query: {query}"),
                DataContent(data=image_data, media_type="image/png")
            ]
        )
        
        response = await vision_agent.run(message)
        return response.text
        
    except Exception as e:
        return f"Error calling Vision Agent: {e}"

def create_coordinator_agent():
    return ChatAgent(
        chat_client=OpenAIChatClient(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_id="qwen3-max",
            env_file_path=".env"
        ),
        instructions="""You are the Coordinator Agent. You manage a multi-agent system.
        You have access to four other agents:
        1. Data Access Agent: Can search and download materials.
        2. ASE Agent: Can perform atomic simulations and structure manipulations.
        3. Vision Checking Agent: Can visually inspect structures and answer questions about them.
        4. Wiki Agent: Can search Wikipedia for concepts and information.
        
        You also have tools to read/write files and execute code in the workspace.
        
        When a user asks for a complex task:
        1. Analyze the request.
        2. If data is needed, ask the Data Access Agent.
        3. If simulation/modeling is needed, ask the ASE Agent.
        4. If visual inspection or checking is needed, ask the Vision Checking Agent.
        5. If general knowledge or concept search is needed, ask the Wiki Agent.
        6. You can coordinate the flow of information between them.
        
        Always explain your plan to the user.
        """,
        tools=[ask_ase_agent, ask_data_agent, visually_inspect_structure, ask_wiki_agent, read_file, write_file, list_files, execute_code],
        middleware=[AgentLoggingMiddleware(), FunctionLoggingMiddleware()]
    )
