from agent_framework import ChatAgent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from logging_utils import AgentLoggingMiddleware, FunctionLoggingMiddleware
import os
import shutil
import sys

class WikiAgentWrapper:
    def __init__(self):
        self.instructions = """You are a Wikipedia Agent. You can search for concepts and retrieve articles from Wikipedia.
        Use the available tools to find information requested by the user.
        """
        self.client = OpenAIChatClient(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_id="qwen3-max",
            env_file_path=".env"
        )
        
        self.agent = ChatAgent(
            chat_client=self.client,
            instructions=self.instructions,
            middleware=[AgentLoggingMiddleware(), FunctionLoggingMiddleware()]
        )
        
        # Path to the wikipedia-mcp executable
        # Try to find the executable in the system PATH
        self.mcp_command = shutil.which("wikipedia-mcp")
        self.mcp_args = []
        
        # If not found in PATH, try to run as a python module
        if not self.mcp_command:
            self.mcp_command = sys.executable
            self.mcp_args = ["-m", "wikipedia_mcp"]

    async def run(self, task: str) -> str:
        # Create the MCP tool context for this run
        # We use the MCPStdioTool to connect to the wikipedia-mcp server
        async with MCPStdioTool(
            name="wikipedia",
            command=self.mcp_command,
            args=self.mcp_args 
        ) as mcp_server:
            # Pass the tool to the agent's run method
            return await self.agent.run(task, tools=mcp_server)

def create_wiki_agent():
    return WikiAgentWrapper()
