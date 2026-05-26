from app.eval.faithfulness_heuristic import (
    answer_relevant_to_query,
    answer_tokens_subset_of_context,
    contains_forbidden_terms,
)


def test_forbidden_terms():
    assert contains_forbidden_terms("Mars kolonisi", ["Mars"])


def test_subset_of_context():
    ctx = ["Ar-Ge yatirimlari onemlidir."]
    assert answer_tokens_subset_of_context("Ar-Ge yatirimlari onemlidir [1]", ctx)


def test_answer_relevant():
    assert answer_relevant_to_query(
        "Ar-Ge yatirimlari onemlidir",
        "Ar-Ge yatirimlari ne kadar onemli?",
    )
