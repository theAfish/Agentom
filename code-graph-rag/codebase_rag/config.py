from __future__ import annotations

from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find the .env file in the project root
# config.py path: /workspace/packages/agent-server/code-graph-rag/codebase_rag/config.py
# .env path: /workspace/config/.env
# So we need to go up 5 levels from config.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / "config" / ".env"

load_dotenv(ENV_FILE)


class AppConfig(BaseSettings):
    """
    Application Configuration using Pydantic for robust validation and type-safety.
    All settings are loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    MEMGRAPH_HOST: str = "localhost"
    MEMGRAPH_PORT: int = 7687
    MEMGRAPH_HTTP_PORT: int = 7444
    LAB_PORT: int = 3000

    LLM_PROVIDER: Literal["gemini", "local", "deepseek", "openai"] = "openai"
    GEMINI_PROVIDER: Literal["gla", "vertex"] = "gla"

    GEMINI_MODEL_ID: str = "gemini-2.5-pro"  # DO NOT CHANGE THIS
    GEMINI_VISION_MODEL_ID: str = "gemini-2.5-flash"  # DO NOT CHANGE THIS
    MODEL_CYPHER_ID: str = "gemini-2.5-flash-lite-preview-06-17"  # DO NOT CHANGE THIS
    GEMINI_API_KEY: str | None = None
    GEMINI_THINKING_BUDGET: int | None = None

    GCP_PROJECT_ID: str | None = None
    GCP_REGION: str = "us-central1"
    GCP_SERVICE_ACCOUNT_FILE: str | None = None

    DEEPSEEK_MODEL_ID: str = "deepseek-chat"
    DEEPSEEK_API_KEY: str | None = None

    LOCAL_MODEL_ENDPOINT: AnyHttpUrl = AnyHttpUrl("http://localhost:11434/v1")
    LOCAL_ORCHESTRATOR_MODEL_ID: str = "llama3"
    LOCAL_CYPHER_MODEL_ID: str = "llama3"
    LOCAL_MODEL_API_KEY: str = "ollama"

    TARGET_REPO_PATH: str | None = None
    SHELL_COMMAND_TIMEOUT: int = 30

    MP_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str | None = None

    @model_validator(mode="after")
    def check_required_fields(self) -> AppConfig:
        """Validate that required API keys and project IDs are set based on the provider."""
        print("LLM_PROVIDER =", self.LLM_PROVIDER, "GEMINI_PROVIDER =", self.GEMINI_PROVIDER)
        if self.LLM_PROVIDER == "gemini":
            if self.GEMINI_PROVIDER == "gla" and not self.GEMINI_API_KEY:
                raise ValueError(
                    "Configuration Error: GEMINI_API_KEY is required when GEMINI_PROVIDER is 'gla'."
                )
            if self.GEMINI_PROVIDER == "vertex" and not self.GCP_PROJECT_ID:
                raise ValueError(
                    "Configuration Error: GCP_PROJECT_ID is required when GEMINI_PROVIDER is 'vertex'."
                )
        if self.LLM_PROVIDER == "deepseek" and not self.DEEPSEEK_API_KEY:
            raise ValueError(
                "Configuration Error: DEEPSEEK_API_KEY is required when LLM_PROVIDER is 'deepseek'."
            )
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError(
                "Configuration Error: OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'."
            )
        return self


settings = AppConfig()
