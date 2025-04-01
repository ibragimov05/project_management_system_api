from pydantic import BaseModel

from app.core.enums.user_role_enum import UserRole


class ProjectMemberBaseScheme(BaseModel):
    user_id: int
    project_id: int
    role: UserRole
