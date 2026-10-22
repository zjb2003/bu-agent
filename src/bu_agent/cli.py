from __future__ import annotations

import argparse
import asyncio
import json

from bu_agent.config import Settings
from bu_agent.domain.models import RuntimeCapabilities
from bu_agent.main import create_app
from bu_agent.skills.loader import SkillLoader


def _dry_run(settings: Settings) -> int:
    path = settings.skill_path / "evals" / "cases.jsonl"
    if not path.exists():
        print("No evals/cases.jsonl found; structural dry-run skipped.")
        return 0
    count = 0
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError(f"case line {number} must be an object")
            count += 1
    print(f"Validated {count} eval case objects. This is structural dry-run only, not model evaluation.")
    return 0


async def _chat(settings: Settings) -> None:
    app = create_app(settings)
    agent = app.state.agent
    session = "cli"
    print("BU 小助手 CLI；输入 exit 退出。")
    while True:
        message = input("> ").strip()
        if message.lower() in {"exit", "quit"}:
            break
        result = await agent.chat(session, message, RuntimeCapabilities())
        print(result.answer)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("chat")
    sub.add_parser("check-skill")
    ev = sub.add_parser("eval")
    ev.add_argument("--dry-run", action="store_true", required=True)
    args = parser.parse_args()
    settings = Settings()
    if args.command == "check-skill":
        SkillLoader(settings.skill_path).validate()
        print("Skill installation is valid.")
    elif args.command == "eval":
        _dry_run(settings)
    else:
        asyncio.run(_chat(settings))


if __name__ == "__main__":
    main()

