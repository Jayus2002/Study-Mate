import json

from fastapi.testclient import TestClient
from types import SimpleNamespace

import pytest
from backend.app.schemas import PlanRequest
from backend.app.services.planner import (
    generate_plan,
    PlannerOutputError,
    PlannerTimeoutError,
)

def make_request():
    return PlanRequest(
        goal="学习 Python",
        duration_days=3,
        daily_minutes=60,
    )

def make_plan_json(days=3):
    return json.dumps({
        "title": "Python 计划",
        "summary": "三天计划",
        "days": [
            {
                "day": day,
                "topic": f"主题 {day}",
                "tasks": ["阅读资料", "完成练习"],
                "expected_output": f"完成第 {day} 天产出",
            }
            for day in range(1, days + 1)
        ],
    }, ensure_ascii=False)

class FakeCompletion:
    def __init__(self, content=None, error=None):
        self.content = content
        self.error = error
    def create(self, **kwargs):
        if self.error:
            raise self.error
        return SimpleNamespace(choices=
                               [SimpleNamespace(
                                   message=SimpleNamespace(content=self.content)
                                   )
                                ]
                            )

class FakeClient:
    def __init__(self, content=None, error=None):
        self.chat = SimpleNamespace(
            completions=FakeCompletion(
                content=content, 
                error=error,
            )
        )
def test_generate_plan_success(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    client = FakeClient(content=make_plan_json())
    plan = generate_plan(make_request(), client=client)
    assert plan.title == "Python 计划"
    assert len(plan.days) == 3
    assert [day.day for day in plan.days] == [1, 2, 3]

def test_invalid_json(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    client = FakeClient(content="{invalid")
    with pytest.raises(PlannerOutputError):
        generate_plan(make_request(), client=client)

def test_wrong_day_numbers(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    client = FakeClient(content=make_plan_json(days=2))
    with pytest.raises(PlannerOutputError):
        generate_plan(make_request(), client=client)

def test_timeout_error(monkeypatch):
    class FakeTimeoutError(Exception):
        pass
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setattr("backend.app.services.planner.APITimeoutError",
                        FakeTimeoutError, )   
    client = FakeClient(error=FakeTimeoutError())
    with pytest.raises(PlannerTimeoutError):
        generate_plan(make_request(), client=client)