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


@pytest.mark.asyncio
async def test_colloquial_child_sport_triggers_course_skill():
    result = await ScopeRouter().route("我想要教小朋友们打篮球")
    assert result.in_scope and result.task_mode == "course" and "course" in result.reference_keys


@pytest.mark.asyncio
async def test_assistant_capabilities_trigger_project_skill():
    result = await ScopeRouter().route("你会什么？")
    assert result.in_scope and result.task_mode == "project_info"


@pytest.mark.asyncio
async def test_follow_up_keeps_previous_task_mode():
    from bu_agent.domain.models import Message

    history = [Message(role="user", content="帮我设计一节课"), Message(role="assistant", content="先确认年级。")]
    result = await ScopeRouter().route("那第一步呢？", history)
    assert result.in_scope and result.task_mode == "course"

