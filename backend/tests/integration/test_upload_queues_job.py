import io
import time

from app.services.document_service import DocumentService


def test_upload_starts_background_job(client, app):
    data = {"file": (io.BytesIO(b"sample content"), "job.txt")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    doc_id = response.get_json()["id"]

    service: DocumentService = app.extensions["document_service"]
    assert doc_id in service._jobs

    for _ in range(200):
        doc = service._store.get(doc_id)
        if doc.status == "ready":
            break
        if doc.status == "error":
            raise AssertionError("Belge işleme hatası")
        time.sleep(0.05)

    assert doc.status == "ready"
    assert doc.chunk_count > 0
    assert doc.progress == 100
