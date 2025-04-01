from sqlalchemy import Column, Enum, ForeignKey, Integer

from app.core.enums.user_role_enum import UserRole
from app.database.base import Base


class ProjectMember(Base):
    __tablename__: str = "project_members"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.TEAM_MEMBER, nullable=False)

    def __repr__(self):
        return f"<ProjectMember(user_id={self.user_id}, project_id={self.project_id}, role={self.role})>"
