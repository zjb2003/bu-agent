from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from bu_agent.api.schemas import ChatRequest, ChatResponse
from bu_agent.api.sse import event

router = APIRouter()


def _metadata(request: Request, result) -> dict | None:
    if not request.app.state.settings.expose_debug_metadata:
        return None
    return {"skill_used": result.route.in_scope, "task_mode": result.route.task_mode, "risk": result.safety.risk, "evidence": result.evidence, "references_loaded": result.references_loaded}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    request.app.state.loader.validate()
    return {"status": "ready"}


@router.post("/v1/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    session_id = payload.session_id or str(uuid.uuid4())
    result = await request.app.state.agent.chat(session_id, payload.message, payload.capabilities)
    return ChatResponse(session_id=session_id, answer=result.answer, metadata=_metadata(request, result))


@router.post("/v1/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    session_id = payload.session_id or str(uuid.uuid4())

    async def generate():
        yield event("session", {"session_id": session_id})
        try:
            async for kind, value in request.app.state.agent.stream_chat(session_id, payload.message, payload.capabilities):
                if kind == "delta":
                    yield event("delta", {"text": value})
                else:
                    yield event("done", {"metadata": _metadata(request, value)})
        except Exception:  # noqa: BLE001 - SSE must convert provider failures into a safe event.
            yield event("error", {"code": "generation_failed", "message": "生成失败，请稍后重试。"})

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@router.delete("/v1/sessions/{session_id}")
async def delete_session(session_id: str, request: Request) -> dict[str, object]:
    return {"deleted": await request.app.state.store.delete(session_id)}

