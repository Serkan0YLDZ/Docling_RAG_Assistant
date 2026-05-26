import logging

from app.domain.chunk import Chunk
from app.ports.chunk_enrichment import ChunkEnrichmentPort
from app.ports.docling_parser import DoclingParserPort
from app.services.chunk_store import ChunkStore
from app.services.file_store import FileStore
from app.services.header_footer_stripper import HeaderFooterStripper
from app.services.page_mapper import assign_pages_from_document
from app.services.recursive_splitter import RecursiveSplitter
from app.services.structural_chunker import StructuralChunker
from app.services.table_continuity_merger import TableContinuityMerger

_log = logging.getLogger(__name__)


class DocumentProcessor:
    """Docling → son işleme → yapısal/recursive bölütleme pipeline'ı."""

    def __init__(
        self,
        store: FileStore,
        chunk_store: ChunkStore,
        parser: DoclingParserPort,
        enricher: ChunkEnrichmentPort,
        max_tokens: int = 512,
        overlap_ratio: float = 0.15,
        use_llm_enrichment: bool = False,
    ):
        self._store = store
        self._chunk_store = chunk_store
        self._parser = parser
        self._enricher = enricher
        self._use_llm_enrichment = use_llm_enrichment
        self._stripper = HeaderFooterStripper()
        self._table_merger = TableContinuityMerger()
        self._structural = StructuralChunker()
        self._recursive = RecursiveSplitter(max_tokens, overlap_ratio)

    def process(self, document_id: str, on_progress=None) -> list[Chunk]:
        """Belgeyi ayrıştırır, böler ve chunk'ları kaydeder."""
        doc = self._store.get(document_id)
        file_path = self._store.get_file_path(document_id)

        def report(progress: int) -> None:
            if on_progress:
                on_progress(progress)

        report(10)
        parsed = self._parser.parse(file_path, doc.mime_kind)

        report(28)
        cleaned = self._stripper.strip(parsed.markdown)

        working = cleaned
        if self._use_llm_enrichment:
            report(40)
            working = self._enricher.enrich(working, document_name=doc.name)
            working = self._stripper.strip(working)

        report(50)
        working = self._table_merger.merge(working)

        report(60)
        blocks = self._structural.split(working)
        chunks = self._recursive.split_blocks(blocks, parsed.page_count)
        assign_pages_from_document(working, chunks, parsed.section_pages)

        if parsed.ocr_enabled:
            for chunk in chunks:
                chunk.metadata["ocr"] = True
        if self._use_llm_enrichment:
            for chunk in chunks:
                chunk.metadata["llm_enriched"] = True

        report(85)
        self._chunk_store.save(document_id, chunks)

        doc.chunk_count = len(chunks)
        doc.status = "processing"
        doc.progress = 85
        self._store.update(doc)
        _log.info("Belge %s ayrıştırıldı: %d chunk (indeksleme bekliyor)", document_id, len(chunks))
        return chunks
