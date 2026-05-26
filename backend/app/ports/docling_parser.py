from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class ParsedDocument:
    """Docling veya düz metin ayrıştırma çıktısı."""

    markdown: str
    page_count: int = 1
    ocr_enabled: bool = False
    section_pages: dict[str, int] | None = None


class DoclingParserPort(Protocol):
    """Belge dosyasını yapısal metne çevirir."""

    def parse(self, file_path: Path, mime_kind: str) -> ParsedDocument:
        """Dosyayı markdown benzeri metne dönüştürür."""
        ...
