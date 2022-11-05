import os
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
    body: Dict[str, Any]


template = """
        <html>
        <body>
            <p>Hi !!!
            <br>Thanks for using fastapi mail, keep using it..!!!</p>
        </body>
        </html>
        """

conf = ConnectionConfig(
    MAIL_USERNAME='vardeath',
    MAIL_PASSWORD='ymqtswvegisomyeq',
    MAIL_FROM='vardeath@yandex.ru',
    MAIL_PORT=465,
    MAIL_SERVER='smtp.yandex.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    SUPPRESS_SEND=True
)


async def send_mail(subject: str, email: EmailSchema, template_name: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email.email],
        template_body=template,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    # background_tasks = BackgroundTasks()
    # background_tasks.add_task(fm.send_message, message,
    #                           template_name=template_name)
