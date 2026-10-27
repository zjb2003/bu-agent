from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from bu_agent.domain.models import (
    AgentResult,
    EvidenceResult,
    LLMRequest,
    Message,
    RouteDecision,
    RuntimeCapabilities,
    SafetyDecision,
)
from bu_agent.providers.llm import LLMProvider
from bu_agent.runtime.evidence_router import EvidenceRouter
from bu_agent.runtime.output_validator import OutputValidator
from bu_agent.runtime.prompt_builder import PromptBuilder
from bu_agent.runtime.safety_gate import SafetyGate
from bu_agent.runtime.scope_router import ScopeRouter
from bu_agent.security.pii import detect_pii
from bu_agent.sessions.base import ConversationStore
from bu_agent.skills.loader import SkillLoader
from bu_agent.skills.models import LoadedSkill


@dataclass
class PreparedTurn:
    route: RouteDecision
    safety: SafetyDecision
    evidence: EvidenceResult
    skill: LoadedSkill | None
    request: LLMRequest | None
    history: list[Message]
    fixed_answer: str | None = None


class BUAgent:
    def __init__(self, *, llm: LLMProvider, loader: SkillLoader, store: ConversationStore, evidence_router: EvidenceRouter, scope_router: ScopeRouter | None = None):
        self.llm, self.loader, self.store = llm, loader, store
        self.evidence_router = evidence_router
        self.scope_router = scope_router or ScopeRouter()
        self.safety_gate, self.prompt_builder, self.validator = SafetyGate(), PromptBuilder(), OutputValidator()

    async def _prepare(self, session_id: str, message: str, capabilities: RuntimeCapabilities) -> PreparedTurn:
        safety = await self.safety_gate.assess(message)
        history = await self.store.get(session_id)
        route = await self.scope_router.route(message, history)
        if safety.risk == "high" or safety.privacy_detected:
            route.in_scope, route.task_mode = True, "child_safety"
            route.reference_keys = ["child_safety", "routing", "runtime"]
        if not route.in_scope:
            return PreparedTurn(
                route=route,
                safety=safety,
                evidence=EvidenceResult(state="unavailable"),
                skill=None,
                request=None,
                history=history,
                fixed_answer="我主要支持 BoundlessUs、支教、公益教育、志愿服务及相关安全与资源任务。你可以问我备课、课堂活动、复盘或合作边界。",
            )
        skill = self.loader.load(route.reference_keys)
        evidence = await self.evidence_router.resolve(message, capabilities)
        request = self.prompt_builder.build(skill=skill, route=route, safety=safety, evidence=evidence, capabilities=capabilities, history=history, user_message=message)
        return PreparedTurn(route=route, safety=safety, evidence=evidence, skill=skill, request=request, history=history)

    def _result(self, prepared: PreparedTurn, answer: str, usage=None) -> AgentResult:
        return AgentResult(
            answer=answer,
            route=prepared.route,
            safety=prepared.safety,
            evidence=prepared.evidence.state,
            references_loaded=list(prepared.skill.references) if prepared.skill else [],
            usage=usage,
        )

    async def _complete_prepared(self, prepared: PreparedTurn, message: str, capabilities: RuntimeCapabilities) -> AgentResult:
        if prepared.fixed_answer is not None:
            return self._result(prepared, prepared.fixed_answer)
        assert prepared.request is not None and prepared.skill is not None
        result = await self.llm.complete(prepared.request)
        check = self.validator.validate(result.text, safety=prepared.safety, evidence=prepared.evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
        answer = result.text
        if not check.valid:
            retry = self.prompt_builder.build(skill=prepared.skill, route=prepared.route, safety=prepared.safety, evidence=prepared.evidence, capabilities=capabilities, history=prepared.history, user_message=message, correction="上次输出未通过检查：" + ",".join(check.codes) + "。请修正且不要复述敏感输入。")
            second = await self.llm.complete(retry)
            check2 = self.validator.validate(second.text, safety=prepared.safety, evidence=prepared.evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
            answer = second.text if check2.valid else self._fallback(prepared.safety)
        return self._result(prepared, answer, result.usage)

    async def chat(self, session_id: str, message: str, capabilities: RuntimeCapabilities) -> AgentResult:
        prepared = await self._prepare(session_id, message, capabilities)
        result = await self._complete_prepared(prepared, message, capabilities)
        if prepared.route.in_scope:
            await self.store.append(session_id, [Message(role="user", content=message), Message(role="assistant", content=result.answer)])
        return result

    async def stream_chat(self, session_id: str, message: str, capabilities: RuntimeCapabilities) -> AsyncIterator[tuple[str, str | AgentResult]]:
        """Stream low-risk model deltas; buffer risk/privacy turns until validation completes."""
        prepared = await self._prepare(session_id, message, capabilities)
        must_buffer = prepared.safety.risk != "low" or prepared.safety.action != "answer"
        if must_buffer or prepared.fixed_answer is not None:
            result = await self._complete_prepared(prepared, message, capabilities)
            for start in range(0, len(result.answer), 24):
                yield "delta", result.answer[start : start + 24]
            if prepared.route.in_scope:
                await self.store.append(session_id, [Message(role="user", content=message), Message(role="assistant", content=result.answer)])
            yield "done", result
            return

        assert prepared.request is not None
        parts: list[str] = []
        async for llm_event in self.llm.stream(prepared.request):
            if llm_event.delta:
                parts.append(llm_event.delta)
                yield "delta", llm_event.delta
        answer = "".join(parts)
        check = self.validator.validate(answer, safety=prepared.safety, evidence=prepared.evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
        if not check.valid:
            assert prepared.skill is not None
            retry = self.prompt_builder.build(skill=prepared.skill, route=prepared.route, safety=prepared.safety, evidence=prepared.evidence, capabilities=capabilities, history=prepared.history, user_message=message, correction="上次输出未通过检查：" + ",".join(check.codes) + "。请修正且不要复述敏感输入。")
            second = await self.llm.complete(retry)
            check2 = self.validator.validate(second.text, safety=prepared.safety, evidence=prepared.evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
            answer = second.text if check2.valid else self._fallback(prepared.safety)
            yield "replace", answer
        await self.store.append(session_id, [Message(role="user", content=message), Message(role="assistant", content=answer)])
        yield "done", self._result(prepared, answer)

    @staticmethod
    def _fallback(safety: SafetyDecision) -> str:
        if safety.risk == "high":
            return "请先确保当事人处于安全环境，并立即联系现场老师、项目负责人或监护人；如有迫切危险，请联系当地警方或急救。不要公开或继续转发个人信息。"
        return "当前无法安全生成完整回答。请先删除可识别个人信息，并由项目负责人确认事实与授权后再继续。"
