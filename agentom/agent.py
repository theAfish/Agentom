
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



agentom = AgentFactory.create_coordinator_agent()

# Create the app for web UI and CLI compatibility
app = App(
    name=settings.APP_NAME,
    root_agent=agentom,
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=[CustomLoggingPlugin()],
)


# # !!!!!!!!!!!!!!!!!!!!!!!!
# Now moved to services.py in middleware package, but left here commented

# # Ensure temporary files are cleaned up when the process exits or is interrupted

# def _cleanup_on_exit(signum=None, frame=None):
#     """Cleanup handler to remove temporary files on exit.

#     This will be registered with atexit and as a handler for common
#     termination signals so tmp files are removed after a user-initiated
#     exit (e.g. KeyboardInterrupt) or normal shutdown.
#     """
#     try:
#         transfer_outputs_to_target_dir(target_dir=target_dir)
#         clear_temp_dir()
#         clear_input_dir()
#         clear_workspace()
#         clear_output_dir()
#     except Exception:
#         # Avoid raising during shutdown — best-effort cleanup
#         pass


# # Register for normal interpreter exit
# atexit.register(_cleanup_on_exit)

# # Register for common termination signals (KeyboardInterrupt and termination)
# for _sig in (signal.SIGINT, signal.SIGTERM):
#     try:
#         signal.signal(_sig, _cleanup_on_exit)
#     except Exception:
#         # Some signal operations may not be supported on all platforms — ignore
#         pass

