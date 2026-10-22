from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from bu_agent.domain.models import LLMEvent, LLMRequest, LLMResult


class LLMProvider(Protocol):
    async def complete(self, request: LLMRequest) -> LLMResult: ...
    def stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]: ...

