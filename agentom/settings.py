from pydantic import BaseModel, ConfigDict
from pathlib import Path
from typing import Optional
import os
import json

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
    
    # Default WORKSPACE_DIR, can be overridden by config
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    
    # Model Configuration
    AGENTOM_MODEL: str = "openai/qwen3-max"
    VISION_MODEL: str = "openai/qwen3-omni-flash"
    WIKI_MODEL: str = "openai/qwen3-max"
    STRUCTURE_MODEL: str = "openai/qwen3-max"
    MP_MODEL: str = "openai/qwen-turbo"

    # Output archive directory for preserving outputs
    OUTPUT_ARCHIVE_DIR: Optional[Path] = Path("outputs_archive")

    def __init__(self, **data):
        # Load from config file if it exists
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
            # Convert WORKSPACE_DIR to Path if present
            if 'WORKSPACE_DIR' in config_data:
                wd = Path(config_data['WORKSPACE_DIR'])
                if not wd.is_absolute():
                    wd = ROOT_DIR / wd
                config_data['WORKSPACE_DIR'] = wd
            # Convert OUTPUT_ARCHIVE_DIR to Path if present
            if 'OUTPUT_ARCHIVE_DIR' in config_data:
                od = Path(config_data['OUTPUT_ARCHIVE_DIR'])
                if not od.is_absolute():
                    od = ROOT_DIR / od
                config_data['OUTPUT_ARCHIVE_DIR'] = od
            # Update data with config
            data.update(config_data)
        super().__init__(**data)

    @property
    def LOGS_DIR(self) -> Path:
        return self.WORKSPACE_DIR / "logs"

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
settings.ensure_directories()
