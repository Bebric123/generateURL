import redis
from datetime import datetime, timedelta
from config import settings
import logging
import json

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

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