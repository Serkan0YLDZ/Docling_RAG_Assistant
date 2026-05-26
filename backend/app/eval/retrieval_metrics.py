def precision_at_k(relevant: set[int], retrieved: list[int], k: int) -> float:
    """precision@k = |relevant ∩ top_k| / k"""
    if k <= 0:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    hits = sum(1 for idx in top if idx in relevant)
    return hits / k


def recall_at_k(relevant: set[int], retrieved: list[int], k: int) -> float:
    """recall@k = |relevant ∩ top_k| / |relevant|"""
    if not relevant:
        return 0.0
    top = retrieved[:k]
    hits = sum(1 for idx in top if idx in relevant)
    return hits / len(relevant)
