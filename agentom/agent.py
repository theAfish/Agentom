
"""
Entry point for ADK agent team.

This module exports the root agent for use with ADK's web UI, CLI, or API server.
The root agent (coordinator) automatically manages the team of specialized agents.
"""

import sys
from pathlib import Path

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
import atexit
import signal
# from agentom.utils import clear_temp_dir, clear_input_dir, clear_workspace, transfer_outputs_to_target_dir, clear_output_dir


# Use configurable output archive directory
target_dir = str(settings.OUTPUT_ARCHIVE_DIR)


# Ensure workspace exists
settings.ensure_directories()

agentom = AgentFactory.create_coordinator_agent()

# Create the app for web UI and CLI compatibility
app = App(
    name=settings.APP_NAME,
    root_agent=agentom,
    resumability_config=ResumabilityConfig(is_resumable=True),
    # Register our custom logging plugin so the app's runner will call
    # our plugin hooks and the conversation/tool events will be recorded
    plugins=[CustomLoggingPlugin()],
)

