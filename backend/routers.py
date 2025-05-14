from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services import r, get_user_key, send_email_notification
from checker import generate_unique_key, get_available_combinations, get_available_count
from schemas import UrlRequest, UserLinksRequest, LinkStatsRequest, AvailableCombinationsResponse
from config import settings
import json
from datetime import datetime, timedelta
import logging

router = APIRouter()

def deactivate_expired_links():
    now = datetime.now()
    for key in r.scan_iter("*"):
        key_str = key.decode()
        if key_str.startswith('user:') or key_str.startswith(('created_at:', 'last_accessed:')):
            continue
        
        created_at = r.get(f"created_at:{key_str}")
        if created_at:
            created_at = datetime.fromisoformat(created_at.decode())
            if (now - created_at) > timedelta(minutes=2):
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
                
                logging.info(f"Deactivated and removed link: {key_str}")

@router.post("/shorten")
async def shorten_url(request: UrlRequest):  
    short_key = generate_unique_key()
    r.set(short_key, request.long_url)
    r.set(f"created_at:{short_key}", datetime.now().isoformat())
    r.set(f"last_accessed:{short_key}", datetime.now().isoformat())

    user_key = get_user_key(request.email)
    link_data = {
        'short_url': f'{settings.BASE_URL}/{short_key}',
        'long_url': request.long_url,
        'created_at': datetime.now().isoformat(),
        'is_active': True
    }

    r.rpush(user_key, json.dumps(link_data)) 
    logging.info(f"Generated url {short_key}")
    send_email_notification(
        email_to=request.email,
        short_url=link_data['short_url'],
        long_url=request.long_url
    )

    deactivate_expired_links()
    return {'short_url': link_data['short_url']}

@router.get("/available-combinations", response_model=AvailableCombinationsResponse)
async def available_combinations(count: int = 5):
    return {
        "combinations": get_available_combinations(count),
        "available_count": get_available_count()
    }

@router.post("/user/links")
async def get_user_links(request: UserLinksRequest):
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    result_links = []
    for link in links:
        link_data = json.loads(link)
        short_key = link_data['short_url'].split('/')[-1]
        if not r.exists(short_key):
            link_data['is_active'] = False
        
        result_links.append(link_data)
    
    return {"links": result_links}

@router.get("/{short_key}")
async def redirect(short_key: str):
    if not r.exists(short_key):
        raise HTTPException(status_code=410, detail="Ссылка неактивна")
    
    for user_key in r.scan_iter("user:*"):
        links = r.lrange(user_key, 0, -1)
        for link in links:
            link_data = json.loads(link)
            if link_data.get('short_url', '').endswith(f"/{short_key}"):
                if not link_data.get('is_active', True):
                    raise HTTPException(status_code=410, detail="Ссылка неактивна")
                break
    now = datetime.now()
    day_key = now.strftime("%Y-%m-%d")
    month_key = now.strftime("%Y-%m")
    r.hincrby(f"clicks:{short_key}:day", day_key, 1)
    r.hincrby(f"clicks:{short_key}:month", month_key, 1)
    r.set(f"last_accessed:{short_key}", now.isoformat())
    
    long_url = r.get(short_key)
    if not long_url:
        raise HTTPException(status_code=404)
    
    return RedirectResponse(url=long_url.decode())

@router.post("/stats/clicks")
async def get_link_clicks(request: LinkStatsRequest):
    short_key = request.short_url.split('/')[-1]
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    if not any(link for link in links if json.loads(link)['short_url'] == request.short_url):
        raise HTTPException(status_code=403, detail="Not your link")
    day_stats = r.hgetall(f"clicks:{short_key}:day") or {}
    month_stats = r.hgetall(f"clicks:{short_key}:month") or {}
    def convert_bytes(data):
        return {k.decode(): int(v.decode()) for k, v in data.items()}
    result = {
        'day': convert_bytes(day_stats),
        'month': convert_bytes(month_stats)
    }
    logging.info(f"Stats for {short_key}: {result}")
    return result[request.period]