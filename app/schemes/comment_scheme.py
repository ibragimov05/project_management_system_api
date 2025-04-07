from datetime import datetime

from pydantic import BaseModel, Field


class CommentBaseScheme(BaseModel):
    content: str = Field(min_length=4)


class CreateCommentScheme(CommentBaseScheme):
    task_id: int


class UpdateCommentScheme(CommentBaseScheme):
    pass


class CommentResponseScheme(CommentBaseScheme):
    id: int
    author_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
