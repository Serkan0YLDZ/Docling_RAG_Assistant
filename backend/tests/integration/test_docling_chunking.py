from pathlib import Path

import pytest

from app.infrastructure.fake_chunk_enricher import FakeChunkEnricher
from app.infrastructure.noop_chunk_enricher import NoOpChunkEnricher
from app.services.header_footer_stripper import HeaderFooterStripper
from app.services.structural_chunker import StructuralChunker
from app.services.table_continuity_merger import TableContinuityMerger

pytestmark = pytest.mark.tc_chunk

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "documents"


def _run_post_pipeline(markdown: str, use_llm: bool = False) -> str:
    text = HeaderFooterStripper(min_repeats=2).strip(markdown)
    if use_llm:
        text = FakeChunkEnricher().enrich(text)
        text = HeaderFooterStripper(min_repeats=2).strip(text)
    return TableContinuityMerger().merge(text)


def test_tc_chunk_01_multicolumn_reading_order_preserved():
    raw = (FIXTURES / "multicolumn_order.md").read_text(encoding="utf-8")
    processed = _run_post_pipeline(raw)
    idx_intro = processed.find("Sol sütun")
    idx_method = processed.find("## Yöntem")
    idx_result = processed.find("Sonuç paragrafı")
    assert idx_intro < idx_method < idx_result


def test_tc_chunk_02_table_rows_stay_together():
    raw = (FIXTURES / "split_table.md").read_text(encoding="utf-8")
    processed = _run_post_pipeline(raw)
    assert "| 2024-Q1 | 100 | 40 |" in processed
    assert "| 2024-Q2 | 120 | 45 |" in processed
    blocks = StructuralChunker().split(processed)
    table_block = next((b for b in blocks if "| 2024-Q1" in b.text), None)
    assert table_block is not None
    assert "| 2024-Q2" in table_block.text


def test_tc_chunk_04_header_footer_with_llm_enricher():
    raw = (FIXTURES / "header_footer_noise.md").read_text(encoding="utf-8")
    processed = _run_post_pipeline(raw, use_llm=True)
    blocks = StructuralChunker().split(processed)
    sections = [b.section for b in blocks if b.section]
    assert "Doğru Bölüm Başlığı" in sections or any(
        "Doğru" in (s or "") for s in sections
    )
    assert not any(s and "Sayfa Üstbilgi" in s for s in sections)


@pytest.mark.slow
def test_docling_adapter_parses_txt_integration(tmp_path):
    """Gerçek Docling yolu: küçük TXT dosyası (USE_FAKE_DOCLING=0 ortamında)."""
    pytest.importorskip("docling")
    from app.infrastructure.docling_adapter import DoclingAdapter

    sample = tmp_path / "sample.txt"
    sample.write_text((FIXTURES / "multicolumn_order.md").read_text(), encoding="utf-8")
    adapter = DoclingAdapter()
    result = adapter.parse(sample, "text")
    assert result.markdown.strip()
    assert result.page_count >= 1
