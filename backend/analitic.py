import redis
from config import settings
import logging
import json
from services import sanitize_url

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

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
                sanitize_url(link_data.get('long_url', ''))
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
                        logging.warning(f"Skipping invalid URL: {e}")
                        continue
                        
            except json.JSONDecodeError:
                continue
            
        if domain_counts:
            analytics['useful_domen'] = max(domain_counts.items(), key=lambda x: x[1])[0]
        
        return analytics
        
    except Exception as e:
        print(f"Error in analytics calculation: {e}")
        return None