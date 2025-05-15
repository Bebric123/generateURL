import redis
from urllib.parse import urlparse
import re
import hashlib
from html import escape
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
                return True
            
def safe_json_loads(data: str):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None
    
def get_analitic(user_key):
    try:
        if not r.exists(user_key):
            return None

        links = r.lrange(user_key, 0, -1)
        if not links:
            return None
        
        analytics = {
            "useful_domen": "",
            "one_use_links": 0,
            "max_redirect_link": 0,
            "max_all_redirect": 0
        }
        
        domain_counts = {}
        
        for link in links:
            try:
                link_data = json.loads(link)
                short_key = link_data['short_url'].split('/')[-1]

                day_stats = r.hgetall(f"clicks:{short_key}:day") or {}
                total_clicks = sum(int(v) for v in day_stats.values())

                analytics['max_all_redirect'] += total_clicks
                analytics['max_redirect_link'] = max(analytics['max_redirect_link'], total_clicks)
                analytics['one_use_links'] += 1 if total_clicks == 1 else 0
                if 'long_url' in link_data:
                    try:
                        domain = link_data['long_url'].split('/')[2].replace('www.', '')
                        domain_counts[domain] = domain_counts.get(domain, 0) + total_clicks
                    except (IndexError, AttributeError):
                        continue
                        
            except json.JSONDecodeError:
                continue
            
        if domain_counts:
            analytics['useful_domen'] = max(domain_counts.items(), key=lambda x: x[1])[0]
        
        return analytics
        
    except Exception as e:
        print(f"Error in analytics calculation: {e}")
        return None