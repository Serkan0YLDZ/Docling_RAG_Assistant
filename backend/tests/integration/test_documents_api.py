import io
import time

import pytest

from app.config import Config
from app.constants import messages


@pytest.mark.tc_doc
def test_upload_list_delete_txt(client):
    content = ("# Rapor\n\n" + "analiz kelimesi " * 80).encode("utf-8")
    data = {
        "file": (io.BytesIO(content), "Q3_Report.txt"),
    }
    upload = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert upload.status_code == 201
    body = upload.get_json()
    assert body["name"] == "Q3_Report.txt"
    assert body["mimeKind"] == "text"
    assert "id" in body
    assert body["sizeLabel"]

    listed = client.get("/api/documents")
    assert listed.status_code == 200
    ids = [d["id"] for d in listed.get_json()]
    assert body["id"] in ids

    for _ in range(100):
        status = client.get(f"/api/documents/{body['id']}/status").get_json()
        if status["status"] == "ready":
            break
        time.sleep(0.05)

    deleted = client.delete(f"/api/documents/{body['id']}")
    assert deleted.status_code == 204

    listed_after = client.get("/api/documents")
    assert body["id"] not in [d["id"] for d in listed_after.get_json()]


@pytest.mark.tc_doc
def test_tc_doc_01_api_empty_file(client):
    data = {"file": (io.BytesIO(b""), "empty.pdf")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == messages.EMPTY_FILE


@pytest.mark.tc_doc
def test_tc_doc_04_api_oversized_file(client):
    oversized = b"x" * (Config.MAX_UPLOAD_BYTES + 1)
    data = {"file": (io.BytesIO(oversized), "big.pdf")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
    assert response.get_json()["error"] == messages.MAX_FILE_SIZE


@pytest.mark.tc_fmt
def test_tc_fmt_01_api_invalid_extension(client):
    data = {"file": (io.BytesIO(b"text"), "virus.exe")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == messages.INVALID_EXTENSION


def test_document_status_endpoint(client):
    data = {"file": (io.BytesIO(b"hello"), "notes.txt")}
    upload = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    doc_id = upload.get_json()["id"]

    for _ in range(100):
        status = client.get(f"/api/documents/{doc_id}/status")
        assert status.status_code == 200
        payload = status.get_json()
        if payload["status"] == "ready":
            assert payload["progress"] == 100
            listed = client.get("/api/documents").get_json()
            doc = next(d for d in listed if d["id"] == doc_id)
            assert doc["chunkCount"] > 0
            break
        if payload["status"] == "error":
            pytest.fail("Belge işleme hatası")
        time.sleep(0.05)
    else:
        pytest.fail("Belge ready durumuna geçmedi")
