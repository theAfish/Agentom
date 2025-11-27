from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from tools.ase_tools import generate_structure_image, list_all_files
from tools.vision_tools import get_image_content
from logging_utils import AgentLoggingMiddleware, FunctionLoggingMiddleware

def create_vision_agent():
    return ChatAgent(
        chat_client=OpenAIChatClient(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_id="qwen3-omni-flash",
            env_file_path=".env"
        ),
        instructions="""You are a Vision Checking Agent. Your goal is to visually inspect atomic structures.
        You are powered by a Vision Language Model (Qwen-VL), so you can see images directly.
        
        You will receive an image of the structure along with a query.
        Analyze the image and answer the user's questions about the structure.
        
        Always explain what you see in the image to justify your answer.
        """,
        tools=[],
        middleware=[AgentLoggingMiddleware(), FunctionLoggingMiddleware()]
    )
