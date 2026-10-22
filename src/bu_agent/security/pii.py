from __future__ import annotations

import re

PATTERNS = {
    "phone": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "id_number": re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"),
}


def detect_pii(text: str) -> set[str]:
    """Return PII types only; never return matched values."""
    found = {name for name, pattern in PATTERNS.items() if pattern.search(text)}
    if re.search(r"(?:学校|小学|中学|班级).{0,10}(?:姓名|叫|同学)", text):
        found.add("child_identity_context")
    return found


def redact_pii(text: str) -> str:
    for kind, pattern in PATTERNS.items():
        text = pattern.sub(f"[已隐藏{kind}]", text)
    return text

