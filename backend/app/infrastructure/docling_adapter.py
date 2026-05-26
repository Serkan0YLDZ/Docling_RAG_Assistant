import logging
import os
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import OcrAutoOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from app.infrastructure.docling_device import build_accelerator_options
from app.ports.docling_parser import DoclingParserPort, ParsedDocument
from app.services.page_mapper import build_section_pages_from_docling

_log = logging.getLogger(__name__)


def _ocr_enabled() -> bool:
    return os.environ.get("DOCLING_DO_OCR", "true").lower() in ("1", "true", "yes")


class DoclingAdapter(DoclingParserPort):
    """Docling DocumentConverter ile PDF/DOCX ayrıştırma."""

    def __init__(self) -> None:
        accelerator = build_accelerator_options()
        pdf_options = PdfPipelineOptions()
        pdf_options.accelerator_options = accelerator
        pdf_options.do_ocr = _ocr_enabled()
        pdf_options.do_table_structure = True
        if pdf_options.do_ocr:
            # ocrmac → rapidocr → easyocr sırası (Docling OcrAutoModel)
            pdf_options.ocr_options = OcrAutoOptions()

        self._ocr_enabled = pdf_options.do_ocr
        _log.info("Docling pipeline: ocr=%s device=%s", self._ocr_enabled, accelerator.device)

        self._converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.DOCX],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
            },
        )

    def parse(self, file_path: Path, mime_kind: str) -> ParsedDocument:
        """Dosyayı markdown metnine çevirir."""
        if mime_kind == "text":
            text = file_path.read_text(encoding="utf-8", errors="replace")
            return ParsedDocument(markdown=text, page_count=1, ocr_enabled=False)

        _log.info("Docling ayrıştırma: %s (ocr=%s)", file_path.name, self._ocr_enabled)
        result = self._converter.convert(str(file_path))
        if result.status not in (
            ConversionStatus.SUCCESS,
            ConversionStatus.PARTIAL_SUCCESS,
        ):
            raise RuntimeError(f"Docling dönüşümü başarısız: {result.status}")

        doc = result.document
        markdown = doc.export_to_markdown()
        if not markdown.strip():
            raise RuntimeError(
                "Docling metin üretemedi. Taranmış PDF ise DOCLING_DO_OCR=true ve "
                "DOCLING_DEVICE=cpu ile yeniden yükleyin."
            )

        pages = getattr(doc, "pages", None) or []
        page_count = max(1, len(pages) if pages else 1)
        section_pages = build_section_pages_from_docling(doc)
        return ParsedDocument(
            markdown=markdown,
            page_count=page_count,
            ocr_enabled=self._ocr_enabled,
            section_pages=section_pages or None,
        )
