from fastapi.testclient import TestClient
from backend.app import main
from backend.app.services.planner import (
    PlannerOutputError,
    PlannerTimeoutError,
)

client = TestClient(main.app)

def request_body():
    return {
        "goal": "学习 Python",
        "duration_days": 3,
        "daily_minutes": 60,
        "background": "了解变量"
    }

def test_timeout_map_to_504(monkeypatch):
    def mock_generate_plan(request):
        raise PlannerTimeoutError("Simulated timeout error")
    monkeypatch.setattr(main, "generate_plan", mock_generate_plan)
    response = client.post("/plan", json=request_body())
    assert response.status_code == 504
    assert response.json() == {"detail": "请求超时，请稍后再试。"}

def test_output_error_map_to_500(monkeypatch):
    def mock_generate_plan(request):
        raise PlannerOutputError("Simulated output error")
    monkeypatch.setattr(main, "generate_plan", mock_generate_plan)
    response = client.post("/plan", json=request_body())
    assert response.status_code == 500
    assert response.json() == {"detail": "生成的学习计划格式不正确。"}