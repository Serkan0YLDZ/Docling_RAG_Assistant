import pytest

from app.domain.chunk import Chunk
from app.domain.document import Document
from app.infrastructure.chroma_vector_store import ChromaVectorStore
from app.infrastructure.deterministic_embedding import DeterministicEmbedding
from app.services.chunk_store import ChunkStore
from app.services.context_filter import ContextFilter
from app.services.file_store import FileStore
from app.services.indexing_service import IndexingService
from app.services.query_pipeline import QueryPipeline
from app.services.query_validator import QueryValidator
from app.services.search_response_builder import SearchResponseBuilder


@pytest.fixture
def pipeline(tmp_path):
    store = FileStore(tmp_path / "uploads", tmp_path / "registry.json")
    chunk_store = ChunkStore(tmp_path / "chunks")
    embedding = DeterministicEmbedding()
    vector_store = ChromaVectorStore(tmp_path / "chroma", dimension=768)
    indexing = IndexingService(embedding, vector_store, batch_size=8)

    doc = Document(name="finans.txt", size_bytes=100, mime_kind="text", status="ready")
    store.save_file(doc, b"x")
    chunks = [
        Chunk(
            text="Ar-Ge yatırımları en büyük harcama kalemidir.",
            chunk_index=0,
            page=1,
            section="Finans",
        ),
        Chunk(
            text="Pazarlama bütçesi düşük kaldı.",
            chunk_index=1,
            page=2,
            section="Pazarlama",
        ),
    ]
    chunk_store.save(doc.id, chunks)
    indexing.index(doc.id, doc.name, chunks)

    store.update(
        Document(
            id=doc.id,
            name=doc.name,
            size_bytes=doc.size_bytes,
            mime_kind=doc.mime_kind,
            status="ready",
            chunk_count=2,
        )
    )

    pipe = QueryPipeline(
        store=store,
        embedding=embedding,
        vector_store=vector_store,
        validator=QueryValidator(10, 500),
        context_filter=ContextFilter(0.0),
        response_builder=SearchResponseBuilder(),
        top_k=5,
    )
    return pipe, doc.id


def test_search_returns_hits_for_related_query(pipeline):
    pipeline, doc_id = pipeline
    result = pipeline.search_only(
        "Ar-Ge yatırımları hakkında bilgi",
        document_ids=[doc_id],
    )
    assert result["message"]["role"] == "assistant"
    assert len(result["sources"]) >= 1
    assert result["sources"][0]["documentId"] == doc_id


def test_search_no_context_message(pipeline):
    pipeline, _doc_id = pipeline
    result = pipeline.search_only(
        "xyzzy completely unrelated quantum physics",
        document_ids=["00000000-0000-0000-0000-000000000000"],
    )
    assert "bulunmamaktadır" in result["message"]["content"]
    assert result["sources"] == []
