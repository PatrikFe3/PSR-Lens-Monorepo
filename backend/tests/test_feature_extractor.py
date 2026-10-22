import unittest
from src.preprocessing.feature_extractor import (
    url_extraction,
    analyze_url,
)


class FeatureExtractorTestCase(unittest.TestCase):
    def test_markdown_links(self):
        text = "Click [Login](https://example.com/login)"

        self.assertEqual(
            url_extraction(text),
            ["https://example.com/login"],
        )

    def test_url_training_punctuation(self):
        text = "Visit https://example.com/login"

        self.assertEqual(
            url_extraction(text),
            ["https://example.com/login"],
        )

    def test_multiple_markdown_links(self):
        text = (
            "Visit [One](https://one.example) and "
            "[Two](https://two.example)"
        )

        self.assertEqual(
            url_extraction(text),
            [
                "https://one.example",
                "https://two.example",
            ]
        )

    def test_mixed_markdown_plain_urls(self):
        text = (
            "Visit [Login](https://login.example) "
            "or https://help.example."
        )

        self.assertEqual(
            url_extraction(text),
            [
                "https://login.example",
                "https://help.example",
            ]
        )

    def test_no_urls(self):
        self.assertEqual(
            url_extraction("This message contains no links."),
            [],
        )

    def test_empty_text(self):
        self.assertEqual(
            url_extraction(""), []
        )

    def test_analyze_https_url(self):
        result = analyze_url("https://example.com/login")

        self.assertTrue(result["uses_https"])
        self.assertFalse(result["is_ip_address"])
        self.assertFalse(result["has_username"])

    def test_analyze_ip_url(self):
        result = analyze_url("http://192.0.2.1/login")

        self.assertFalse(result["uses_https"])
        self.assertTrue(result["is_ip_address"])

    def test_analyze_url_with_username(self):
        result = analyze_url("https://trusted.example@malicious.example/login")

        self.assertTrue(result["has_username"])

    def test_analyze_url_length(self):
        url = "https://www.example.com/login"
        result = analyze_url(url)

        self.assertEqual(result["url_length"], len(url))

    def test_analyze_url_dimensions(self):
        result = analyze_url("https://example.com/login")

        self.assertEqual(result["hostname_length"], len("example.com"))
        self.assertEqual(result["path_length"], len("/login"))
        self.assertFalse(result["has_at_symbol"])

if __name__ == '__main__':
    unittest.main()
