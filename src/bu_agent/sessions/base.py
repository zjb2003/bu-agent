from typing import Protocol

from bu_agent.domain.models import Message


class ConversationStore(Protocol):
    async def get(self, session_id: str) -> list[Message]: ...
    async def append(self, session_id: str, messages: list[Message]) -> None: ...
    async def delete(self, session_id: str) -> bool: ...

