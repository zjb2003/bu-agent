import asyncio

import pytest

from bu_agent.domain.models import Message
from bu_agent.sessions.memory import MemoryConversationStore


@pytest.mark.asyncio
async def test_delete_and_ttl():
    store = MemoryConversationStore(ttl_seconds=0.01)
    await store.append("one", [Message(role="user", content="x")])
    assert await store.delete("one")
    assert await store.get("one") == []
    await store.append("two", [Message(role="user", content="x")])
    await asyncio.sleep(0.02)
    assert await store.get("two") == []

