from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

UserRole = Literal["visitor", "volunteer", "project_member", "contributor", "partner", "parent_teacher", "child", "casual", "abusive", "unknown"]
TaskMode = Literal["project_info", "resource", "course", "activity", "writing", "co_creation", "cooperation", "child_safety", "unrelated"]
EvidenceState = Literal["confirmed", "draft_internal", "missing", "conflicting", "unavailable"]


class RouteDecision(BaseModel):
    in_scope: bool
    user_role: UserRole = "unknown"
    task_mode: TaskMode = "unrelated"
    confidence: float = Field(ge=0, le=1)
    reference_keys: list[str] = Field(default_factory=list)


class SafetyDecision(BaseModel):
    risk: Literal["low", "medium", "high", "unknown"]
    action: Literal["answer", "answer_with_boundary", "redact_first", "refuse_and_redirect", "handoff"]
    privacy_detected: bool = False
    reasons: list[str] = Field(default_factory=list)


class RuntimeCapabilities(BaseModel):
    knowledge_retrieval: bool = False
    web_search: bool = False
    external_contact: bool = False
    publish_or_submit: bool = False


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class KnowledgeRecord(BaseModel):
    id: str
    text: str
    status: Literal["confirmed", "draft", "internal", "unknown", "conflicting"]
    sensitivity: Literal["public", "internal", "child_data", "unknown"] = "unknown"
    updated_at: datetime | None = None
    source_label: str


class EvidenceResult(BaseModel):
    state: EvidenceState
    records: list[KnowledgeRecord] = Field(default_factory=list)


class TokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMRequest(BaseModel):
    messages: list[Message]
    temperature: float = 0.2


class LLMResult(BaseModel):
    text: str
    usage: TokenUsage | None = None


class LLMEvent(BaseModel):
    delta: str = ""


class AgentResult(BaseModel):
    answer: str
    route: RouteDecision
    safety: SafetyDecision
    evidence: EvidenceState
    references_loaded: list[str]
    usage: TokenUsage | None = None

