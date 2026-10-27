import pytest
from httpx import ASGITransport, AsyncClient

from bu_agent.main import create_app


@pytest.mark.asyncio
async def test_stream_events(settings, fake_llm):
    app = create_app(settings, llm=fake_llm)
    async with app.router.lifespan_context(app), AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/v1/chat/stream", json={"message": "如何准备支教课程"})
        assert response.status_code == 200
        assert "event: session" in response.text
        assert "event: delta" in response.text
        assert "event: done" in response.text


@pytest.mark.asyncio
async def test_stream_replaces_answer_when_final_validation_fails(settings):
    from bu_agent.providers.fake_llm import FakeLLMProvider

    llm = FakeLLMProvider(["我已联系项目方。", "这是参考课程方案，请先确认年级。"])
    app = create_app(settings, llm=llm)
    async with app.router.lifespan_context(app), AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/v1/chat/stream", json={"message": "如何准备支教课程"})
        assert response.status_code == 200
        assert "event: replace" in response.text
        assert "event: done" in response.text
        assert "event: error" not in response.text

