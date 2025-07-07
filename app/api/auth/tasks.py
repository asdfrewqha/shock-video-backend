from email.message import EmailMessage
import logging
import smtplib
import ssl

from celery import shared_task
from starlette.templating import Jinja2Templates

from app.core.config import EMAIL_HOST, EMAIL_PASSWORD, EMAIL_PORT, EMAIL_USERNAME, FRONTEND_URL


logger = logging.getLogger(__name__)


@shared_task
def send_confirmation_email(to_email: str, code: str) -> None:
    templates = Jinja2Templates(directory="templates")
    template = templates.get_template(name="email_confirmation.html")
    html_content = template.render(code=code)
    message = EmailMessage()
    message.add_alternative(html_content, subtype="html")
    message["From"] = EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = f"Email confirmation <{code}>"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host=EMAIL_HOST, port=EMAIL_PORT, context=context) as smtp:
        smtp.login(
            user=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
        )
        smtp.send_message(msg=message)
    logger.info("Email sent")


@shared_task
def send_confirmation_email_pwd(to_email: str, token: str) -> None:
    confirmation_url = f"{FRONTEND_URL}/edit-password-confirm?token={token}"

    templates = Jinja2Templates(directory="templates")
    template = templates.get_template(name="pwd_confirmation.html")
    html_content = template.render(confirmation_url=confirmation_url, token=token)
    message = EmailMessage()
    message.add_alternative(html_content, subtype="html")
    message["From"] = EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = "Password editing confirmation"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host=EMAIL_HOST, port=EMAIL_PORT, context=context) as smtp:
        smtp.login(
            user=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
        )
        smtp.send_message(msg=message)
    logger.info("Email sent")
