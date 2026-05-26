import os

from app.env_loader import load_repo_env

load_repo_env()

_DEFAULT_MODEL = "gemini-embedding-2"


def gemini_embedding_model_id() -> str:
    """models/ öneki olmadan model kimliği."""
    raw = os.environ.get("GEMINI_EMBEDDING_MODEL", _DEFAULT_MODEL).strip()
    return raw or _DEFAULT_MODEL


def gemini_embedding_api_model() -> str:
    """Gemini embed_content için tam model yolu."""
    model_id = gemini_embedding_model_id()
    return model_id if model_id.startswith("models/") else f"models/{model_id}"


GEMINI_EMBEDDING_MODEL = gemini_embedding_model_id()
