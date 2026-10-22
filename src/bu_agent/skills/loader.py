from __future__ import annotations

from pathlib import Path

from bu_agent.domain.errors import SkillConfigurationError
from bu_agent.security.path_guard import safe_child
from bu_agent.skills.models import LoadedSkill
from bu_agent.skills.registry import REFERENCE_MAP


class SkillLoader:
    """Read the authoritative Skill and whitelisted references with mtime caching."""

    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[Path, tuple[int, str]] = {}

    def _read(self, relative: str) -> str:
        path = safe_child(self.root, relative)
        stamp = path.stat().st_mtime_ns
        cached = self._cache.get(path)
        if cached and cached[0] == stamp:
            return cached[1]
        text = path.read_text(encoding="utf-8")
        self._cache[path] = (stamp, text)
        return text

    def validate(self) -> None:
        self._read("SKILL.md")
        required = {name for values in REFERENCE_MAP.values() for name in values}
        for name in sorted(required):
            self._read(f"references/{name}")

    def load(self, keys: list[str]) -> LoadedSkill:
        names: list[str] = []
        for key in keys:
            if key not in REFERENCE_MAP:
                raise SkillConfigurationError(f"Unknown reference key: {key}")
            names.extend(REFERENCE_MAP[key])
        unique = list(dict.fromkeys(names))
        return LoadedSkill(
            instructions=self._read("SKILL.md"),
            references={name: self._read(f"references/{name}") for name in unique},
        )

