from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """Ayrıştırılmış metin parçası."""

    text: str
    chunk_index: int
    page: int = 1
    section: str | None = None
    paragraph: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_store_dict(self) -> dict:
        """Kalıcı depolama için sözlük."""
        return {
            "text": self.text,
            "chunk_index": self.chunk_index,
            "page": self.page,
            "section": self.section,
            "paragraph": self.paragraph,
            "metadata": self.metadata,
        }

    @classmethod
    def from_store_dict(cls, data: dict) -> "Chunk":
        """JSON kaydından chunk oluşturur."""
        return cls(
            text=data["text"],
            chunk_index=data["chunk_index"],
            page=data.get("page", 1),
            section=data.get("section"),
            paragraph=data.get("paragraph"),
            metadata=data.get("metadata", {}),
        )
