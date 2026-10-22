import json

import pytest

from bu_agent.providers.local_records import LocalRecordProvider


@pytest.mark.asyncio
async def test_conflicting_records_stay_conflicting(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text(json.dumps({"id": "1", "text": "项目 日期", "status": "conflicting", "sensitivity": "public", "source_label": "test"}, ensure_ascii=False), encoding="utf-8")
    result = await LocalRecordProvider(path).search("项目 日期")
    assert result.state == "conflicting"

