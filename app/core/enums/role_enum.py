from enum import Enum


class RoleEnum(Enum):
    ADMIN: str = "ADMIN"
    PROJECT_MANAGER: str = "PROJECT_MANAGER"
    TEAM_MEMBER: str = "TEAM_MEMBER"
