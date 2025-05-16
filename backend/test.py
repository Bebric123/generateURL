import unittest
import services
from datetime import datetime, timedelta
import json
import redis
from config import settings

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        self.r.flushdb()

    def test_is_valid_email(self):
        self.assertTrue(services.is_valid_email("test@example.com"))
        self.assertFalse(services.is_valid_email("invalid-email"))

    def test_deactivate_expired_links(self):
        short_key = "test123"
        self.r.set(short_key, "http://abc.com")
        self.r.set(f"created_at:{short_key}", (datetime.now() - timedelta(minutes=2)).isoformat())
        self.r.set(f"last_accessed:{short_key}", (datetime.now() - timedelta(minutes=2)).isoformat())
        
        email = "user@example.com"
        user_key = services.get_user_key(email)
        link_data = {
            'short_url': f'http://short.link/{short_key}',
            'long_url': 'http://abc.com',
            'is_active': True
        }
        self.r.rpush(user_key, json.dumps(link_data))
        
        result = services.deactivate_expired_links()
        self.assertTrue(result)
        
        links = self.r.lrange(user_key, 0, -1)
        self.assertEqual(len(links), 1)
        self.assertFalse(json.loads(links[0])['is_active'])

    def test_get_analitic(self):
        email = "user@example.com"
        user_key = services.get_user_key(email)
        links = [
            {
                'short_url': 'http://short.link/abc123',
                'long_url': 'http://localhost:3000/statistic',
                'is_active': True
            },
            {
                'short_url': 'http://short.link/def456',
                'long_url': 'http://localhost:3000/statistic',
                'is_active': True
            }
        ]
        
        for link in links:
            self.r.rpush(user_key, json.dumps(link))
        self.r.hset("clicks:abc123:day", "2023-01-01", 5)
        self.r.hset("clicks:def456:day", "2023-01-01", 3)
        
        analytics = services.get_analitic(user_key)
        
        self.assertEqual(analytics['useful_domen'], "localhost:3000")
        self.assertEqual(analytics['one_use_links'], 0)
        self.assertEqual(analytics['max_redirect_link'], 5)
        self.assertEqual(analytics['max_all_redirect'], 8)

    
if __name__ == '__main__':
    unittest.main()