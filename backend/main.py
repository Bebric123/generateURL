from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from fastapi.responses import RedirectResponse
import redis
import secrets

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    long_url: str

def generate_short_key():
    return secrets.token_urlsafe(5)[:8]

@app.post("/shorten")
async def shorten_url(request: UrlRequest):  
    short_key = generate_short_key()
    r.set(short_key, request.long_url)
    return {"short_url": f"http://localhost:8000/{short_key}"}

@app.get("/{short_key}")
async def redirect(short_key: str):
    long_url = r.get(short_key)
    if not long_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=long_url.decode())