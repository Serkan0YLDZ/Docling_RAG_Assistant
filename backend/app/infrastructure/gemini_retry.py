import logging
import re
import time
from collections.abc import Callable
from typing import TypeVar

_log = logging.getLogger(__name__)

T = TypeVar("T")

_RETRY_IN_RE = re.compile(r"retry in ([\d.]+)s", re.IGNORECASE)


def is_quota_exhausted(exc: BaseException) -> bool:
    text = str(exc).upper()
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "QUOTA" in text


def quota_retry_delay_seconds(exc: BaseException, attempt: int) -> float:
    """API RetryInfo veya üstel bekleme süresi (saniye)."""
    match = _RETRY_IN_RE.search(str(exc))
    if match:
        return float(match.group(1)) + 2.0
    return min(120.0, 45.0 + attempt * 15.0)


def call_with_quota_retry(
    fn: Callable[[], T],
    *,
    max_retries: int = 8,
    min_interval_sec: float = 0.0,
    last_request_at: list[float] | None = None,
    label: str = "Gemini API",
) -> T:
    """429 kota hatalarında RetryInfo süresi kadar bekleyip yeniden dener."""
    if last_request_at is not None and min_interval_sec > 0:
        elapsed = time.monotonic() - last_request_at[0]
        if elapsed < min_interval_sec:
            time.sleep(min_interval_sec - elapsed)

    last_exc: BaseException | None = None
    for attempt in range(max_retries):
        try:
            result = fn()
            if last_request_at is not None:
                last_request_at[0] = time.monotonic()
            return result
        except Exception as exc:
            last_exc = exc
            if not is_quota_exhausted(exc) or attempt >= max_retries - 1:
                raise
            delay = quota_retry_delay_seconds(exc, attempt)
            _log.warning(
                "%s kota aşıldı; %.0f sn sonra yeniden denenecek (%d/%d)",
                label,
                delay,
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)

    assert last_exc is not None
    raise last_exc
