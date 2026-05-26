import pytest

from app.services.recursive_splitter import RecursiveSplitter
from app.services.structural_chunker import TextBlock
from app.services.token_utils import estimate_tokens

pytestmark = pytest.mark.tc_rec


def _words(count: int) -> str:
    return " ".join(f"w{i}" for i in range(count))


@pytest.mark.tc_rec
def test_tc_rec_01_under_limit_single_chunk():
    text = _words(500)
    parts = RecursiveSplitter(max_tokens=512)._split_text(text)
    assert len(parts) == 1


@pytest.mark.tc_rec
def test_tc_rec_02_exact_limit_single_chunk():
    text = _words(512)
    parts = RecursiveSplitter(max_tokens=512)._split_text(text)
    assert len(parts) == 1


@pytest.mark.tc_rec
def test_tc_rec_03_over_limit_splits():
    text = _words(600)
    parts = RecursiveSplitter(max_tokens=512, overlap_ratio=0.0)._split_text(text)
    assert len(parts) >= 2


@pytest.mark.tc_rec
def test_tc_rec_04_overlap_between_chunks():
    text = _words(600)
    splitter = RecursiveSplitter(max_tokens=512, overlap_ratio=0.15)
    parts = splitter._split_text(text)
    assert len(parts) >= 2
    overlap_tokens = int(512 * 0.15)
    tail_words = parts[0].split()[-overlap_tokens:]
    head_words = parts[1].split()[: overlap_tokens + 5]
    assert any(word in head_words for word in tail_words)
