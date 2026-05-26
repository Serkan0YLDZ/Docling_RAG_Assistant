from app.services.citation_sync import (
    append_sources_footer,
    extract_ref_indices,
    strip_invalid_refs,
)


def test_append_sources_footer_lists_all_citations_in_order():
    citations = [
        {"refIndex": 1, "page": 3, "section": "Bölüm 1"},
        {"refIndex": 2, "page": 5, "section": "Bölüm 2"},
        {"refIndex": 3, "page": 8},
        {"refIndex": 4, "page": 10},
    ]
    result = append_sources_footer("Cevap metni [1] ve [3].", citations)
    assert "**Kaynaklar:**" in result
    assert "[1] Sayfa 3" in result
    assert "[2] Sayfa 5" in result
    assert "[3] Sayfa 8" in result
    assert "[4] Sayfa 10" in result


def test_strip_invalid_refs_removes_unknown_numbers():
    text = "Bilgi [3] ve [9] kaynaklı."
    cleaned = strip_invalid_refs(text, {1, 2, 3})
    assert "[3]" in cleaned
    assert "[9]" not in cleaned


def test_extract_ref_indices_preserves_order():
    refs = extract_ref_indices("Önce [3] sonra [1] tekrar [3].")
    assert refs == [3, 1]
