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

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0)
logging.basicConfig(level=logging.INFO, filename='py_log.log', filemode='w', format="%(asctime)s %(levelname)s %(message)s")

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
    email:str

def generate_short_key():
    return secrets.token_urlsafe(5)[:8]

def get_user_key(email: str) -> str:
    return f"user:{hashlib.sha256(email.encode()).hexdigest()}"

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
    logging.info(f"generate url {short_key}")
    return {'short_url': link_data['short_url']}

@app.post("/user/links")
async def get_user_links(request: UserLinksRequest):
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    return {"links": [json.loads(link) for link in links]}

@app.get("/{short_key}")
async def redirect(short_key: str):
    long_url = r.get(short_key)
    logging.info(f"redirecting")
    if not long_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=long_url.decode())