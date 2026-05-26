import pytest

from app.services.table_continuity_merger import TableContinuityMerger

pytestmark = pytest.mark.tc_chunk


def test_tc_chunk_02_merges_split_table_blocks():
    raw = """| A | B |
|---|---|

| 1 | 2 |
| 3 | 4 |"""
    merged = TableContinuityMerger().merge(raw)
    data_rows = [
        line
        for line in merged.splitlines()
        if line.strip().startswith("|") and "---" not in line
    ]
    assert len(data_rows) >= 3
    assert "| 1 | 2 |" in merged
    assert "| 3 | 4 |" in merged


def test_removes_blank_lines_between_table_rows():
    text = "| x |\n\n| y |"
    merged = TableContinuityMerger().merge(text)
    assert "\n\n" not in merged or merged.count("|") >= 2
