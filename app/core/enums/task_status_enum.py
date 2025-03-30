from enum import Enum


class TaskStatus(str, Enum):
    TODO: str = "TODO"
    IN_PROGRESS: str = "IN_PROGRESS"
    DONE: str = "DONE"
