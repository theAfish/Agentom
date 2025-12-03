
"""
Entry point for ADK agent team.

This module exports the root agent for use with ADK's web UI, CLI, or API server.
The root agent (coordinator) automatically manages the team of specialized agents.
"""

import os
import sys

# Add the current directory to sys.path to ensure imports work as expected
# when loaded by adk
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agents.coordinator import create_coordinator_agent
from google.adk.apps import App, ResumabilityConfig

# Ensure workspace exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(BASE_DIR, 'workspace')
os.makedirs(WORKSPACE, exist_ok=True)

# Create and export the root agent
# This is the entry point that ADK will use when running via web UI, CLI, or API server
root_agent = create_coordinator_agent()

# Create the app for web UI and CLI compatibility
app = App(
    name="agentom",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
