import secrets
import redis
from config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def is_link_unique(short_key: str) -> bool:
    return not r.exists(short_key)

def generate_unique_key(length: int = 6, max_attempts: int = 100) -> str:
    for _ in range(max_attempts):
        key = secrets.token_urlsafe(length)[:length]
        if is_link_unique(key):
            return key
    raise ValueError("Failed to generate unique key")