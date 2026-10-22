from __future__ import annotations

import json
from pathlib import Path

from bu_agent.domain.models import EvidenceResult, KnowledgeRecord


class LocalRecordProvider:
    def __init__(self, path: Path):
        self.path = path

    async def search(self, query: str) -> EvidenceResult:
        records = [KnowledgeRecord.model_validate(json.loads(line)) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        safe = [r for r in records if r.sensitivity == "public" and r.status not in {"internal", "unknown"} and any(token in r.text for token in query.split() if len(token) > 1)]
        if not safe:
            return EvidenceResult(state="missing")
        if any(r.status == "conflicting" for r in safe):
            return EvidenceResult(state="conflicting", records=safe)
        if any(r.status == "draft" for r in safe):
            return EvidenceResult(state="draft_internal", records=safe)
        return EvidenceResult(state="confirmed", records=safe)

