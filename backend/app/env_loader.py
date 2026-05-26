from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]


def load_repo_env() -> Path:
    """Proje kökündeki .env dosyasını yükler."""
    load_dotenv(_REPO_ROOT / ".env")
    return _REPO_ROOT
