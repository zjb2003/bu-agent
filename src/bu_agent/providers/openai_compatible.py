from __future__ import annotations

from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from bu_agent.domain.errors import ProviderCompatibilityError
from bu_agent.domain.models import LLMEvent, LLMRequest, LLMResult, TokenUsage


class OpenAICompatibleProvider:
    def __init__(self, *, api_key: str, base_url: str, model: str, api_mode: str, timeout: float, max_retries: int):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=max_retries)
        self.model, self.api_mode = model, api_mode

    async def complete(self, request: LLMRequest) -> LLMResult:
        messages = [m.model_dump() for m in request.messages]
        try:
            if self.api_mode == "chat_completions":
                response = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=request.temperature)
                usage = response.usage
                return LLMResult(text=response.choices[0].message.content or "", usage=TokenUsage(input_tokens=getattr(usage, "prompt_tokens", None), output_tokens=getattr(usage, "completion_tokens", None)))
            response = await self.client.responses.create(model=self.model, input=messages, temperature=request.temperature)
            return LLMResult(text=response.output_text)
        except Exception as exc:
            if self.api_mode == "responses":
                raise ProviderCompatibilityError("Responses API failed; verify provider support or set API_MODE=chat_completions") from exc
            raise

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        messages = [m.model_dump() for m in request.messages]
        if self.api_mode == "chat_completions":
            stream = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=request.temperature, stream=True)
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield LLMEvent(delta=delta)
            return
        try:
            async with self.client.responses.stream(model=self.model, input=messages, temperature=request.temperature) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta":
                        yield LLMEvent(delta=event.delta)
        except Exception as exc:
            raise ProviderCompatibilityError("Responses streaming failed; set API_MODE=chat_completions if unsupported") from exc

