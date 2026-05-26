import io

import pytest


def _upload_txt(client, name: str, content: bytes) -> str:
    data = {"file": (io.BytesIO(content), name)}
    resp = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


@pytest.mark.tc_doc
def test_document_file_returns_inline_content(client):
    doc_id = _upload_txt(client, "sample.txt", b"Ar-Ge yatirim ozeti 2024.\n")
    file_resp = client.get(f"/api/documents/{doc_id}/file")
    assert file_resp.status_code == 200
    assert "text/plain" in file_resp.content_type
    assert b"Ar-Ge" in file_resp.data


@pytest.mark.tc_doc
def test_document_file_not_found(client):
    resp = client.get("/api/documents/nonexistent-id/file")
    assert resp.status_code == 404


@pytest.mark.tc_doc
def test_document_file_deleted_returns_404(client):
    doc_id = _upload_txt(client, "gone.txt", b"temp")
    assert client.delete(f"/api/documents/{doc_id}").status_code == 204
    assert client.get(f"/api/documents/{doc_id}/file").status_code == 404
