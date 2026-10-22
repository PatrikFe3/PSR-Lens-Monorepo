import unittest
from src.api.routes import analyze_message

class MyTestCase(unittest.TestCase):
    def analyze_message(self):
          self.assertTrue(analyze_message('Hello World!'))


if __name__ == '__main__':
    unittest.main()
