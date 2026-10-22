from typing import Any

from pydantic import BaseModel, Field

from bu_agent.domain.models import RuntimeCapabilities


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=128)
    message: str = Field(min_length=1, max_length=20000)
    capabilities: RuntimeCapabilities = Field(default_factory=RuntimeCapabilities)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    metadata: dict[str, Any] | None = None

