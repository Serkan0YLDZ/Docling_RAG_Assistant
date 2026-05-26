from dataclasses import dataclass


@dataclass
class SearchHit:
    """Chroma anlamsal arama sonucu."""

    text: str
    similarity: float
    document_id: str
    document_name: str
    chunk_index: int
    page: int = 1
    section: str | None = None
    paragraph: int | None = None
