
"""
Entry point for ADK agent team.

This module exports the root agent for use with ADK's web UI, CLI, or API server.
The root agent (coordinator) automatically manages the team of specialized agents.
"""

import sys
from pathlib import Path

from starlette.staticfiles import StaticFiles

# Add the parent directory to sys.path to ensure agentom package is resolvable
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from agentom.factory import AgentFactory
from agentom.settings import settings
from agentom.logging_utils import CustomLoggingPlugin, logger
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.apps import App, ResumabilityConfig
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import atexit
import signal
# from agentom.utils import clear_temp_dir, clear_input_dir, clear_workspace, transfer_outputs_to_target_dir, clear_output_dir


# Use configurable output archive directory
target_dir = str(settings.OUTPUT_ARCHIVE_DIR)



agentom = AgentFactory.create_coordinator_agent()

# Shared plugins for both app and a2a_app
plugins = [CustomLoggingPlugin()]

# Create the app for web UI and CLI compatibility
app = App(
    name=settings.APP_NAME,
    root_agent=agentom,
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=plugins,
)

# Create a runner with the same plugins for the a2a app
a2a_runner = Runner(
    app_name=settings.APP_NAME,
    agent=agentom,
    plugins=plugins,
    session_service=InMemorySessionService(),
)

a2a_app = to_a2a(
    agentom,
    host=settings.A2A_HOST,
    port=settings.A2A_PORT,
    protocol=settings.A2A_PROTOCOL,
    runner=a2a_runner,
)
a2a_app.mount("/artifacts", StaticFiles(directory=settings.WORKSPACE_ROOT), name="artifacts")