from __future__ import annotations

from collections.abc import AsyncIterator

from bu_agent.domain.models import LLMEvent, LLMRequest, LLMResult


class FakeLLMProvider:
    def __init__(self, responses: list[str] | None = None):
        self.responses = responses or ["这是离线测试回答。"]
        self.requests: list[LLMRequest] = []
        self.calls = 0

    async def complete(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        answer = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return LLMResult(text=answer)

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        result = await self.complete(request)
        for char in result.text:
            yield LLMEvent(delta=char)

