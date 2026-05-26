from typing import Protocol


class ChunkEnrichmentPort(Protocol):
    """Docling çıktısı üzerinde bağlamsal zenginleştirme (rapor §3.1)."""

    def enrich(self, markdown: str, document_name: str = "") -> str:
        """Markdown metnini yapı/metadata açısından iyileştirir."""
        ...
