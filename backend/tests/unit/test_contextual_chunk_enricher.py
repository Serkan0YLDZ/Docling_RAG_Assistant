import pytest

from app.infrastructure.fake_chunk_enricher import FakeChunkEnricher

pytestmark = pytest.mark.tc_ctx


def test_tc_ctx_01_fixes_wrong_section_title():
    raw = """# Rapor

## WRONG_SECTION_TITLE

Metin gövdesi.
"""
    enriched = FakeChunkEnricher().enrich(raw)
    assert "WRONG_SECTION_TITLE" not in enriched
    assert "Doğru Bölüm Başlığı" in enriched


def test_tc_ctx_02_removes_page_header_as_section():
    raw = """## Sayfa Üstbilgi

# Gerçek Başlık

İçerik.
"""
    enriched = FakeChunkEnricher().enrich(raw)
    assert "Sayfa Üstbilgi" not in enriched
    assert "Gerçek Başlık" in enriched
