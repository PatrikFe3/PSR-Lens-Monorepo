"""
Ther will be documentation!
"""
import re
from urllib.parse import urlparse
import ipaddress

MARKDOWN_URL_PATTERN = re.compile(
    r'\[[^\]]*\]\((?P<markdown>https?://[^)\s]+)\)',
    re.IGNORECASE,
)

URL_PATTERN = re.compile(
    r"""https?://[^\s<>"')\]]+""",
    re.IGNORECASE,
)


def url_extraction(text: str) -> list[str]:
    urls = []
    last_position = 0

    for match in MARKDOWN_URL_PATTERN.finditer(text):
        plain_text = text[last_position:match.start()]

        urls.extend(
            url.rstrip(".,;:!?)}]")
            for url in URL_PATTERN.findall(plain_text)
        )

        url = match.group("markdown").rstrip(".,;:!?")
        urls.append(url)

        last_position = match.end()

    remaining_text = text[last_position:]

    urls.extend(
        url.rstrip(".,;:!?)}]")
        for url in URL_PATTERN.findall(remaining_text)
    )
    return urls


def analyze_url(url: str) -> dict:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    uses_https = parsed_url.scheme.lower() == "https"

    is_ip_address = False

    if hostname:
        try:
            ipaddress.ip_address(hostname)
            is_ip_address = True
        except ValueError:
            pass
    # This returned dictionary is later considered as features,
    # that are later important for Machine Learning
    return {
        "url": url,
        "uses_https": uses_https,
        "is_ip_address": is_ip_address,
        "has_username": parsed_url.username is not None,
        "url_length": len(url),
        "hostname_length": len(hostname) if hostname else 0,
        "path_length": len(parsed_url.path),
        "has_at_symbol": "@" in url,
    }
