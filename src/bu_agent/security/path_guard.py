from __future__ import annotations

from pathlib import Path

from bu_agent.domain.errors import SkillConfigurationError


def safe_child(root: Path, relative: str) -> Path:
    """Resolve a regular file strictly below root, rejecting traversal/symlinks."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SkillConfigurationError(f"Unsafe skill path: {relative}")
    root_resolved = root.resolve(strict=True)
    candidate = root_resolved.joinpath(rel)
    if candidate.is_symlink():
        raise SkillConfigurationError(f"Symlinks are not allowed: {relative}")
    resolved = candidate.resolve(strict=True)
    if root_resolved not in resolved.parents:
        raise SkillConfigurationError(f"Path escapes skill root: {relative}")
    if not resolved.is_file():
        raise SkillConfigurationError(f"Required skill file is not a file: {relative}")
    return resolved

