import pytest

from app.eval.retrieval_metrics import precision_at_k, recall_at_k
from app.services.chunk_store import ChunkStore

pytestmark = pytest.mark.tc_uat


def _relevant_chunk_indices(chunks, keywords: list[str]) -> set[int]:
    relevant: set[int] = set()
    for chunk in chunks:
        text_lower = chunk.text.lower()
        if any(kw.lower() in text_lower for kw in keywords):
            relevant.add(chunk.chunk_index)
    return relevant


def _raw_retrieved_indices(app, query: str, doc_id: str, top_k: int) -> list[int]:
    pipeline = app.extensions["query_pipeline"]
    embedding = app.extensions["embedding"]
    vector_store = app.extensions["vector_store"]
    query_vector = embedding.embed_query(query)
    hits = vector_store.query(
        query_embedding=query_vector,
        top_k=top_k,
        document_ids=[doc_id],
    )
    return [h.chunk_index for h in hits]


@pytest.mark.tc_uat
def test_tc_uat_02_in_scope_retrieval_meets_threshold(app, uat_doc_id, uat_cases):
    case = next(c for c in uat_cases if c["id"] == "TC_UAT_02")
    pipeline = app.extensions["query_pipeline"]
    hits = pipeline.retrieve_hits(case["query"], [uat_doc_id])
    assert hits, "Beklenen bağlam bulunamadı"
    assert hits[0].similarity >= case["min_similarity"]
    combined = " ".join(h.text for h in hits)
    for phrase in case["expect_chunk_contains"]:
        assert phrase.lower() in combined.lower()


@pytest.mark.tc_uat
def test_tc_uat_03_contextual_precision(app, uat_doc_id, uat_cases):
    case = next(c for c in uat_cases if c["id"] == "TC_UAT_03")
    cfg = app.extensions["config"]
    chunk_store: ChunkStore = ChunkStore(cfg.CHUNKS_DIR)
    chunks = chunk_store.load(uat_doc_id)
    relevant = _relevant_chunk_indices(chunks, case["relevant_keywords"])
    assert relevant, "Altın etiket chunk bulunamadı"

    retrieved = _raw_retrieved_indices(
        app, case["query"], uat_doc_id, case["k"]
    )
    score = precision_at_k(relevant, retrieved, case["k"])
    assert score >= case["min_precision"], f"precision@{case['k']}={score}"


@pytest.mark.tc_uat
def test_tc_uat_04_contextual_recall(app, uat_doc_id, uat_cases):
    case = next(c for c in uat_cases if c["id"] == "TC_UAT_04")
    cfg = app.extensions["config"]
    chunk_store: ChunkStore = ChunkStore(cfg.CHUNKS_DIR)
    chunks = chunk_store.load(uat_doc_id)
    relevant = _relevant_chunk_indices(chunks, case["relevant_keywords"])
    assert relevant

    retrieved = _raw_retrieved_indices(
        app, case["query"], uat_doc_id, case["k"]
    )
    score = recall_at_k(relevant, retrieved, case["k"])
    assert score >= case["min_recall"], f"recall@{case['k']}={score}"
