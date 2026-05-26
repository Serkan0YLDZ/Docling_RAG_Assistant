import pytest

from app.domain.document import Document
from app.domain.errors import NotFoundError
from app.services.file_store import FileStore


def test_save_and_list_document(tmp_path):
    store = FileStore(tmp_path / "uploads", tmp_path / "registry.json")
    doc = Document(name="test.pdf", size_bytes=1200, mime_kind="pdf")
    store.save_file(doc, b"%PDF-1.4 sample")

    listed = store.list_documents()
    assert len(listed) == 1
    assert listed[0].id == doc.id
    assert listed[0].name == "test.pdf"


def test_delete_removes_record_and_files(tmp_path):
    store = FileStore(tmp_path / "uploads", tmp_path / "registry.json")
    doc = Document(name="remove.txt", size_bytes=10, mime_kind="text")
    store.save_file(doc, b"hello")
    store.delete(doc.id)

    assert store.list_documents() == []
    with pytest.raises(NotFoundError):
        store.get(doc.id)
