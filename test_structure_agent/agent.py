from google.adk.apps import App, ResumabilityConfig

from agentom.agents.structure_agent import create_structure_agent
from agentom.logging_utils import CustomLoggingPlugin
from agentom.settings import settings


app = App(
    name=f"{settings.APP_NAME}_structure",
    root_agent=create_structure_agent(),
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=[CustomLoggingPlugin()],
)
