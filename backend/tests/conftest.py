import pytest
from pathlib import Path

from app import create_app
from app.config import Config


class TestConfig(Config):
    """İzole test dizinleri."""

    TESTING = True
    # DeterministicEmbedding: örtüşen sorgu–chunk ~0.65–0.70; gerçek Gemini ≥0.75
    SIMILARITY_THRESHOLD = 0.65
    UPLOAD_DIR = Path("data/test_uploads")
    REGISTRY_PATH = Path("data/test_documents.json")


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Her test için temiz upload ve registry."""
    monkeypatch.setenv("USE_FAKE_DOCLING", "1")
    cfg = TestConfig()
    cfg.UPLOAD_DIR = tmp_path / "uploads"
    cfg.REGISTRY_PATH = tmp_path / "documents.json"
    cfg.CHUNKS_DIR = tmp_path / "chunks"
    cfg.CHROMA_PATH = tmp_path / "chroma"

    application = create_app(cfg)
    application.config["TESTING"] = True
    yield application

    service = application.extensions["document_service"]
    for thread in list(service._jobs.values()):
        if thread.is_alive():
            thread.join(timeout=2)

    import shutil

    if cfg.UPLOAD_DIR.exists():
        shutil.rmtree(cfg.UPLOAD_DIR, ignore_errors=True)
    if cfg.REGISTRY_PATH.exists():
        cfg.REGISTRY_PATH.unlink(missing_ok=True)
    if cfg.CHROMA_PATH.exists():
        shutil.rmtree(cfg.CHROMA_PATH, ignore_errors=True)


@pytest.fixture
def client(app):
    """Flask test istemcisi."""
    return app.test_client()
