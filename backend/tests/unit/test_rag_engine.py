from unittest.mock import MagicMock

import pytest

from app.domain.search_hit import SearchHit
from app.infrastructure.fake_llm import FakeLLM
from app.services.rag_engine import RAGEngine
from app.services.search_response_builder import SearchResponseBuilder


def _hit(text: str = "Ar-Ge yatırımları önemlidir.") -> SearchHit:
    return SearchHit(
        text=text,
        similarity=0.9,
        document_id="doc-1",
        document_name="rapor.txt",
        chunk_index=0,
        page=3,
        section="Bölüm 1",
    )


@pytest.mark.tc_rag
def test_tc_rag_02_no_context_skips_llm():
    pipeline = MagicMock()
    pipeline.retrieve_hits.return_value = []
    llm = MagicMock()
    engine = RAGEngine(pipeline, llm, SearchResponseBuilder())

    result = engine.generate("Bu konuda bilgi var mı?", None, [])

    llm.generate.assert_not_called()
    assert "bulunmamaktadır" in result["message"]["content"]
    assert result["sources"] == []


@pytest.mark.tc_rag
def test_tc_rag_01_calls_llm_with_context():
    pipeline = MagicMock()
    pipeline.retrieve_hits.return_value = [_hit()]
    llm = FakeLLM()
    engine = RAGEngine(pipeline, llm, SearchResponseBuilder())

    result = engine.generate(
        "Ar-Ge ne kadar önemli?",
        ["doc-1"],
        [{"role": "user", "content": "Önceki soru"}],
    )

    assert len(result["sources"]) == 1
    assert len(result["message"]["citations"]) == 1
    assert "**Kaynaklar:**" in result["message"]["content"]
    assert "[1] Sayfa 3" in result["message"]["content"]
