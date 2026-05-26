import pytest

from app.eval.faithfulness_heuristic import (
    answer_relevant_to_query,
    answer_tokens_subset_of_context,
    contains_forbidden_terms,
)
from app.infrastructure.fake_llm import FakeLLM
from app.services.rag_engine import RAGEngine
from app.services.search_response_builder import SearchResponseBuilder

pytestmark = pytest.mark.tc_uat


@pytest.mark.tc_uat
def test_tc_uat_05_faithfulness_heuristic(app, uat_doc_id, uat_cases):
    case = next(c for c in uat_cases if c["id"] == "TC_UAT_05")
    pipeline = app.extensions["query_pipeline"]
    engine = RAGEngine(pipeline, FakeLLM(), SearchResponseBuilder())

    result = engine.generate(case["query"], [uat_doc_id], [])
    answer = result["message"]["content"]
    assert result["sources"], "Kaynak bekleniyordu"
    assert not contains_forbidden_terms(answer, case["forbidden_terms"])

    contexts = [s.get("highlightText", "") or "" for s in result["sources"]]
    for hit in pipeline.retrieve_hits(case["query"], [uat_doc_id]):
        contexts.append(hit.text)
    if case.get("required_terms_from_context"):
        assert answer_tokens_subset_of_context(answer, contexts)


@pytest.mark.tc_uat
def test_tc_uat_06_answer_relevancy(app, uat_doc_id, uat_cases):
    case = next(c for c in uat_cases if c["id"] == "TC_UAT_06")
    pipeline = app.extensions["query_pipeline"]
    engine = RAGEngine(pipeline, FakeLLM(), SearchResponseBuilder())

    result = engine.generate(case["query"], [uat_doc_id], [])
    answer = result["message"]["content"]
    assert "bulunmamaktadır" not in answer.lower()
    assert answer_relevant_to_query(answer, case["query"])
