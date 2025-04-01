from datetime import datetime

from pydantic import BaseModel, Field


class ProjectBaseScheme(BaseModel):
    name: str = Field(description="project's name", min_length=4, max_length=255)
    description: str = Field(description="description for project", min_length=4)
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

    members: list[str] = []
    tasks: list[str] = []
    comments: list[str] = []

    class Config:
        from_attributes = True
