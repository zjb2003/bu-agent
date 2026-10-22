import logging

import pytest

from bu_agent.runtime.safety_gate import SafetyGate


@pytest.mark.asyncio
async def test_pii_types_only(caplog):
    text = "学生电话是13800138000，邮箱kid@example.com"
    result = await SafetyGate().assess(text)
    logging.getLogger("test").info("safety=%s reasons=%s", result.risk, result.reasons)
    assert result.privacy_detected and result.action == "redact_first"
    assert text not in caplog.text and "13800138000" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["孩子说想自杀", "学生可能遭到侵害", "孩子走失了"])
async def test_high_risk_first(text):
    result = await SafetyGate().assess(text)
    assert result.risk == "high" and result.action == "handoff"

