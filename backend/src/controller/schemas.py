from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=20000,
        description="Message to analyze.",
    )

class UrlFeatures(BaseModel):
    url: str
    uses_https: bool
    is_ip_address: bool
    has_username: bool
    url_length: int
    hostname_length: int
    path_length: int
    has_at_symbol: bool

class AnalysisResponse(BaseModel):
    cleaned_message: str
    message_length: int
    urls: list[str]
    url_features: list[UrlFeatures]