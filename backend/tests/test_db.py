import pytest
from backend.app.schemas import StudyDay, StudyPlan
from sqlmodel import select, Session
from backend.app.services.progress import save_plan, get_saved_plan,PlanPersistenceError
from backend.app.db.models import Plan

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

def test_save_plan_rollback_on_partial_plan(session, test_engine, monkeypatch):
    """提交失败时回滚"""
    def broken_commit():
        # 模拟在保存计划时抛出异常
        raise  RuntimeError("模拟数据库提交失败")
    monkeypatch.setattr(session, "commit", broken_commit)
    with pytest.raises(PlanPersistenceError):
        save_plan(mark_plan(), session)
    with Session(test_engine) as new_session:
        # 检查数据库中是否没有保存任何计划
        result = new_session.exec(select(Plan)).all()
        assert len(result) == 0