from app.eval.retrieval_metrics import precision_at_k, recall_at_k


def test_precision_at_k():
    assert precision_at_k({1, 2}, [1, 3, 2], 3) == 2 / 3


def test_recall_at_k():
    assert recall_at_k({1, 2}, [1, 3], 2) == 0.5
