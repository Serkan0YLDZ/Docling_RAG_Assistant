import io
import time

import pytest

from app.domain.errors import NotFoundError
from app.services.document_service import DocumentService


@pytest.mark.tc_del
def test_tc_del_01_delete_removes_chroma_and_chunks(client, app):
    data = {"file": (io.BytesIO(b"cascade delete test document body."), "del.txt")}
    response = client.post(
        "/api/documents",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    doc_id = response.get_json()["id"]

    service: DocumentService = app.extensions["document_service"]
    vector_store = app.extensions["vector_store"]
    chunk_store = service._chunk_store

    for _ in range(200):
        doc = service._store.get(doc_id)
        if doc.status == "ready":
            break
        if doc.status == "error":
            raise AssertionError("İşleme hatası")
        time.sleep(0.05)

    assert vector_store.count_by_document(doc_id) > 0
    assert chunk_store.exists(doc_id)

    delete_resp = client.delete(f"/api/documents/{doc_id}")
    assert delete_resp.status_code == 204
    assert vector_store.count_by_document(doc_id) == 0
    assert not chunk_store.exists(doc_id)

    with pytest.raises(NotFoundError):
        service._store.get(doc_id)
