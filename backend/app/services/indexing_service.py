import logging

from app.domain.chunk import Chunk
from app.ports.embedding import EmbeddingPort
from app.ports.vector_store import VectorStorePort

_log = logging.getLogger(__name__)


class IndexingService:
    """Chunk'ları embed edip ChromaDB'ye yazar."""

    def __init__(
        self,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        batch_size: int = 32,
    ):
        self._embedding = embedding
        self._vector_store = vector_store
        self._batch_size = max(1, batch_size)

    @property
    def vector_store(self) -> VectorStorePort:
        return self._vector_store

    def index(
        self,
        document_id: str,
        document_name: str,
        chunks: list[Chunk],
        on_progress=None,
    ) -> int:
        """Chunk listesini vektör veritabanına indeksler."""
        if not chunks:
            self._vector_store.delete_by_document(document_id)
            return 0

        texts = [chunk.text for chunk in chunks]
        embeddings: list[list[float]] = []
        total_batches = (len(texts) + self._batch_size - 1) // self._batch_size

        for batch_idx, start in enumerate(range(0, len(texts), self._batch_size)):
            batch = texts[start : start + self._batch_size]
            embeddings.extend(self._embedding.embed(batch))
            if on_progress and total_batches:
                pct = 86 + int((batch_idx + 1) / total_batches * 13)
                on_progress(min(pct, 99))

        self._vector_store.delete_by_document(document_id)
        self._vector_store.upsert_chunks(
            document_id, document_name, chunks, embeddings
        )
        count = self._vector_store.count_by_document(document_id)
        _log.info("Belge %s indekslendi: %d vektör", document_id, count)
        if on_progress:
            on_progress(99)
        return count
