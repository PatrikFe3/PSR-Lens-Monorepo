from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = ARTIIFACTS_DIR / "models"

MODELS_DIR.mkdir(parents=True, exist_ok=True)