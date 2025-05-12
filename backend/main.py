from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from fastapi.responses import RedirectResponse
import redis
import secrets
import hashlib
import datetime
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0)
logging.basicConfig(level=logging.INFO, filename='py_log.log', filemode='w', format="%(asctime)s %(levelname)s %(message)s")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "swooplida@gmail.com"
SMTP_PASSWORD = "gvev ltnr iojj ciie"
EMAIL_FROM = "swooplida@gmail.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    long_url: str
    email: str

class UserLinksRequest(BaseModel):
    email: str

def generate_short_key():
    return secrets.token_urlsafe(5)[:8]

def get_user_key(email: str) -> str:
    return f"user:{hashlib.sha256(email.encode()).hexdigest()}"

def send_email_notification(email_to: str, short_url: str, long_url: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = email_to
        msg['Subject'] = "Ваша ссылка была успешно сокращена"
        
        body = f"""
        <h1>Ваша ссылка была сокращена!</h1>
        <p><strong>Оригинальная ссылка:</strong> {long_url}</p>
        <p><strong>Сокращенная ссылка:</strong> <a href="{short_url}">{short_url}</a></p>
        <p>Дата создания: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() 
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
        logging.info(f"Email sent to {email_to}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

@app.post("/shorten")
async def shorten_url(request: UrlRequest):  
    short_key = generate_short_key()
    r.set(short_key, request.long_url)

    user_key = get_user_key(request.email)
    link_data = {
        'short_url': f'http://localhost:8000/{short_key}',
        'long_url': request.long_url,
        'created_at': datetime.datetime.now().isoformat()
    }

    r.rpush(user_key, json.dumps(link_data)) 
    logging.info(f"Generated url {short_key}")
    
    send_email_notification(
        email_to=request.email,
        short_url=link_data['short_url'],
        long_url=request.long_url
    )
    
    return {'short_url': link_data['short_url']}

@app.post("/user/links")
async def get_user_links(request: UserLinksRequest):
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    return {"links": [json.loads(link) for link in links]}

@app.get("/{short_key}")
async def redirect(short_key: str):
    long_url = r.get(short_key)
    logging.info(f"Redirecting from {short_key}")
    if not long_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=long_url.decode())