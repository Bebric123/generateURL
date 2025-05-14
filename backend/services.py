import redis
import secrets
import hashlib
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config import settings
import logging

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
    
def deactivate_expired_links():
    now = datetime.now()
    for key in r.scan_iter("*"):
        key_str = key.decode()
        
        if key_str.startswith('user:') or key_str.startswith(('created_at:', 'last_accessed:')):
            continue
        last_accessed = r.get(f"last_accessed:{key_str}")
        
        if last_accessed:
            last_accessed = datetime.fromisoformat(last_accessed.decode())
            
            if (now - last_accessed) > timedelta(minutes=1):
                r.delete(key_str)
                r.delete(f"created_at:{key_str}")
                r.delete(f"last_accessed:{key_str}")
                for user_key in r.scan_iter("user:*"):
                    links = r.lrange(user_key, 0, -1)
                    for i, link in enumerate(links):
                        link_data = json.loads(link)
                        if link_data.get('short_url', '').endswith(f"/{key_str}"):
                            link_data['is_active'] = False
                            r.lset(user_key, i, json.dumps(link_data))
                
                logging.info(f"Deactivated inactive link: {key_str} (last accessed: {last_accessed})")