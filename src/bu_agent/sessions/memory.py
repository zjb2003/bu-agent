from __future__ import annotations

import asyncio
import time
from collections import OrderedDict

from bu_agent.domain.models import Message


class MemoryConversationStore:
    def __init__(self, ttl_seconds: int = 3600, max_sessions: int = 1000, max_turns: int = 10):
        self.ttl, self.max_sessions, self.max_messages = ttl_seconds, max_sessions, max_turns * 2
        self._items: OrderedDict[str, tuple[float, list[Message]]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, session_id: str) -> list[Message]:
        async with self._lock:
            item = self._items.get(session_id)
            if not item or item[0] <= time.monotonic():
                self._items.pop(session_id, None)
                return []
            self._items.move_to_end(session_id)
            return list(item[1])

    async def append(self, session_id: str, messages: list[Message]) -> None:
        async with self._lock:
            previous = self._items.get(session_id, (0, []))[1]
            self._items[session_id] = (time.monotonic() + self.ttl, (previous + messages)[-self.max_messages :])
            self._items.move_to_end(session_id)
            while len(self._items) > self.max_sessions:
                self._items.popitem(last=False)

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            return self._items.pop(session_id, None) is not None

