import re

_WORD_RE = re.compile(r"\b[\wçğıöşüÇĞİÖŞÜ]+\b", re.UNICODE)


def tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text) if len(w) > 2}


def _tokens_overlap(query_tokens: set[str], answer_tokens: set[str]) -> int:
    """Tam eşleşme veya kısa kök ön eki (onemli / onemlidir)."""
    count = 0
    for q in query_tokens:
        if q in answer_tokens:
            count += 1
            continue
        if len(q) < 4:
            continue
        if any(
            a.startswith(q) or q.startswith(a)
            for a in answer_tokens
            if len(a) >= 4
        ):
            count += 1
    return count


def answer_tokens_subset_of_context(answer: str, contexts: list[str]) -> bool:
    """Cevaptaki anlamlı tokenler bağlam birleşiminde mi (basit faithfulness)."""
    answer_tokens = tokenize(answer)
    if not answer_tokens:
        return True
    context_tokens = set()
    for ctx in contexts:
        context_tokens |= tokenize(ctx)
    if not context_tokens:
        return False
    foreign = answer_tokens - context_tokens
    allowed = {
        "kaynak",
        "kaynağı",
        "kaynakları",
        "kaynaklar",
        "sayfa",
        "bağlam",
        "bağlamdaki",
        "raporu",
        "finansal",
        "özet",
        "ozet",
    }
    foreign -= allowed
    return len(foreign) <= max(2, int(len(answer_tokens) * 0.15))


def contains_forbidden_terms(answer: str, forbidden: list[str]) -> bool:
    lower = answer.lower()
    return any(term.lower() in lower for term in forbidden)


def answer_relevant_to_query(answer: str, query: str) -> bool:
    """Soru anahtar kelimelerinin bir kısmı cevapta (kök/ön ek toleranslı)."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return True
    a_tokens = tokenize(answer)
    overlap = _tokens_overlap(q_tokens, a_tokens)
    required = min(2, len(q_tokens))
    return overlap >= required
