import logging
import sys
from datetime import datetime
from google.adk.plugins.base_plugin import BasePlugin
from agentom.settings import settings

def setup_logging():
    """Configures the logging system."""

    handlers = []

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    handlers.append(console_handler)

    # Configure root logger
    # Configure the root logger safely (console + optional file)
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    for handler in handlers:
        root_logger.addHandler(handler)

    # Create a dedicated named logger for this project so ADK's global
    # logger configuration (which may overwrite the root logger) won't
    # stop our file logging. We set propagate=False so it doesn't bubble to
    # the root logger.
    agent_logger = logging.getLogger("agentom")
    agent_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    agent_logger.propagate = False

    # Ensure there's at least one console handler on the agent logger for development
    if not any(isinstance(h, logging.StreamHandler) for h in agent_logger.handlers):
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        agent_logger.addHandler(ch)

    agent_logger.info("Logging system initialized.")
    return agent_logger

# Initialize logging
logger = setup_logging()

class CustomLoggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="custom_logging")

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # Set session-specific workspace
        session_id = invocation_context.session.id if hasattr(invocation_context, 'session') and invocation_context.session else 'default_session'
        settings.set_session_workspace(session_id)

        # print("===================================================")
        # print(f"Session workspace set to: {settings.WORKSPACE_DIR}")
        
        # Remove any existing file handlers to ensure per-session logging
        for h in logger.handlers[:]:
            if isinstance(h, logging.FileHandler):
                logger.removeHandler(h)
                h.close()
        
        # Add file handler if logging to file
        if settings.LOG_TO_FILE:
            log_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}.log"
            log_path = settings.LOGS_DIR / log_filename
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
            logger.addHandler(file_handler)
            logger.info(f"Log file set: {log_path}")
        
        # Record the raw user message content
        try:
            text = ''.join(p.text or '' for p in (user_message.parts or []))
        except Exception:
            text = str(user_message)
        logger.info(f"[USER] ({invocation_context.session_id if hasattr(invocation_context, 'session_id') else 'no-session'}): {text}")

    async def before_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        logger.info(f"=== Agent Start: {agent_name} ===")

    async def after_agent_callback(self, *, agent, callback_context):
        agent_name = agent.name or "Unknown"
        # The callback_context often contains the response content/events; try to extract and log any agent reply
        try:
            reply_parts = callback_context.response.content.parts if hasattr(callback_context, 'response') and callback_context.response and callback_context.response.content else None
            if reply_parts:
                text = ''.join(part.text or '' for part in reply_parts)
                logger.info(f"[AGENT:{agent_name}] {text}")
        except Exception:
            # fallback markers
            logger.info(f"=== Agent End: {agent_name} ===")

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        func_name = getattr(tool, 'name', repr(tool))
        logger.info(f">>> Tool Call: {func_name}")
        logger.info(f"Tool args: {tool_args}")

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        func_name = getattr(tool, 'name', repr(tool))
        logger.info(f"Tool {func_name} Result: {result}")
        logger.info(f"<<< Tool End: {func_name}")

    async def on_event_callback(self, *, invocation_context, event):
        # Log generic events yielded from the runner (tool starts/completions, etc.)
        try:
            logger.debug(f"Event: {type(event).__name__} -> {repr(event)}")
        except Exception:
            logger.debug(f"Event: {repr(event)}")

    async def after_model_callback(self, *, callback_context, llm_response):
        # Log the model output (LLM response parts)
        try:
            parts = llm_response.content.parts if llm_response and llm_response.content else None
            if parts:
                text = ''.join(p.text or '' for p in parts)
                logger.info(f"[MODEL RESPONSE] {text}")
        except Exception:
            logger.debug(f"LLM response: {repr(llm_response)}")

    async def on_model_error_callback(self, *, callback_context, llm_request, error):
        logger.error(f"Model error: {error} for request {llm_request}")

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        logger.error(f"Tool error in {getattr(tool, 'name', repr(tool))}: {error} | args: {tool_args}")
