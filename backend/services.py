import redis
from urllib.parse import urlparse
import re
import hashlib
from html import escape
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_user_key(email: str) -> str:
    if not is_valid_email(email):
        raise ValueError("Invalid email format")
    return f"user:{hashlib.sha256(email.encode()).hexdigest()}"

def sanitize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL format")
    return url

def send_email_notification(email_to: str, short_url: str, long_url: str):
    try:
        sanitize_url(short_url)
        sanitize_url(long_url)
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = email_to
        msg['Subject'] = "Ваша ссылка была успешно сокращена"
        
        body = f"""
        <h1>Ваша ссылка была сокращена!</h1>
        <p><strong>Оригинальная ссылка:</strong> {escape(long_url)}</p>
        <p><strong>Сокращенная ссылка:</strong> <a href="{escape(short_url)}">{escape(short_url)}</a></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logging.error(f"Invalid URL in notification: {e}")
        raise e
            
def safe_json_loads(data: str):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None