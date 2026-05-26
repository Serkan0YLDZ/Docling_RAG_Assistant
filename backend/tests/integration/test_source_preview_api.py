import io
import time

import pytest


def _upload_ready_txt(client, text: str, name: str = "src.txt") -> str:
    upload = client.post(
        "/api/documents",
        data={"file": (io.BytesIO(text.encode()), name)},
        content_type="multipart/form-data",
    )
    doc_id = upload.get_json()["id"]
    for _ in range(200):
        st = client.get(f"/api/documents/{doc_id}/status").get_json()
        if st["status"] == "ready":
            return doc_id
        time.sleep(0.05)
    raise AssertionError("ready timeout")


def test_source_preview_by_ref(client):
    doc_id = _upload_ready_txt(
        client,
        "# Bölüm\n\nKaynak cümlesi burada görünür.",
    )
    for ref in range(0, 5):
        preview = client.get(f"/api/documents/{doc_id}/source?ref={ref}")
        if preview.status_code != 200:
            continue
        body = preview.get_json()
        if "Kaynak cümlesi" in body.get("highlightText", ""):
            assert body["documentId"] == doc_id
            return
    pytest.fail("Kaynak metni chunk bulunamadı")
