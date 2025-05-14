import secrets
import redis
from config import settings
from typing import List, Tuple

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def is_link_unique(short_key: str) -> bool:
    return not r.exists(short_key)

def generate_unique_key(length: int = 6) -> str:
    key = secrets.token_urlsafe(length)[:length]
    if is_link_unique(key):
        return key

def get_available_count() -> int:
    chars = 62 
    length = 6
    total_combinations = chars ** length
    used_keys = sum(1 for key in r.scan_iter() 
                   if not key.decode().startswith(('created_at:', 'last_accessed:', 'user:', 'clicks:')))
    
    return max(0, total_combinations - used_keys)