"""Request / response bodies of the design API."""
from pydantic import BaseModel, Field

from src.core.spec import DesignSpec


class BuildRequest(BaseModel):
    spec: DesignSpec
    printer: str | None = None
    material: str | None = None


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    printer: str | None = None
    material: str | None = None
    ask_user: bool = True


class BuildResponse(BaseModel):
    design_id: str
    manifest: dict
    plates: dict
    files: list[str]
    warnings: list[dict]