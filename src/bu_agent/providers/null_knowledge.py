from bu_agent.domain.models import EvidenceResult


class NullKnowledgeProvider:
    async def search(self, query: str) -> EvidenceResult:
        return EvidenceResult(state="unavailable")

