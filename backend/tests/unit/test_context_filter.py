import pytest

from app.domain.search_hit import SearchHit
from app.services.context_filter import ContextFilter

pytestmark = pytest.mark.tc_sim

filter_ = ContextFilter(threshold=0.75)


def _hit(sim: float) -> SearchHit:
    return SearchHit(
        text="örnek",
        similarity=sim,
        document_id="d1",
        document_name="doc.pdf",
        chunk_index=0,
    )


def test_tc_sim_01_below_threshold_rejected():
    assert filter_.apply([_hit(0.74)]) == []


def test_tc_sim_02_at_threshold_accepted():
    result = filter_.apply([_hit(0.75)])
    assert len(result) == 1


def test_tc_sim_03_nominal_accepted():
    assert len(filter_.apply([_hit(0.85)])) == 1


def test_tc_sim_04_high_accepted():
    assert len(filter_.apply([_hit(0.99)])) == 1
