import pytest

from bu_agent.domain.models import RuntimeCapabilities
from bu_agent.providers.fake_llm import FakeLLMProvider
from bu_agent.providers.null_knowledge import NullKnowledgeProvider
from bu_agent.runtime.agent import BUAgent
from bu_agent.runtime.evidence_router import EvidenceRouter
from bu_agent.sessions.memory import MemoryConversationStore
from bu_agent.skills.loader import SkillLoader


@pytest.mark.asyncio
async def test_validator_rewrites_only_once(skill_path):
    llm = FakeLLMProvider(["我已联系项目方。", "我已联系项目方并提交。"])
    agent = BUAgent(llm=llm, loader=SkillLoader(skill_path), store=MemoryConversationStore(), evidence_router=EvidenceRouter(NullKnowledgeProvider()))
    result = await agent.chat("s", "帮我写支教合作文案", RuntimeCapabilities())
    assert llm.calls == 2
    assert "无法安全生成" in result.answer
    assert result.evidence == "unavailable"

