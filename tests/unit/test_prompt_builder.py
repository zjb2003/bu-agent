from bu_agent.domain.models import (
    EvidenceResult,
    Message,
    RouteDecision,
    RuntimeCapabilities,
    SafetyDecision,
)
from bu_agent.runtime.prompt_builder import PromptBuilder
from bu_agent.skills.models import LoadedSkill


def test_capabilities_and_untrusted_evidence_are_explicit():
    request = PromptBuilder().build(skill=LoadedSkill(instructions="RULE", references={"x.md": "REF"}), route=RouteDecision(in_scope=True, task_mode="course", confidence=1), safety=SafetyDecision(risk="low", action="answer"), evidence=EvidenceResult(state="unavailable"), capabilities=RuntimeCapabilities(), history=[Message(role="user", content="旧消息")], user_message="新消息")
    system = request.messages[0].content
    assert "完整 SKILL.md" in system and "非可信证据数据" in system
    assert '"web_search":false' in system

