from bu_agent.domain.models import EvidenceResult, RuntimeCapabilities
from bu_agent.providers.knowledge import KnowledgeProvider


class EvidenceRouter:
    def __init__(self, provider: KnowledgeProvider):
        self.provider = provider

    async def resolve(self, query: str, capabilities: RuntimeCapabilities) -> EvidenceResult:
        if not capabilities.knowledge_retrieval:
            return EvidenceResult(state="unavailable")
        return await self.provider.search(query)

