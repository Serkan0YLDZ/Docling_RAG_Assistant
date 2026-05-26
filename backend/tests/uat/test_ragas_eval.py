import os

import pytest

pytestmark = pytest.mark.rag_eval

ragas = pytest.importorskip("ragas")
from datasets import Dataset  # noqa: E402
from ragas import evaluate  # noqa: E402
from ragas.metrics import answer_relevancy, faithfulness  # noqa: E402


@pytest.mark.tc_uat
@pytest.mark.rag_eval
def test_tc_uat_07_ragas_faithfulness_and_relevancy(app, uat_doc_id):
    """RAGAS faithfulness + answer relevancy (GEMINI_API_KEY gerekir)."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        pytest.skip("GEMINI_API_KEY tanımlı değil")

    pipeline = app.extensions["query_pipeline"]
    engine = app.extensions["rag_engine"]

    query = "Ar-Ge yatirimlari ne kadar onemli?"
    hits = pipeline.retrieve_hits(query, [uat_doc_id])
    if not hits:
        pytest.skip("Retrieval bağlam üretmedi; RAGAS atlandı")

    result = engine.generate(query, [uat_doc_id], [])
    answer = result["message"]["content"]
    contexts = [h.text for h in hits[:3]]
    ground_truth = (
        "Ar-Ge yatirimlari sirketin en buyuk harcama kalemidir ve onemlidir."
    )

    dataset = Dataset.from_dict(
        {
            "question": [query],
            "contexts": [contexts],
            "answer": [answer],
            "ground_truth": [ground_truth],
        }
    )

    scores = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
    )
    df = scores.to_pandas()
    row = df.iloc[0]
    faith = float(row.get("faithfulness", 0) or 0)
    relev = float(row.get("answer_relevancy", 0) or 0)

    min_faith = float(os.environ.get("RAG_EVAL_MIN_FAITHFULNESS", "0.5"))
    min_relev = float(os.environ.get("RAG_EVAL_MIN_RELEVANCY", "0.5"))
    assert faith >= min_faith, f"faithfulness={faith}"
    assert relev >= min_relev, f"answer_relevancy={relev}"
