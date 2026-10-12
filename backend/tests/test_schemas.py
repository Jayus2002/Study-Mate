from backend.app.schemas import PlanRequest, StudyPlan
import pytest
from pydantic import ValidationError
def make_day(day: int):
    return {
        "day": day,
        "topic": f"Topic {day}",
        "tasks": ["阅读资料", "完成目标"],
        "expected_output": f"完成第 {day} 天的学习计划",
    }

def test_valid_plan():
    request = PlanRequest(
        goal="学习 Python",
        duration_days=3,
        daily_minutes=60,
        background="了解变量",
    )
    plan = StudyPlan(
        title="Python 学习计划",
        summary="为期 3 天的 Python 学习计划",
        days=[make_day(i) for i in range(1, 4)],
    )
    assert request.duration_days == 3
    assert len(plan.days) == 3
    assert plan.days[0].topic == "Topic 1"

@pytest.mark.parametrize(
    "payload",
    [
        {"goal":"", "duration_days":3, "daily_minutes":60},
        {"goal":"  ", "duration_days":3, "daily_minutes":60},
        {"goal": "Python", "duration_days": 0, "daily_minutes": 60},
        {"goal": "Python", "duration_days": 31, "daily_minutes": 60},
        {"goal": "Python", "duration_days": 3, "daily_minutes": 14},
        {"goal": "Python", "duration_days": 3, "daily_minutes": 721},
    ],
)
def test_invalid_plan_request(payload):
    with pytest.raises(ValidationError):
        PlanRequest(**payload)

@pytest.mark.parametrize(
    "plan",
    [
        {
            "title": "Python 学习计划",
            "summary": "为期 3 天的 Python 学习计划",
            "days": [make_day(1), make_day(3)],
        },
        {
            "title": "Python 学习计划",
            "summary": "为期 3 天的 Python 学习计划",
            "days": [make_day(1), make_day(2), make_day(4), make_day(5)],
        },
        {
            "title":"",
            "summary":"",
            "days":"",
        }
    ],
)
def test_invalid_study_plan(plan):
    with pytest.raises(ValidationError):
        StudyPlan(**plan)