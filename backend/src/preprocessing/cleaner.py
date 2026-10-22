"""
line_endings_normalize() => Unifies line endings.
whitespace_normalize() => Adjusts excess spaces and tabs, but preserves line breaks.
blank_lines_normalize() => Removes excess empty lines.
clean_text(text) => Joins all steps to one.
"""

import re

def line_endings_normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")

def whitespace_normalize(text: str) -> str:
    lines = [
        re.sub(r"[^\S\n]+", " ", line).strip()
        for line in text.split("\n")
    ]
    return "\n".join(lines)

def blank_lines_normalize(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def clean_text(text: str) -> str:
    text = line_endings_normalize(text)
    text = whitespace_normalize(text)
    text = blank_lines_normalize(text)
    return text
