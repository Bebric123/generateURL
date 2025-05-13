from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services import r, generate_short_key, get_user_key, send_email_notification
from schemas import UrlRequest, UserLinksRequest
from config import Settings
import json
from datetime import datetime
import logging

router = APIRouter()

@router.post("/shorten")
async def shorten_url(request: UrlRequest):  
    short_key = generate_short_key()
    r.set(short_key, request.long_url)

    user_key = get_user_key(request.email)
    link_data = {
        'short_url': f'{Settings.BASE_URL}/{short_key}',
        'long_url': request.long_url,
        'created_at': datetime.now().isoformat()
    }

    r.rpush(user_key, json.dumps(link_data)) 
    logging.info(f"Generated url {short_key}")
    
    send_email_notification(
        email_to=request.email,
        short_url=link_data['short_url'],
        long_url=request.long_url
    )
    
    return {'short_url': link_data['short_url']}

@router.post("/user/links")
async def get_user_links(request: UserLinksRequest):
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    return {"links": [json.loads(link) for link in links]}

@router.get("/{short_key}")
async def redirect(short_key: str):
    long_url = r.get(short_key)
    logging.info(f"Redirecting from {short_key}")
    if not long_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=long_url.decode())