from ..schemas import StudyPlan, SavedPlan, SavedTask
from sqlmodel import Session, select
from ..db.models import Plan, Task

class PlanPersistenceError(Exception):
    pass

def _build_saved_plan(plan: Plan, tasks: list[Task]) -> SavedPlan:
    return SavedPlan(
        id=plan.id,
        title=plan.title,
        summary=plan.summary,
        created_at=plan.created_at,
            tasks=[
            SavedTask.model_validate(task, from_attributes=True)
            for task in tasks
        ],
    )
 
def save_plan(plan_data: StudyPlan, session: Session):
    db_plan = Plan(
        title=plan_data.title,
        summary=plan_data.summary
    )
    try:
        session.add(db_plan)
        session.flush()  # Ensure the plan is saved and has an ID
        # print(db_plan.id)
        for study_day in plan_data.days:
            for order, description in enumerate(study_day.tasks, start=1):
                db_task = Task(
                    plan_id=db_plan.id,
                    day=study_day.day,
                    topic=study_day.topic,
                    task_order=order,
                    description=description,
                    expected_output=study_day.expected_output,
                    status="pending"
                )
                session.add(db_task)
        session.commit()  # Commit the transaction to save all changes
        session.refresh(db_plan)  # Refresh to get the latest state from the database
        tasks = session.exec(
            select(Task)
            .where(Task.plan_id == db_plan.id)
            .order_by(Task.day, Task.task_order)
        ).all()
        return _build_saved_plan(db_plan, tasks)
    except Exception as e:
        session.rollback()  # Rollback the transaction in case of error
        raise PlanPersistenceError(f"Failed to save plan: {e}") from e

def get_saved_plan(
    plan_id: int,
    session: Session
) -> SavedPlan | None:
    db_plan = session.get(Plan, plan_id)

    if db_plan is None:
        return None
    tasks = session.exec(
        select(Task)
        .where(Task.plan_id == db_plan.id)
        .order_by(Task.day, Task.task_order)
    ).all()

    return _build_saved_plan(db_plan, tasks)