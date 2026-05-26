from app.domain.chunk import Chunk
from app.infrastructure.chroma_vector_store import ChromaVectorStore
from app.infrastructure.deterministic_embedding import DeterministicEmbedding
from app.services.indexing_service import IndexingService


def test_indexing_service_indexes_chunks(tmp_path):
    vector_store = ChromaVectorStore(tmp_path / "chroma", dimension=768)
    embedding = DeterministicEmbedding()
    service = IndexingService(embedding, vector_store, batch_size=2)
    chunks = [
        Chunk(text="one", chunk_index=0, page=1),
        Chunk(text="two", chunk_index=1, page=1),
        Chunk(text="three", chunk_index=2, page=2),
    ]
    count = service.index("doc-x", "rapor.txt", chunks)
    assert count == 3
    assert vector_store.count_by_document("doc-x") == 3
