from app.domain.search_hit import SearchHit


class ContextFilter:
    """Kosinüs benzerlik eşiği — rapor ≥0.75 (TC_SIM)."""

    def __init__(self, threshold: float = 0.75):
        self._threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    def apply(self, hits: list[SearchHit]) -> list[SearchHit]:
        """Eşik altındaki parçaları eler."""
        return [h for h in hits if h.similarity >= self._threshold]
