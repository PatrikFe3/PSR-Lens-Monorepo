import unittest

from src.services.analysis_service import analyze_message

class MyTestCase(unittest.TestCase):

    def test_analyze_message_with_url(self):
        result = analyze_message(
            "  URGENT!  Click here: https://example.com/login  "
        )

        self.assertEqual(
            result["cleaned_message"],
            "URGENT! Click here: https://example.com/login",
        )
        self.assertEqual(
            result["urls"],
            ["https://example.com/login"],
        )
        self.assertEqual(len(result["url_features"]), 1)
        self.assertTrue(result["url_features"][0]["uses_https"])

    def test_analyze_message_without_urls(self):
        result = analyze_message("Hello, how are you?")

        self.assertEqual(result["urls"], [])
        self.assertEqual(result["url_features"], [])

    def test_analyze_message_with_multiple_urls(self):
        result = analyze_message(
            "Visit https://one.example and https://two.example"
        )

        self.assertEqual(
            result["urls"],
            [
                "https://one.example",
                "https://two.example",
            ]
        )

        self.assertEqual(len(result["url_features"]), 2)

if __name__ == '__main__':
    unittest.main()
