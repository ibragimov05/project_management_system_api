import re

from app.database.models.tasks import Task


class Helpers:
    @staticmethod
    def is_valid_email(email: str):
        return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None

    @staticmethod
    def get_new_task_assigned_detail(task: Task, project_name: str, username: str, assigned_by: str) -> str:
        return (
            f"Hello, {username}!\n\n"
            f"You have been assigned a new task by {assigned_by}. Please find the details below:\n\n"
            f"Task ID: {task.id}\n"
            f"Project name: {project_name}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description or 'No description provided.'}\n"
            f"Status: {task.status.name}\n"
            f"Priority: {task.priority.name}\n"
            f"Due-date: {task.due_to.strftime('%Y-%m-%d %H:%M:%S') if task.due_to else 'N/A'}\n"
            f"Created-at: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'}\n"
            f"Updated-at: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else 'N/A'}\n\n"
            f"Please log in to the Project Management System for more details and to take action on this task.\n\n"
            f"Best regards, your Project Management Team"
        )

    @staticmethod
    def get_task_updated_details(task: Task, project_name: str, username: str, updated_by: str) -> str:
        return (
            f"Hello, {username}!\n\n"
            f"Your task has been updated by {updated_by}. Please find the details below:\n\n"
            f"Task ID: {task.id}\n"
            f"Project name: {project_name}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description or 'No description provided.'}\n"
            f"Status: {task.status.name}\n"
            f"Priority: {task.priority.name}\n"
            f"Due-date: {task.due_to.strftime('%Y-%m-%d %H:%M:%S') if task.due_to else 'N/A'}\n"
            f"Created-at: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'}\n"
            f"Updated-at: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else 'N/A'}\n\n"
            f"Please log in to the Project Management System for more details and to take action on this task.\n\n"
            f"Best regards, your Project Management Team"
        )
