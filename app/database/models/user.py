import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.enums.role_enum import RoleEnum
from app.database.base import Base


class User(Base):
    __tablename__: str = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False, default=RoleEnum.TEAM_MEMBER)
    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
    )

    # # Relationship
    # shops = relationship("Shop", back_populates="user", cascade="all, delete")
