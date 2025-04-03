from pydantic import BaseModel


class ProjectMemberBaseScheme(BaseModel):
    user_id: int
    project_id: int
