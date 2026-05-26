import pytest

from app.infrastructure.gemini_retry import (
    call_with_quota_retry,
    is_quota_exhausted,
    quota_retry_delay_seconds,
)


def test_is_quota_exhausted():
    assert is_quota_exhausted(Exception("429 RESOURCE_EXHAUSTED quota"))
    assert not is_quota_exhausted(Exception("500 internal"))


def test_quota_retry_delay_parses_api_hint():
    exc = Exception("Please retry in 45.653554588s.")
    assert quota_retry_delay_seconds(exc, 0) == pytest.approx(47.65, rel=0.01)


def test_call_with_quota_retry_eventually_succeeds(monkeypatch):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("429 RESOURCE_EXHAUSTED retry in 0.01s")
        return "ok"

    monkeypatch.setattr(
        "app.infrastructure.gemini_retry.time.sleep",
        lambda _s: None,
    )
    assert call_with_quota_retry(flaky, max_retries=5, min_interval_sec=0) == "ok"
    assert calls["n"] == 3
