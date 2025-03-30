from sqlalchemy import Column, ForeignKey, Integer, Enum

from app.core.enums.user_role_enum import UserRole
from app.database.base import Base


class ProjectMember(Base):
    __tablename__: str = "project_members"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.TEAM_MEMBER, nullable=False)
