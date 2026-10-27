from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from bu_agent.api.routes import router
from bu_agent.config import Settings
from bu_agent.logging_config import configure_logging
from bu_agent.providers.local_records import LocalRecordProvider
from bu_agent.providers.null_knowledge import NullKnowledgeProvider
from bu_agent.providers.openai_compatible import OpenAICompatibleProvider
from bu_agent.runtime.agent import BUAgent
from bu_agent.runtime.evidence_router import EvidenceRouter
from bu_agent.runtime.scope_router import ScopeRouter
from bu_agent.sessions.memory import MemoryConversationStore
from bu_agent.skills.loader import SkillLoader


def create_app(settings: Settings | None = None, *, llm=None, knowledge=None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.log_level)
    loader = SkillLoader(settings.skill_path)
    store = MemoryConversationStore(settings.session_ttl_seconds, settings.max_sessions, settings.max_history_turns)
    knowledge = knowledge or (LocalRecordProvider(settings.local_knowledge_path) if settings.local_knowledge_path else NullKnowledgeProvider())
    if llm is None:
        settings.validate_provider()
        llm = OpenAICompatibleProvider(api_key=settings.api_key, base_url=settings.base_url, model=settings.model, api_mode=settings.api_mode, timeout=settings.request_timeout_seconds, max_retries=settings.max_retries)
    agent = BUAgent(llm=llm, loader=loader, store=store, evidence_router=EvidenceRouter(knowledge), scope_router=ScopeRouter(classifier=llm))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        loader.validate()
        yield

    app = FastAPI(title="BoundlessUs BU Assistant", version="0.1.0", lifespan=lifespan)
    app.state.settings, app.state.loader, app.state.store, app.state.agent = settings, loader, store, agent
    app.include_router(router)
    return app



