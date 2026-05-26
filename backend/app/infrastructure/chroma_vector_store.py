import logging
from pathlib import Path

import chromadb

from app.domain.chunk import Chunk
from app.domain.search_hit import SearchHit

_log = logging.getLogger(__name__)


def _chunk_metadata(document_id: str, document_name: str, chunk: Chunk) -> dict:
    meta = {
        "document_id": document_id,
        "document_name": document_name,
        "chunk_index": chunk.chunk_index,
        "page": chunk.page,
    }
    if chunk.section:
        meta["section"] = chunk.section
    if chunk.paragraph is not None:
        meta["paragraph"] = chunk.paragraph
    return meta


class ChromaVectorStore:
    """Embedded ChromaDB — semantic search indeksi."""

    def __init__(
        self,
        persist_path: Path,
        collection_name: str = "rag_chunks",
        dimension: int = 768,
    ):
        persist_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_path))
        self._dimension = dimension
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def dimension(self) -> int:
        return self._dimension

    def upsert_chunks(
        self,
        document_id: str,
        document_name: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("chunk ve embedding sayıları eşleşmiyor")

        ids = [f"{document_id}:{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            _chunk_metadata(document_id, document_name, chunk) for chunk in chunks
        ]
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def delete_by_document(self, document_id: str) -> None:
        """Belgeye ait tüm vektörleri Chroma'dan kaldırır."""
        ids = self._ids_for_document(document_id)
        if ids:
            self._collection.delete(ids=ids)
            return
        try:
            self._collection.delete(where={"document_id": document_id})
        except Exception as exc:
            _log.warning(
                "Chroma where-delete başarısız (document_id=%s): %s",
                document_id,
                exc,
            )

    def _ids_for_document(self, document_id: str) -> list[str]:
        try:
            result = self._collection.get(
                where={"document_id": document_id},
                include=[],
            )
            return list(result.get("ids") or [])
        except Exception as exc:
            _log.warning(
                "Chroma get ids başarısız (document_id=%s): %s",
                document_id,
                exc,
            )
            return []

    def count_by_document(self, document_id: str) -> int:
        try:
            result = self._collection.get(
                where={"document_id": document_id},
                include=[],
            )
            return len(result.get("ids") or [])
        except Exception:
            return 0

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[SearchHit]:
        """K-NN arama; distance → similarity = 1 - distance (cosine)."""
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}

        try:
            result = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []

        return self._parse_query_result(result)

    def _parse_query_result(self, result: dict) -> list[SearchHit]:
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        hits: list[SearchHit] = []
        for idx, doc_id in enumerate(ids):
            if idx >= len(documents):
                break
            meta = metadatas[idx] if idx < len(metadatas) else {}
            distance = distances[idx] if idx < len(distances) else 1.0
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))
            hits.append(
                SearchHit(
                    text=documents[idx] or "",
                    similarity=similarity,
                    document_id=str(meta.get("document_id", "")),
                    document_name=str(meta.get("document_name", "")),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    page=int(meta.get("page", 1)),
                    section=meta.get("section"),
                    paragraph=meta.get("paragraph"),
                )
            )
        return hits
