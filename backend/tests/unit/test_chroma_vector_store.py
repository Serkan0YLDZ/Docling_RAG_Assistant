from app.domain.chunk import Chunk
from app.infrastructure.chroma_vector_store import ChromaVectorStore
from app.infrastructure.deterministic_embedding import DeterministicEmbedding


def test_upsert_count_delete(tmp_path):
    store = ChromaVectorStore(tmp_path / "chroma", dimension=768)
    emb = DeterministicEmbedding()
    chunks = [
        Chunk(text="alpha", chunk_index=0, page=1, section="A"),
        Chunk(text="beta", chunk_index=1, page=2),
    ]
    vectors = emb.embed([c.text for c in chunks])
    store.upsert_chunks("doc-1", "test.pdf", chunks, vectors)
    assert store.count_by_document("doc-1") == 2

    store.delete_by_document("doc-1")
    assert store.count_by_document("doc-1") == 0
