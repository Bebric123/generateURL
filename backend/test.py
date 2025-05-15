import unittest
from services import send_email_notification, deactivate_expired_links
from checker import generate_unique_key, get_available_count

class TestStringMethods(unittest.TestCase):
    def test_1(self):
        self.assertEqual(type(generate_unique_key()), str)
    def test_2(self):
        self.assertEqual(type(get_available_count()), int)
    def test_3(self):
        self.assertEqual(send_email_notification('swooplida@gmail.com', 'fhjhf', 'adadasd'), True)
    def test_4(self):
        self.assertEqual(deactivate_expired_links(), True)
    
if __name__ == '__main__':
    unittest.main()