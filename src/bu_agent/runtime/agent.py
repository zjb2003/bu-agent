from __future__ import annotations

from bu_agent.domain.models import AgentResult, Message, RuntimeCapabilities
from bu_agent.providers.llm import LLMProvider
from bu_agent.runtime.evidence_router import EvidenceRouter
from bu_agent.runtime.output_validator import OutputValidator
from bu_agent.runtime.prompt_builder import PromptBuilder
from bu_agent.runtime.safety_gate import SafetyGate
from bu_agent.runtime.scope_router import ScopeRouter
from bu_agent.security.pii import detect_pii
from bu_agent.sessions.base import ConversationStore
from bu_agent.skills.loader import SkillLoader


class BUAgent:
    def __init__(self, *, llm: LLMProvider, loader: SkillLoader, store: ConversationStore, evidence_router: EvidenceRouter, scope_router: ScopeRouter | None = None):
        self.llm, self.loader, self.store = llm, loader, store
        self.evidence_router = evidence_router
        self.scope_router = scope_router or ScopeRouter()
        self.safety_gate, self.prompt_builder, self.validator = SafetyGate(), PromptBuilder(), OutputValidator()

    async def chat(self, session_id: str, message: str, capabilities: RuntimeCapabilities) -> AgentResult:
        safety = await self.safety_gate.assess(message)
        route = await self.scope_router.route(message)
        if safety.risk == "high" or safety.privacy_detected:
            route.in_scope, route.task_mode = True, "child_safety"
            route.reference_keys = ["child_safety", "routing", "runtime"]
        if not route.in_scope:
            answer = "我主要支持 BoundlessUs、支教、公益教育、志愿服务及相关安全与资源任务。你可以问我备课、课堂活动、复盘或合作边界。"
            return AgentResult(answer=answer, route=route, safety=safety, evidence="unavailable", references_loaded=[])
        skill = self.loader.load(route.reference_keys)
        evidence = await self.evidence_router.resolve(message, capabilities)
        history = await self.store.get(session_id)
        request = self.prompt_builder.build(skill=skill, route=route, safety=safety, evidence=evidence, capabilities=capabilities, history=history, user_message=message)
        result = await self.llm.complete(request)
        check = self.validator.validate(result.text, safety=safety, evidence=evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
        answer = result.text
        if not check.valid:
            retry = self.prompt_builder.build(skill=skill, route=route, safety=safety, evidence=evidence, capabilities=capabilities, history=history, user_message=message, correction="上次输出未通过检查：" + ",".join(check.codes) + "。请修正且不要复述敏感输入。")
            second = await self.llm.complete(retry)
            check2 = self.validator.validate(second.text, safety=safety, evidence=evidence.state, capabilities=capabilities, input_pii=detect_pii(message))
            answer = second.text if check2.valid else self._fallback(safety)
        await self.store.append(session_id, [Message(role="user", content=message), Message(role="assistant", content=answer)])
        return AgentResult(answer=answer, route=route, safety=safety, evidence=evidence.state, references_loaded=list(skill.references), usage=result.usage)

    @staticmethod
    def _fallback(safety) -> str:
        if safety.risk == "high":
            return "请先确保当事人处于安全环境，并立即联系现场老师、项目负责人或监护人；如有迫切危险，请联系当地警方或急救。不要公开或继续转发个人信息。"
        return "当前无法安全生成完整回答。请先删除可识别个人信息，并由项目负责人确认事实与授权后再继续。"

