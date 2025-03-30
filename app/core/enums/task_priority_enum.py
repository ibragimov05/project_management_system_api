from enum import Enum


class TaskPriority(str, Enum):
    LOW: str = "LOW"
    MEDIUM: str = "MEDIUM"
    HIGH: str = "HIGH"
