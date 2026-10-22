import pytest

from bu_agent.runtime.scope_router import ScopeRouter


@pytest.mark.asyncio
async def test_course_triggers_skill():
    result = await ScopeRouter().route("我第一次去小学支教，怎样准备一节课？")
    assert result.in_scope and result.task_mode == "course"


@pytest.mark.asyncio
async def test_classroom_without_bu_triggers():
    result = await ScopeRouter().route("课堂突然冷场怎么办")
    assert result.in_scope and result.task_mode == "course"


@pytest.mark.asyncio
async def test_unrelated_is_not_forced():
    result = await ScopeRouter().route("帮我写一个股票交易程序")
    assert not result.in_scope and result.task_mode == "unrelated"

