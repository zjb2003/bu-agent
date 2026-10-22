from __future__ import annotations

from pathlib import Path

import pytest

from bu_agent.config import Settings
from bu_agent.providers.fake_llm import FakeLLMProvider


@pytest.fixture
def skill_path() -> Path:
    return Path(__file__).parents[1] / "skills" / "boundlessus-bu-assistant"


@pytest.fixture
def settings(skill_path: Path) -> Settings:
    return Settings(base_url="https://example.invalid/v1", api_key="test-placeholder", model="fake", skill_path=skill_path, expose_debug_metadata=True)


@pytest.fixture
def fake_llm() -> FakeLLMProvider:
    return FakeLLMProvider(["先确定课程目标，再准备低压力互动和备用活动；这是通用初稿，请按年级与时长调整。"])

