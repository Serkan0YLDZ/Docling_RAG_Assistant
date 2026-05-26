from typing import Protocol


class EmbeddingPort(Protocol):
    """Metinleri vektör uzayına gömer."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini embedding vektörlerine dönüştürür (doküman indeksi)."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Kullanıcı sorgusunu vektörleştirir (RETRIEVAL_QUERY)."""
        ...
