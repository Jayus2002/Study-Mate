from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
class PlanRequest(BaseModel):
    goal: str = Field(min_length=2)
    duration_days: int = Field(ge=1, le=30)
    daily_minutes: int = Field(ge=15, le=720)
    background: str = ""
    @field_validator("goal")
    @classmethod
    def goal_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Goal must not be empty.")
        return value
class StudyDay(BaseModel):
    day: int = Field(ge=1)
    topic: str
    tasks: List[str] = Field(min_length=1)
    expected_output: str

    @field_validator("topic","expected_output")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be empty.")
        return value
    @field_validator("tasks")
    @classmethod
    def tasks_must_not_be_empty(cls, value: List[str]) -> List[str]:
        cleaned_tasks = [task.strip() for task in value if task.strip()]
        if not cleaned_tasks:
            raise ValueError("Tasks list must contain at least one non-empty task.")
        return cleaned_tasks

class StudyPlan(BaseModel):
    title: str
    summary: str
    days: List[StudyDay] = Field(min_length=1)

    @model_validator(mode="after")
    def validata_day_numbers(self):
        numbers = [item.day for item in self.days]
        expected_numbers = list(range(1, len(self.days) + 1))
        if numbers != expected_numbers:
            raise ValueError(f"Day numbers must be sequential starting from 1. Found: {numbers}")
        return self

class SavedTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    day: int
    topic: str
    task_order: int
    description: str
    expected_output: str
    status: str

class SavedPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: str
    created_at: datetime
    tasks: List[SavedTask] = []