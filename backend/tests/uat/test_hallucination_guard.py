from unittest.mock import MagicMock

import pytest

from app.services.rag_engine import RAGEngine
from app.services.search_response_builder import SearchResponseBuilder

pytestmark = pytest.mark.tc_uat


@pytest.mark.tc_uat
def test_tc_uat_01_out_of_scope_skips_llm(app, uat_doc_id):
    """Belge dışı soru → LLM çağrılmaz (halüsinasyon koruması)."""
    pipeline = app.extensions["query_pipeline"]
    llm = MagicMock()
    engine = RAGEngine(pipeline, llm, SearchResponseBuilder())

    result = engine.generate(
        "Mars kolonisi icin ayrilan butce ne kadar?",
        [uat_doc_id],
        [],
    )

    llm.generate.assert_not_called()
    assert "bulunmamaktadır" in result["message"]["content"].lower()
