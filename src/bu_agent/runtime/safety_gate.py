from __future__ import annotations

from bu_agent.domain.models import SafetyDecision
from bu_agent.security.pii import detect_pii

HIGH = ("自杀", "自伤", "杀了", "正在被打", "性侵", "侵害", "走失", "失踪", "突发疾病", "昏迷", "严重欺凌", "不敢回家")
MEDIUM = ("照片", "视频", "书信", "反馈", "公开", "发布", "联系方式", "加微信", "授权")


class SafetyGate:
    async def assess(self, text: str) -> SafetyDecision:
        pii = detect_pii(text)
        reasons: list[str] = []
        if any(term in text for term in HIGH):
            reasons.append("immediate_or_child_safety_risk")
            if pii:
                reasons.extend(f"pii:{kind}" for kind in sorted(pii))
            return SafetyDecision(risk="high", action="handoff", privacy_detected=bool(pii), reasons=reasons)
        if pii:
            reasons.extend(f"pii:{kind}" for kind in sorted(pii))
            return SafetyDecision(risk="medium", action="redact_first", privacy_detected=True, reasons=reasons)
        if any(term in text for term in MEDIUM):
            return SafetyDecision(risk="medium", action="answer_with_boundary", reasons=["privacy_or_authorization_context"])
        return SafetyDecision(risk="low", action="answer")

