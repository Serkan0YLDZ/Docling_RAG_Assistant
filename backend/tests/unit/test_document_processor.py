from pathlib import Path

from app.infrastructure.noop_chunk_enricher import NoOpChunkEnricher
from app.ports.docling_parser import ParsedDocument
from app.services.chunk_store import ChunkStore
from app.services.document_processor import DocumentProcessor
from app.services.file_store import FileStore


class FakeParser:
    """Docling yerine sabit markdown döner."""

    def parse(self, file_path: Path, mime_kind: str) -> ParsedDocument:
        return ParsedDocument(
            markdown=(
                "# Finans\n\n"
                + "word " * 600
                + "\n\n## Ar-Ge\n\n"
                + "detay " * 50
            ),
            page_count=3,
        )


def test_processor_creates_chunks(tmp_path):
    store = FileStore(tmp_path / "uploads", tmp_path / "registry.json")
    chunk_store = ChunkStore(tmp_path / "chunks")
    from app.domain.document import Document

    doc = Document(name="rapor.txt", size_bytes=100, mime_kind="text")
    store.save_file(doc, b"placeholder")

    processor = DocumentProcessor(
        store=store,
        chunk_store=chunk_store,
        parser=FakeParser(),
        enricher=NoOpChunkEnricher(),
        max_tokens=512,
        overlap_ratio=0.15,
        use_llm_enrichment=False,
    )
    chunks = processor.process(doc.id)
    assert len(chunks) >= 2
    assert chunk_store.count(doc.id) == len(chunks)

    updated = store.get(doc.id)
    assert updated.status == "processing"
    assert updated.chunk_count == len(chunks)
    assert updated.progress == 85
