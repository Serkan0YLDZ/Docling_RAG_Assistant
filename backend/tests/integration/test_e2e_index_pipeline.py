import io
import time

from app.services.document_service import DocumentService


def test_upload_parse_index_ready(client, app):
    data = {"file": (io.BytesIO(b"RAG test content for indexing pipeline."), "index.txt")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    doc_id = response.get_json()["id"]

    service: DocumentService = app.extensions["document_service"]
    vector_store = app.extensions["vector_store"]

    for _ in range(200):
        doc = service._store.get(doc_id)
        if doc.status == "ready":
            break
        if doc.status == "error":
            raise AssertionError("Belge işleme/indeksleme hatası")
        time.sleep(0.05)

    assert doc.status == "ready"
    assert doc.chunk_count > 0
    assert doc.progress == 100
    assert vector_store.count_by_document(doc_id) == doc.chunk_count
