from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services import r, get_user_key, send_email_notification, deactivate_expired_links, get_analitic, safe_json_loads
from checker import generate_unique_key
from schemas import UrlRequest, UserLinksRequest, LinkStatsRequest, AnaliticLinks
from config import settings
import json
from datetime import datetime
import logging

router = APIRouter()

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

@router.post("/analytics/user")
async def get_user_analytics(request: AnaliticLinks):
    if not request.email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    user_key = get_user_key(request.email)
    analytics = get_analitic(user_key)
    
    if not analytics:
        return {
            "useful_domen": "No data",
            "one_use_links": 0,
            "max_redirect_link": 0,
            "max_all_redirect": 0
        }
    
    return analytics

@router.post("/user/links")
async def get_user_links(request: UserLinksRequest):
    user_key = get_user_key(request.email)
    links = r.lrange(user_key, 0, -1)
    result_links = []
    for link in links:
        link_data = safe_json_loads(link)
        if not link_data:
            continue
        short_key = link_data['short_url'].split('/')[-1]
        if not r.exists(short_key):
            link_data['is_active'] = False
        
        result_links.append(link_data)
    deactivate_expired_links()
    return {"links": result_links}

@router.get("/{short_key}")
async def redirect(short_key: str):
    if not r.exists(short_key):
        raise HTTPException(status_code=410, detail="Ссылка неактивна")

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