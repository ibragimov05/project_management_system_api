import smtplib

from email.message import EmailMessage

from app.core.utils.constants import APP_EMAIL, APP_PASSWORD
from app.database.models.tasks import Task
from app.services.logger_service import logger


class EmailService:
    def __init__(self) -> None:
        self.app_email: str = APP_EMAIL
        self.app_password: str = APP_PASSWORD

    def send_new_task_email(self, recipient_email: str, task: Task) -> None:
        try:
            msg = EmailMessage()
            msg["Subject"] = f"New Task Assigned: {task.title}"
            msg["From"] = self.app_email
            msg["To"] = recipient_email

            # Create a clear, structured email body with task details.
            task_details = (
                f"Hello,\n\n"
                f"You have been assigned a new task. Please find the details below:\n\n"
                f"Task ID: {task.id}\n"
                f"Project ID: {task.project_id}\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'No description provided.'}\n"
                f"Status: {task.status.name}\n"
                f"Priority: {task.priority.name}\n"
                f"Due Date: {task.due_to.strftime('%Y-%m-%d %H:%M:%S') if task.due_to else 'N/A'}\n"
                f"Created At: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'}\n"
                f"Updated At: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else 'N/A'}\n\n"
                f"Please log in to the Project Management System for more details and to take action on this task.\n\n"
                f"Best regards,\n"
                f"Your Project Management Team"
            )
            msg.set_content(task_details)

            # Send the email securely using SMTP over SSL.
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.app_email, self.app_password)
                smtp.send_message(msg)

            logger.info(f"Email has been sent successfully to {recipient_email}!")
        except Exception as e:
            logger.error(f"Error when sending email to {recipient_email}: {str(e)}")
