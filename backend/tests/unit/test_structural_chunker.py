import pytest

from app.services.structural_chunker import StructuralChunker

pytestmark = pytest.mark.tc_chunk


def test_tc_chunk_03_splits_by_headings():
    markdown = """# Bölüm A

Paragraf açıklaması A.

## Alt Bölüm B

Paragraf B içeriği.
"""
    blocks = StructuralChunker().split(markdown)
    sections = [b.section for b in blocks]
    assert "Bölüm A" in sections
    assert "Alt Bölüm B" in sections
    assert all(b.text.strip() for b in blocks)
