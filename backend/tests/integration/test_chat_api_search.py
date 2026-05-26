import io
import time

import pytest

from app.constants import messages

pytestmark = pytest.mark.tc_qry


def _wait_ready(client, doc_id: str) -> None:
    for _ in range(200):
        status = client.get(f"/api/documents/{doc_id}/status").get_json()
        if status["status"] == "ready":
            return
        if status["status"] == "error":
            raise AssertionError("Belge hazır değil")
        time.sleep(0.05)
    raise AssertionError("Timeout")


def test_chat_query_after_indexing(client):
    content = (
        "# Finans Raporu\n\n"
        "Ar-Ge yatırımları şirketin en büyük harcama kalemidir. "
        "Detaylar üçüncü çeyrek tablosunda yer alır.\n"
    ).encode()
    upload = client.post(
        "/api/documents",
        data={"file": (io.BytesIO(content), "finans.txt")},
        content_type="multipart/form-data",
    )
    assert upload.status_code == 201
    doc_id = upload.get_json()["id"]
    _wait_ready(client, doc_id)

    response = client.post(
        "/api/chat/query",
        json={
            "message": "Ar-Ge yatırımları ne kadar önemli?",
            "documentIds": [doc_id],
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"]["role"] == "assistant"
    assert "sources" in body

    messages = client.get("/api/chat/messages").get_json()
    assert len(messages) >= 2


def test_chat_query_too_short_400(client):
    response = client.post(
        "/api/chat/query",
        json={"message": "kısa"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == messages.QUERY_TOO_SHORT


def test_chat_query_too_long_400(client):
    response = client.post(
        "/api/chat/query",
        json={"message": "x" * 501},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == messages.QUERY_TOO_LONG
