import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # python-dotenv is optional: settings still work without it.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str, *aliases: str) -> str:
    for key in (name, *aliases):
        value = os.getenv(key)
        if value:
            return value
    return default


@dataclass(frozen=True)
class Settings:
    catalog_dir: Path = field(
        default_factory=lambda: Path(_env('PSR_CATALOG_DIR', str(BACKEND_ROOT / 'catalogs'))))
    output_dir: Path = field(
        default_factory=lambda: Path(_env('PSR_OUTPUT_DIR', str(BACKEND_ROOT / 'artifacts' / 'designs'))))
    default_printer: str = field(default_factory=lambda: _env('PSR_PRINTER', 'prusa_mk4s'))
    default_material: str = field(default_factory=lambda: _env('PSR_MATERIAL', 'pla'))
    kernel: str = field(default_factory=lambda: _env('PSR_KERNEL', 'auto'))
    ollama_host: str = field(default_factory=lambda: _env('OLLAMA_HOST', 'http://localhost:11434'))
    ollama_model: str = field(default_factory=lambda: _env('OLLAMA_MODEL', 'qwen3:4b-instruct'))
    # ``TIMEOUT`` is accepted too, because the original .env used that name.
    ollama_timeout: float = field(
        default_factory=lambda: float(_env('OLLAMA_TIMEOUT', '120', 'TIMEOUT')))


def get_settings() -> Settings:
    return Settings()