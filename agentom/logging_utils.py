import logging
import os
from datetime import datetime
from google.adk.plugins.base_plugin import BasePlugin

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workspace', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename), encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

# Configure root logger for ADK logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

# Add console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
root_logger.addHandler(console_handler)

logger = logging.getLogger("AgentLogger")
logger.setLevel(logging.INFO)

logger.info("Logging system initialized")

class CustomLoggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="custom_logging")

    def before_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent Start: {agent_name} ===")
        # Note: callback_context may contain messages, but logging input here if needed

    def after_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent End: {agent_name} ===")
        # Note: callback_context may contain result

    def before_tool_callback(self, *, tool, tool_args, tool_context):
        func_name = tool.name
        logger.info(f">>> Tool Call: {func_name}")
        logger.info(f"Arguments: {tool_args}")
        
    def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        func_name = tool.name
        logger.info(f"Tool {func_name} Result: {result}")
        logger.info(f"<<< Tool End: {func_name}")
