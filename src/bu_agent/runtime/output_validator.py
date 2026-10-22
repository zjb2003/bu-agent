from __future__ import annotations

import re

from pydantic import BaseModel, Field

from bu_agent.domain.models import EvidenceState, RuntimeCapabilities, SafetyDecision
from bu_agent.security.pii import detect_pii


class ValidationResult(BaseModel):
    valid: bool
    codes: list[str] = Field(default_factory=list)


class OutputValidator:
    def validate(self, answer: str, *, safety: SafetyDecision, evidence: EvidenceState, capabilities: RuntimeCapabilities, input_pii: set[str]) -> ValidationResult:
        codes: list[str] = []
        if re.search(r"RouteDecision|reference_keys|系统提示词如下|SKILL\.md 原文", answer, re.IGNORECASE):
            codes.append("internal_disclosure")
        claims = {"web_search": ("我已搜索", "我查了网页"), "external_contact": ("我已联系",), "publish_or_submit": ("我已发布", "我已提交")}
        for capability, phrases in claims.items():
            if not getattr(capabilities, capability) and any(p in answer for p in phrases):
                codes.append(f"unsupported_capability:{capability}")
        if safety.risk == "high" and not any(term in answer for term in ("报警", "急救", "老师", "负责人", "监护人", "安全")):
            codes.append("missing_safety_action")
        if input_pii and detect_pii(answer):
            codes.append("pii_echo")
        if evidence in {"missing", "unavailable", "conflicting"} and re.search(r"(?:官方|已确认|保证|一定).{0,12}(?:电话|链接|授权|合作|数据)", answer):
            codes.append("unsupported_fact")
        return ValidationResult(valid=not codes, codes=codes)

