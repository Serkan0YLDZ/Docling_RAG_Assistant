import os

import pytest

from app.constants.embedding import gemini_embedding_api_model
from app.infrastructure.gemini_embedding import GeminiEmbedding


@pytest.mark.gemini_live
def test_gemini_embed_two_texts_consistent_dimension():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        pytest.skip("GEMINI_API_KEY yok")

    emb = GeminiEmbedding(api_key=api_key)
    assert emb._model == gemini_embedding_api_model()
    vectors = emb.embed(["similar topic about finance", "different topic about cooking"])
    assert len(vectors) == 2
    assert len(vectors[0]) == len(vectors[1])
    assert len(vectors[0]) > 0
