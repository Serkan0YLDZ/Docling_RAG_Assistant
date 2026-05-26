import logging

from app.domain.errors import ValidationError
from app.ports.embedding import EmbeddingPort
from app.ports.vector_store import VectorStorePort
from app.services.context_filter import ContextFilter
from app.services.file_store import FileStore
from app.services.query_validator import QueryValidator
from app.services.search_response_builder import SearchResponseBuilder

_log = logging.getLogger(__name__)


class QueryPipeline:
    """Anlamsal arama orkestrasyonu (B4: search_only, LLM yok)."""

    def __init__(
        self,
        store: FileStore,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        validator: QueryValidator,
        context_filter: ContextFilter,
        response_builder: SearchResponseBuilder,
        top_k: int = 5,
    ):
        self._store = store
        self._embedding = embedding
        self._vector_store = vector_store
        self._validator = validator
        self._filter = context_filter
        self._builder = response_builder
        self._top_k = top_k

    def retrieve_hits(
        self,
        message: str,
        document_ids: list[str] | None = None,
    ) -> list:
        """Sorguyu doğrular, Chroma arar, eşik uygular; SearchHit listesi döner."""
        query = self._validator.validate(message)
        scope = self._resolve_document_ids(document_ids)
        if scope is not None and not scope:
            return []

        query_vector = self._embedding.embed_query(query)
        hits = self._vector_store.query(
            query_embedding=query_vector,
            top_k=self._top_k,
            document_ids=scope,
        )
        filtered = self._filter.apply(hits)
        if hits and not filtered:
            best = max(h.similarity for h in hits)
            _log.warning(
                "Arama: %d sonuç eşik %.2f altında (en yüksek skor=%.3f)",
                len(hits),
                self._filter.threshold,
                best,
            )
        else:
            _log.info(
                "Arama: %d ham, %d eşik>=%.2f",
                len(hits),
                len(filtered),
                self._filter.threshold,
            )
        return filtered

    def search_only(
        self,
        message: str,
        document_ids: list[str] | None = None,
    ) -> dict:
        """Sorguyu doğrular, Chroma arar, eşik uygular; QueryResponse döner."""
        filtered = self.retrieve_hits(message, document_ids)
        return self._builder.build(filtered)

    def _resolve_document_ids(
        self, document_ids: list[str] | None
    ) -> list[str] | None:
        """İşaretli hazır belgeler; boş liste = tüm hazır belgeler."""
        ready = [
            doc.id
            for doc in self._store.list_documents()
            if doc.status == "ready" and doc.chunk_count > 0
        ]
        if not ready:
            return []

        if not document_ids:
            return ready

        allowed = set(ready)
        filtered = [doc_id for doc_id in document_ids if doc_id in allowed]
        return filtered
