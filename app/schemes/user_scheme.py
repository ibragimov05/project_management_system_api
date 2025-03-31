from pydantic import BaseModel, EmailStr, Field

from app.core.enums.user_role_enum import UserRole


class UserScheme(BaseModel):
    username: str = Field(min_length=5, max_length=99, description="username")
    email: EmailStr = Field(..., description="user email")
    password: str = Field(min_length=6, description="user password")
    full_name: str = Field(min_length=4, description="user's full name")
    role: UserRole = Field(description="user's role", default=UserRole.TEAM_MEMBER)


class CreateUserScheme(UserScheme):
    pass


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True
