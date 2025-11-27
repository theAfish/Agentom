from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from tools.data_tools import search_materials_project, download_structure
from tools.common_tools import list_files
from logging_utils import AgentLoggingMiddleware, FunctionLoggingMiddleware

def create_data_agent():
    return ChatAgent(
        chat_client=OpenAIChatClient(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_id="qwen-turbo",
            env_file_path=".env"
        ),
        instructions="You are a data access agent. You can search and download structures from Materials Project. Use the provided tools to find and retrieve material structures.",
        tools=[search_materials_project, download_structure, list_files],
        middleware=[AgentLoggingMiddleware(), FunctionLoggingMiddleware()]
    )
