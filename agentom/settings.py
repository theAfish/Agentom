from pydantic import BaseModel, ConfigDict
from pathlib import Path
from typing import Optional
import os
import json
from datetime import datetime

# Config file path
ROOT_DIR = Path(__file__).resolve().parents[3]
CONFIG_FILE = ROOT_DIR / "config" / "config.json"

class Settings(BaseModel):
    model_config = ConfigDict(extra='ignore')

    # App Info
    APP_NAME: str = "agentom"
    USER_ID: str = "materials_scientist"
    SESSION_ID: str = "session_001"
    
    # Paths
    # Default to the parent directory of this file (agentom package root)
    BASE_DIR: Path = Path(__file__).resolve().parent
    
    # Default WORKSPACE_ROOT, can be overridden by config
    WORKSPACE_ROOT: Path = BASE_DIR / "workspace"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    
    # Model Configuration
    AGENTOM_MODEL: str = "openai/qwen3-max"
    VISION_MODEL: str = "openai/qwen3-omni-flash"
    WIKI_MODEL: str = "openai/qwen3-max"
    STRUCTURE_MODEL: str = "openai/qwen3-max"
    MP_MODEL: str = "openai/qwen-turbo"

    # A2A server configuration
    A2A_PROTOCOL: str = "http"
    A2A_HOST: str = "localhost"
    A2A_PORT: int = 8001

    # Output archive directory for preserving outputs
    OUTPUT_ARCHIVE_DIR: Optional[Path] = Path("outputs_archive")

    current_session_folder: Optional[str] = None

    def __init__(self, **data):
        # Load from config file if it exists
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
            # Convert WORKSPACE_ROOT to Path if present
            if 'WORKSPACE_ROOT' in config_data:
                wd = Path(config_data['WORKSPACE_ROOT'])
                if not wd.is_absolute():
                    wd = ROOT_DIR / wd
                config_data['WORKSPACE_ROOT'] = wd
            # Convert OUTPUT_ARCHIVE_DIR to Path if present
            if 'OUTPUT_ARCHIVE_DIR' in config_data:
                od = Path(config_data['OUTPUT_ARCHIVE_DIR'])
                if not od.is_absolute():
                    od = ROOT_DIR / od
                config_data['OUTPUT_ARCHIVE_DIR'] = od
            # Update data with config
            data.update(config_data)
        super().__init__(**data)
        self._session_workspaces = {}
        self._current_session = None

    @property
    def WORKSPACE_DIR(self) -> Path:
        if self._current_session and self._current_session in self._session_workspaces:
            return self._session_workspaces[self._current_session]
        # Default to base workspace
        return self.WORKSPACE_ROOT / "default_workspace"

    def set_session_workspace(self, session_id: str):
        if session_id not in self._session_workspaces:
            # Check for existing folder
            existing = None
            workspace_root = self.WORKSPACE_ROOT
            for item in workspace_root.iterdir():
                if item.is_dir() and session_id in item.name:
                    existing = item
                    break
            if existing:
                self._session_workspaces[session_id] = existing
            else:
                dt = datetime.now()
                session_folder = f"{dt.strftime('%Y%m%d_%H%M%S')}-{session_id}"
                self.current_session_folder = session_folder
                self._session_workspaces[session_id] = workspace_root / session_folder
        self._current_session = session_id
        # Ensure directories exist
        self.ensure_directories()

    @property
    def LOGS_DIR(self) -> Path:
        return self.WORKSPACE_ROOT / "logs"

    @property
    def OUTPUT_DIR(self) -> Path:
        return self.WORKSPACE_DIR / "outputs"

    @property
    def TEMP_DIR(self) -> Path:
        return self.WORKSPACE_DIR / "tmp"

    @property
    def INPUT_DIR(self) -> Path:
        return self.WORKSPACE_DIR / "inputs"

    def ensure_directories(self):
        """Ensure all necessary directories exist."""
        for dir_path in [self.WORKSPACE_DIR, self.OUTPUT_DIR, self.TEMP_DIR, self.INPUT_DIR, self.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

settings = Settings()

