from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums.task_priority_enum import TaskPriority
from app.core.enums.task_status_enum import TaskStatus


class TaskBaseScheme(BaseModel):
    project_id: int
    title: str = Field(max_length=255, min_length=4)
    description: str = Field(min_length=4)
    assignee_id: int
    status: TaskStatus
    priority: TaskPriority
    due_to: datetime


class CreateTaskScheme(TaskBaseScheme):
    pass


class UpdateTaskScheme(TaskBaseScheme):
    pass


class TaskResponseScheme(TaskBaseScheme):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
