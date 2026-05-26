from unittest.mock import MagicMock

import pytest

from app.domain.errors import NotFoundError
from app.services.document_service import DocumentService


def _service_with_mocks():
    store = MagicMock()
    store.get.return_value = MagicMock(id="doc-x")
    chunk_store = MagicMock()
    chunk_store.exists.side_effect = [True, False]
    vector_store = MagicMock()
    vector_store.count_by_document.side_effect = [3, 0]
    indexing = MagicMock()
    indexing.vector_store = vector_store
    service = DocumentService(
        store=store,
        validator=MagicMock(),
        processor=MagicMock(),
        chunk_store=chunk_store,
        indexing_service=indexing,
    )
    return service, store, chunk_store, vector_store


def test_delete_purges_chroma_then_chunks_then_registry():
    service, store, chunk_store, vector_store = _service_with_mocks()

    service.delete("doc-x")

    vector_store.delete_by_document.assert_called_once_with("doc-x")
    chunk_store.delete.assert_called_once_with("doc-x")
    store.delete.assert_called_once_with("doc-x")
    assert "doc-x" not in service._cancelled


def test_delete_raises_if_chroma_vectors_remain():
    service, store, chunk_store, vector_store = _service_with_mocks()
    vector_store.count_by_document.side_effect = [2, 1]

    with pytest.raises(RuntimeError, match="Chroma"):
        service.delete("doc-x")

    chunk_store.delete.assert_not_called()
    store.delete.assert_not_called()


def test_delete_raises_if_chunk_file_remains():
    service, store, chunk_store, vector_store = _service_with_mocks()
    chunk_store.exists.side_effect = [True, True]

    with pytest.raises(RuntimeError, match="Chunk"):
        service.delete("doc-x")

    store.delete.assert_not_called()
