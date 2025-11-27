import logging
import os
from datetime import datetime
from agent_framework import AgentMiddleware, AgentRunContext, FunctionMiddleware, FunctionInvocationContext

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure the root logger to write to file
# We use a separate logger to avoid interfering with other loggers if possible,
# but basicConfig affects the root logger.
# Since agent_framework uses its own logger, we can configure that one too if needed.
# But here we just want to log our middleware events.

file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename), encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("AgentLogger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class AgentLoggingMiddleware(AgentMiddleware):
    async def process(self, context: AgentRunContext, next):
        agent_name = context.agent.name or context.agent.id
        logger.info(f"=== Agent Start: {agent_name} ===")
        for msg in context.messages:
            # msg.contents is a list of ContentItem
            logger.info(f"Message ({msg.role}): {msg.contents}")
        
        try:
            await next(context)
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
            raise e
            
        if context.result:
            # context.result is AgentRunResponse
            logger.info(f"Agent {agent_name} Result: {context.result}")
        logger.info(f"=== Agent End: {agent_name} ===")

class FunctionLoggingMiddleware(FunctionMiddleware):
    async def process(self, context: FunctionInvocationContext, next):
        func_name = context.function.name
        logger.info(f">>> Tool Call: {func_name}")
        logger.info(f"Arguments: {context.arguments}")
        
        try:
            await next(context)
        except Exception as e:
            logger.error(f"Tool {func_name} failed: {e}", exc_info=True)
            raise e
            
        logger.info(f"Tool {func_name} Result: {context.result}")
        logger.info(f"<<< Tool End: {func_name}")
