
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
from google.adk.apps import App, ResumabilityConfig

# Ensure workspace exists (handled by settings)
settings.ensure_directories()

# Create and export the root agent
# This is the entry point that ADK will use when running via web UI, CLI, or API server
root_agent = AgentFactory.create_coordinator_agent()

# Create the app for web UI and CLI compatibility
app = App(
    name=settings.APP_NAME,
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
