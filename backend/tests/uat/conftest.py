import io
import json
import time
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "uat"


@pytest.fixture
def uat_cases() -> list[dict]:
    raw = json.loads((FIXTURES / "cases.json").read_text(encoding="utf-8"))
    return raw["cases"]


@pytest.fixture
def uat_doc_id(client):
    """UAT corpus yüklenir ve indekslenene kadar beklenir."""
    corpus = (FIXTURES / "corpus.txt").read_bytes()
    resp = client.post(
        "/api/documents",
        data={"file": (io.BytesIO(corpus), "uat_corpus.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 201
    doc_id = resp.get_json()["id"]
    for _ in range(200):
        resp = client.get(f"/api/documents/{doc_id}/status")
        status = resp.get_json() or {}
        state = status.get("status")
        if state == "ready":
            return doc_id
        if state == "error":
            raise AssertionError(f"UAT corpus indekslenemedi: {status}")
        if resp.status_code >= 400:
            raise AssertionError(f"status HTTP {resp.status_code}: {status}")
        time.sleep(0.05)
    raise AssertionError("UAT corpus timeout")
