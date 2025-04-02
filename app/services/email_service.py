import smtplib

from email.message import EmailMessage
from typing import Annotated

from fastapi import Depends

from app.core.utils.constants import APP_EMAIL, APP_PASSWORD
from app.services.logger_service import logger


class EmailService:
    def __init__(self) -> None:
        self.app_email: str = APP_EMAIL
        self.app_password: str = APP_PASSWORD

    def send_new_task_email(self, recipient_email: str, subject: str, detail: str) -> None:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.app_email
            msg["To"] = recipient_email

            msg.set_content(detail)

            # Send the email securely using SMTP over SSL.
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.app_email, self.app_password)
                smtp.send_message(msg)

            logger.info(f"Email has been sent successfully to {recipient_email}!")
        except Exception as e:
            logger.error(f"Error when sending email to {recipient_email}: {str(e)}")


def _get_email_service() -> EmailService:
    return EmailService()


EMAIL_SERVICE_DEPENDENCY = Annotated[EmailService, Depends(_get_email_service)]
