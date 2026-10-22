import unittest
from src.preprocessing.cleaner import (
    line_endings_normalize,
    whitespace_normalize,
    blank_lines_normalize,
    clean_text,
)

class TestCleaner(unittest.TestCase):

    def test_line_endings_normalize(self):
        self.assertEqual(
            line_endings_normalize('Hello\r\nWorld\rAgain'),
            'Hello\nWorld\nAgain'
        )

    def test_whitespace_normalize(self):
        self.assertEqual(
            whitespace_normalize('    Your       account\tis locked    '),
            'Your account is locked',
        )

    def test_whitespace_normalize_preserves_line_breaks(self):
        self.assertEqual(
            whitespace_normalize('Hello       World\nNext\tline'),
            'Hello World\nNext line',
        )

    def test_blank_lines_normalize(self):
        self.assertEqual(
            blank_lines_normalize('Hello\n\n\n\nWorld'),
            'Hello\n\nWorld',
        )

    def test_clean_text(self):
        message = (
            "URGENT!    Your   account is locked.\r\n"
            "\r\n\r\n"
            "Click here: https://example.com/login   "
        )
        expected = (
            "URGENT! Your account is locked.\n\n"
            "Click here: https://example.com/login"
        )

        self.assertEqual(clean_text(message), expected)

    def test_clean_text_preserves_punctuation_and_case(self):
        message = "URGENT!!! Verify your password NOW!"
        self.assertEqual(clean_text(message), message)

    def test_clean_text_handles_empty_string(self):
        self.assertEqual(clean_text(""), "")

    def test_clean_text_handles_whitespace_only(self):
        self.assertEqual(clean_text("  \t \n   "), "")

if __name__ == '__main__':
    unittest.main()
