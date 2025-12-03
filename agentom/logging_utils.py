import logging
import os
from datetime import datetime
from google.adk.plugins.base_plugin import BasePlugin

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename), encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("AgentLogger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class CustomLoggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="custom_logging")

    async def before_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent Start: {agent_name} ===")
        # Note: callback_context may contain messages, but logging input here if needed

    async def after_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent End: {agent_name} ===")
        # Note: callback_context may contain result

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        func_name = tool.name
        logger.info(f">>> Tool Call: {func_name}")
        logger.info(f"Arguments: {tool_args}")
        
    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        func_name = tool.name
        logger.info(f"Tool {func_name} Result: {result}")
        logger.info(f"<<< Tool End: {func_name}")
