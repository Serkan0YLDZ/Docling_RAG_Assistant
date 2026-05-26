from pathlib import Path

from app.ports.docling_parser import DoclingParserPort, ParsedDocument


class FakeDoclingParser(DoclingParserPort):
    """Testler için hızlı ayrıştırma (Docling model yüklemez)."""

    def parse(self, file_path: Path, mime_kind: str) -> ParsedDocument:
        """Dosya içeriğini veya kısa örnek metni döner."""
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8", errors="replace")
        else:
            text = "örnek belge içeriği"
        if not text.strip():
            text = "boş olmayan içerik"
        return ParsedDocument(
            markdown=f"# Belge\n\n{text}\n\n## Bölüm\n\n{text[:200]}",
            page_count=2,
            ocr_enabled=False,
        )
