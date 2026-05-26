import pytest

from app.services.header_footer_stripper import HeaderFooterStripper

pytestmark = pytest.mark.tc_chunk


def test_tc_chunk_04_strips_repeated_header_lines():
    text = "\n".join(
        ["Kurumsal Rapor 2024", "İçerik paragrafı bir.", "Kurumsal Rapor 2024"]
        + ["Ara metin satırı."]
        + ["Kurumsal Rapor 2024", "Son paragraf."]
    )
    cleaned = HeaderFooterStripper(min_repeats=3).strip(text)
    assert cleaned.count("Kurumsal Rapor 2024") == 0
    assert "İçerik paragrafı bir." in cleaned
    assert "Son paragraf." in cleaned
