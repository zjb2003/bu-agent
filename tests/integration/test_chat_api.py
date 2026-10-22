import pytest
from httpx import ASGITransport, AsyncClient

from bu_agent.main import create_app


@pytest.mark.asyncio
async def test_chat_and_delete(settings, fake_llm):
    app = create_app(settings, llm=fake_llm)
    async with app.router.lifespan_context(app), AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/v1/chat", json={"session_id": "abc", "message": "课堂冷场怎么办"})
        assert response.status_code == 200
        body = response.json()
        assert body["metadata"]["skill_used"] is True
        assert body["metadata"]["evidence"] == "unavailable"
        deleted = await client.delete("/v1/sessions/abc")
        assert deleted.json()["deleted"] is True

