from datetime import datetime

from pydantic import BaseModel, Field

from app.schemes.comment_scheme import CommentResponseScheme
from app.schemes.task_scheme import TaskResponseScheme
from app.schemes.user_scheme import UserResponseSchema


class ProjectBaseScheme(BaseModel):
    name: str = Field(description="project's name", min_length=2, max_length=255)
    description: str = Field(description="description for project", min_length=2)
    start_date: datetime = Field(description="star date of the project", default=datetime.now())
    deadline: datetime = Field(description="end date for the project")


class CreateProjectScheme(ProjectBaseScheme):
    pass


class UpdateProjectScheme(ProjectBaseScheme):
    pass


class ProjectResponseScheme(ProjectBaseScheme):
    id: int
    created_at: datetime
    updated_at: datetime

    members: list[UserResponseSchema] | None
    tasks: list[TaskResponseScheme] | None
    comments: list[CommentResponseScheme] | None

    class Config:
        from_attributes = True
