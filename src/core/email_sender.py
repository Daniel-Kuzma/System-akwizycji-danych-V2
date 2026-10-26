import aiosmtplib
from email.mime.text import MIMEText
from .settings import settings


async def send_email(email_receiver : str, email_subject : str, email_message):
    message = MIMEText(email_message, "plain")
    message["Subject"] = email_subject
    message["From"] = settings.username
    message["To"] = email_receiver

    async with aiosmtplib.SMTP(hostname = settings.smtp_server, port = settings.smtp_port) as server:
        server.starttls()
        server.login(settings.username, settings.password)  
        server.sendmail(settings.username, email_receiver, message.as_string())