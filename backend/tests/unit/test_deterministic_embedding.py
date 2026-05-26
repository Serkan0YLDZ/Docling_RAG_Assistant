from app.infrastructure.deterministic_embedding import DeterministicEmbedding


def test_same_text_same_vector():
    emb = DeterministicEmbedding()
    a = emb.embed(["hello world"])
    b = emb.embed(["hello world"])
    assert a[0] == b[0]


def test_different_text_different_vector():
    emb = DeterministicEmbedding()
    a = emb.embed(["hello"])
    b = emb.embed(["world"])
    assert a[0] != b[0]


def test_dimension_is_768():
    emb = DeterministicEmbedding()
    vec = emb.embed(["test"])[0]
    assert len(vec) == 768


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def test_overlapping_text_high_similarity():
    emb = DeterministicEmbedding()
    chunk = "Ar-Ge yatirimlari sirketin en buyuk harcama kalemidir."
    query = "Ar-Ge yatirimlari sirketin en buyuk harcama kalemidir"
    qv = emb.embed_query(query)
    cv = emb.embed([chunk])[0]
    assert _cosine(qv, cv) >= 0.65
