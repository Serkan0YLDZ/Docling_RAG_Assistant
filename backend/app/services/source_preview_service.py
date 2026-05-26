from app.domain.errors import NotFoundError
from app.services.chunk_store import ChunkStore
from app.services.file_store import FileStore


class SourcePreviewService:
    """Chunk store'dan kaynak önizlemesi üretir."""

    def __init__(self, store: FileStore, chunk_store: ChunkStore):
        self._store = store
        self._chunk_store = chunk_store

    def get_preview(self, document_id: str, ref_index: int) -> dict:
        doc = self._store.get(document_id)
        chunks = self._chunk_store.load(document_id)
        chunk = next((c for c in chunks if c.chunk_index == ref_index), None)
        if chunk is None and chunks:
            chunk = chunks[min(ref_index, len(chunks) - 1)]
        if chunk is None:
            raise NotFoundError("Kaynak parçası bulunamadı")

        from app.services.search_response_builder import _snippet_from_text

        snippet = _snippet_from_text(chunk.text)

        return {
            "documentId": document_id,
            "documentName": doc.name,
            "page": chunk.page,
            "section": chunk.section,
            "highlightText": snippet,
            "mimeKind": doc.mime_kind,
            "refIndex": ref_index,
        }
