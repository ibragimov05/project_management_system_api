from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserScheme(BaseModel):
    username: str = Field(min_length=5, max_length=99, description="username")
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., description="user password")
    telegram_chat_id: Optional[str] = Field(None, description="user's telegram chat id")


class CreateUserScheme(UserScheme):
    pass


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    telegram_chat_id: Optional[str]
    is_active: bool
    is_super_admin: bool = False

    class Config:
        from_attributes = True
