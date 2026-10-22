from typing import Protocol

from bu_agent.domain.models import EvidenceResult


class KnowledgeProvider(Protocol):
    async def search(self, query: str) -> EvidenceResult: ...

