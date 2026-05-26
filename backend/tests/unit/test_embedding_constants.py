from app.constants.embedding import (
    GEMINI_EMBEDDING_MODEL,
    gemini_embedding_api_model,
    gemini_embedding_model_id,
)


def test_default_embedding_model_is_gemini_embedding_2(monkeypatch):
    monkeypatch.delenv("GEMINI_EMBEDDING_MODEL", raising=False)
    assert gemini_embedding_model_id() == "gemini-embedding-2"
    assert gemini_embedding_api_model() == "models/gemini-embedding-2"


def test_env_overrides_embedding_model(monkeypatch):
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
    assert gemini_embedding_model_id() == "gemini-embedding-2"


def test_module_constant_matches_model_id():
    assert GEMINI_EMBEDDING_MODEL == gemini_embedding_model_id()
