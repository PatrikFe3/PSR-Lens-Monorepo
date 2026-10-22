from preprocessing.feature_extractor import url_extraction

test_cases = [
    "Visit https://example.com/login.",
    "Click (https://example.com/login).",
    "Link: https://example.com/login, please.",
    "URL: https://example.com/login",
]

for text in test_cases:
    result = url_extraction(text)

    print(f"Input: {text}")
    print(f"Output: {result}")
    print("-" * 40)
