from datetime import datetime,timezone

from sqlmodel import Field
from typing import Optional
from sqlmodel import SQLModel


class Plan(SQLModel, table=True):
    __tablename__ = "plans"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    summary: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="plans.id",index=True)
    day: int
    topic: str
    task_order: int
    description: str
    expected_output: str
    status: str = Field(default="pending")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    