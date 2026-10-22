from bu_agent.domain.models import RuntimeCapabilities, SafetyDecision
from bu_agent.runtime.output_validator import OutputValidator


def test_rejects_unavailable_tool_claim():
    result = OutputValidator().validate("我已联系项目方并已提交。", safety=SafetyDecision(risk="low", action="answer"), evidence="unavailable", capabilities=RuntimeCapabilities(), input_pii=set())
    assert not result.valid
    assert any("unsupported_capability" in code for code in result.codes)


def test_high_risk_requires_action():
    result = OutputValidator().validate("我理解你的心情。", safety=SafetyDecision(risk="high", action="handoff"), evidence="unavailable", capabilities=RuntimeCapabilities(), input_pii=set())
    assert "missing_safety_action" in result.codes

