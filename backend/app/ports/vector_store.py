from typing import Protocol

from app.domain.chunk import Chunk
from app.domain.search_hit import SearchHit


class VectorStorePort(Protocol):
    """ChromaDB vektör indeksi sözleşmesi."""

    @property
    def dimension(self) -> int:
        """Embedding vektör boyutu."""
        ...

    def upsert_chunks(
        self,
        document_id: str,
        document_name: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Chunk metinlerini ve embedding'leri indekse yazar."""
        ...

    def delete_by_document(self, document_id: str) -> None:
        """Belgeye ait tüm vektör kayıtlarını siler."""
        ...

    def count_by_document(self, document_id: str) -> int:
        """Belgeye ait indekslenmiş kayıt sayısı."""
        ...

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[SearchHit]:
        """Anlamsal benzerlik araması (kosinüs)."""
        ...
