"""
Configuration constants for the agentom package.
"""
from pathlib import Path

# Base directory of the agentom package
BASE_DIR = Path(__file__).resolve().parent

# Environment file
ENV_PATH = BASE_DIR / ".env"

# Workspace directories
WORKSPACE_DIR = BASE_DIR / "workspace"
OUTPUT_DIR = WORKSPACE_DIR / "outputs"
TEMP_DIR = WORKSPACE_DIR / "tmp"
INPUT_DIR = WORKSPACE_DIR / "inputs"
LOGS_DIR = WORKSPACE_DIR / "logs"

# Ensure directories exist
for dir_path in [WORKSPACE_DIR, OUTPUT_DIR, TEMP_DIR, INPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)