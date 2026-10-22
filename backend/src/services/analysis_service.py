from src.preprocessing.cleaner import clean_text
from src.preprocessing.feature_extractor import (
    url_extraction,
    analyze_url,
)

def analyze_message(message: str) -> dict:
    cleaned_message = clean_text(message)

    urls = url_extraction(cleaned_message)

    url_features = [
        analyze_url(url)
        for url in urls
    ]

    return {
        "cleaned_message": cleaned_message,
        "message_length": len(cleaned_message),
        "urls": urls,
        "url_features": url_features,
    }