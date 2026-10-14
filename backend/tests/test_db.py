from backend.app.schemas import StudyDay, StudyPlan
from test_planner import make_plan_json
from backend.app.services.progress import save_plan, get_saved_plan
from fastapi.testclient import TestClient
def test_save_plan_creates_tasks():
    # 构造假的 StudyPlan
    # 使用测试数据库
    # 调用 save_plan()
    # 检查计划数量和任务数量
    pass


def mark_plan():
    return StudyPlan(
        title="Python 学习计划",
        summary="基础学习",
        days=[
            StudyDay(
                day=1,
                topic="变量",
                tasks=["学习变量定义", "完成练习"],
                expected_output="能够解释变量",
            )
        ],
    )
    
def test_save_plan(session):
    plan = mark_plan()
    result = save_plan(plan, session)
    assert result.id is not None
    assert len(result.tasks) == 2
    assert result.tasks[0].status == "pending"
    assert result.tasks[0].task_order == 1

def test_get_saved_plan(session):
    plan = mark_plan()
    test_plan = save_plan(plan, session)  # 保存计划并获取返回的 SavedPlan 对象
    id = test_plan.id
    plan = get_saved_plan(id, session)
    assert plan is not None
    assert plan.title == "Python 学习计划"
    assert len(plan.tasks) == 2
    assert plan.tasks[0].task_order == 1
    # 检查查询结果的标题、任务数量和任务顺序
    
def test_get_missing_plan_returns_none(session):
    result = get_saved_plan(999999, session)
    assert result is None