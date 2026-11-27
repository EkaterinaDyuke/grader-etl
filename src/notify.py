"""Отправка письма с итогом выгрузки."""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

REQUIRED = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "EMAIL_TO")


def is_configured():
    """Проверяет, что все настройки почты заполнены."""
    return all(os.getenv(name) for name in REQUIRED)


def send_report(subject, text):
    """Отправляет письмо с итогом. Возвращает True, если отправлено."""
    if not is_configured():
        log.warning("почта не настроена — письмо не отправлено")
        return False

    message = EmailMessage()
    message.set_content(text)
    message["Subject"] = subject
    message["From"] = os.getenv("SMTP_USER")
    message["To"] = os.getenv("EMAIL_TO")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(
            os.getenv("SMTP_HOST"),
            int(os.getenv("SMTP_PORT")),
            context=context,
        ) as server:
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(message)
    except (smtplib.SMTPException, OSError) as error:
        log.error("письмо не отправлено: %s", error)
        return False

    log.info("письмо отправлено на %s", os.getenv("EMAIL_TO"))
    return True