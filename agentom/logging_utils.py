import logging
import sys
from datetime import datetime
from google.adk.plugins.base_plugin import BasePlugin
from agentom.settings import settings

def setup_logging():
    """Configures the logging system."""
    log_filename = f"agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = settings.LOGS_DIR / log_filename

    handlers = []
    
    # File Handler
    if settings.LOG_TO_FILE:
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        handlers.append(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    handlers.append(console_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    for handler in handlers:
        root_logger.addHandler(handler)

    logger = logging.getLogger("AgentLogger")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.info(f"Logging system initialized. Log file: {log_path}")
    return logger

# Initialize logging
logger = setup_logging()

class CustomLoggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="custom_logging")

    def before_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent Start: {agent_name} ===")

    def after_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent End: {agent_name} ===")

    def before_tool_callback(self, *, tool, tool_args, tool_context):
        func_name = tool.name
        logger.info(f">>> Tool Call: {func_name}")
        logger.info(f"Arguments: {tool_args}")
        
    def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        func_name = tool.name
        logger.info(f"Tool {func_name} Result: {result}")
        logger.info(f"<<< Tool End: {func_name}")
