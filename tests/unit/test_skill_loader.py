import pytest

from bu_agent.domain.errors import SkillConfigurationError
from bu_agent.security.path_guard import safe_child
from bu_agent.skills.loader import SkillLoader


def test_loads_only_course_references(skill_path):
    loaded = SkillLoader(skill_path).load(["course"])
    assert "phase2-course-design-and-classroom.md" in loaded.references
    assert "phase2-recap-and-writing.md" not in loaded.references
    assert "BoundlessUs BU 小助手" in loaded.instructions


def test_path_traversal_rejected(skill_path):
    with pytest.raises(SkillConfigurationError):
        safe_child(skill_path, "../SKILL.md")


def test_validate_real_skill(skill_path):
    SkillLoader(skill_path).validate()

