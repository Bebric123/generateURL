import redis
import secrets
import hashlib
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def generate_short_key():
    return secrets.token_urlsafe(5)[:8]

def get_user_key(email: str) -> str:
    return f"user:{hashlib.sha256(email.encode()).hexdigest()}"

def send_email_notification(email_to: str, short_url: str, long_url: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = email_to
        msg['Subject'] = "Ваша ссылка была успешно сокращена"
        
        body = f"""
        <h1>Ваша ссылка была сокращена!</h1>
        <p><strong>Оригинальная ссылка:</strong> {long_url}</p>
        <p><strong>Сокращенная ссылка:</strong> <a href="{short_url}">{short_url}</a></p>
        <p>Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        raise e