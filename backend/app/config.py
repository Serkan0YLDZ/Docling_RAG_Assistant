import os
from pathlib import Path

from app.constants.embedding import GEMINI_EMBEDDING_MODEL

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _resolve_data_path(env_value: str | None, default: Path) -> Path:
    """Göreli yolları backend köküne göre mutlak yapar (cwd'den bağımsız)."""
    if env_value is None or not str(env_value).strip():
        return default.resolve()
    path = Path(env_value)
    if path.is_absolute():
        return path.resolve()
    return (_BACKEND_ROOT / path).resolve()


class Config:
    """Uygulama yapılandırması."""

    API_HOST = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT = int(os.environ.get("API_PORT", "5000"))
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() in (
        "1",
        "true",
        "yes",
    )

    _backend_root = _BACKEND_ROOT

    UPLOAD_DIR = _resolve_data_path(
        os.environ.get("UPLOAD_DIR"),
        _BACKEND_ROOT / "data" / "uploads",
    )
    REGISTRY_PATH = _resolve_data_path(
        os.environ.get("REGISTRY_PATH"),
        _BACKEND_ROOT / "data" / "documents.json",
    )
    MAX_UPLOAD_BYTES = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = frozenset({"pdf", "docx", "txt"})
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    CHUNKS_DIR = _resolve_data_path(
        os.environ.get("CHUNKS_DIR"),
        _BACKEND_ROOT / "data" / "chunks",
    )
    CHUNK_MAX_TOKENS = int(os.environ.get("CHUNK_MAX_TOKENS", "512"))
    CHUNK_OVERLAP_RATIO = float(os.environ.get("CHUNK_OVERLAP_RATIO", "0.15"))
    DOCLING_NUM_THREADS = int(os.environ.get("DOCLING_NUM_THREADS", "4"))

    CHROMA_PATH = _resolve_data_path(
        os.environ.get("CHROMA_PATH"),
        _BACKEND_ROOT / "data" / "chroma",
    )
    CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "rag_chunks")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_EMBEDDING_MODEL = GEMINI_EMBEDDING_MODEL
    EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "32"))
    EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", "768"))
    # Ücretsiz katman ~100 istek/dk; istekler arası minimum aralık (sn)
    EMBEDDING_MIN_INTERVAL_SEC = float(
        os.environ.get("EMBEDDING_MIN_INTERVAL_SEC", "0.7")
    )
    EMBEDDING_MAX_RETRIES = int(os.environ.get("EMBEDDING_MAX_RETRIES", "8"))
    GEMINI_LLM_MODEL = os.environ.get("GEMINI_LLM_MODEL", "gemini-2.0-flash")
    ENABLE_LLM_CHUNK_ENRICHMENT = os.environ.get(
        "ENABLE_LLM_CHUNK_ENRICHMENT", "false"
    ).lower() in ("1", "true", "yes")
    LLM_ENRICH_MAX_CHARS = int(os.environ.get("LLM_ENRICH_MAX_CHARS", "24000"))

    QUERY_MIN_LENGTH = int(os.environ.get("QUERY_MIN_LENGTH", "10"))
    QUERY_MAX_LENGTH = int(os.environ.get("QUERY_MAX_LENGTH", "500"))
    SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.5"))
    RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "5"))
    RAG_TEMPERATURE = float(os.environ.get("RAG_TEMPERATURE", "0.2"))
    RAG_MAX_HISTORY_TURNS = int(os.environ.get("RAG_MAX_HISTORY_TURNS", "10"))

    TESTING = False
