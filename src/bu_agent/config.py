from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    api_mode: Literal["chat_completions", "responses"] = "chat_completions"
    skill_path: Path = Path("./skills/boundlessus-bu-assistant")
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    request_timeout_seconds: float = 60
    max_retries: int = 2
    max_history_turns: int = 10
    session_ttl_seconds: int = 3600
    max_sessions: int = 1000
    expose_debug_metadata: bool = False
    local_knowledge_path: Path | None = None

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        return value.rstrip("/")

    def validate_provider(self) -> None:
        missing = [name for name in ("base_url", "api_key", "model") if not getattr(self, name)]
        if missing:
            raise ValueError("Missing required provider settings: " + ", ".join(missing))

