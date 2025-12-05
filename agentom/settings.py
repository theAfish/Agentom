from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # App Info
    APP_NAME: str = "agentom"
    USER_ID: str = "materials_scientist"
    SESSION_ID: str = "session_001"
    
    # Paths
    # Default to the parent directory of this file (agentom package root)
    BASE_DIR: Path = Path(__file__).resolve().parent
    
    # Allow overriding WORKSPACE_DIR via env var, default to BASE_DIR/workspace
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
