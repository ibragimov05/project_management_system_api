from datetime import datetime

from pydantic import BaseModel, Field


class CommentBaseScheme(BaseModel):
    content: str = Field(min_length=4)
    author_id: int
    project_id: int
    task_id: int


class CreateCommentScheme(CommentBaseScheme):
    pass


class UpdateCommentScheme(CommentBaseScheme):
    pass


class CommentResponseScheme(CommentBaseScheme):
    id: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
