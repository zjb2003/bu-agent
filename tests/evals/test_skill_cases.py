import json


def test_cases_are_structurally_loadable(skill_path):
    path = skill_path / "evals" / "cases.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert cases and all(isinstance(case, dict) for case in cases)

