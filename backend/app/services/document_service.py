import logging
import threading

from app.constants import messages
from app.domain.document import Document, mime_kind_from_filename
from app.domain.errors import NotFoundError
from app.infrastructure.gemini_retry import is_quota_exhausted
from app.services.document_processor import DocumentProcessor
from app.services.file_store import FileStore
from app.services.indexing_service import IndexingService
from app.services.upload_validator import UploadValidator

_log = logging.getLogger(__name__)


class DocumentService:
    """Belge yükleme, listeleme ve silme iş akışını yönetir."""

    def __init__(
        self,
        store: FileStore,
        validator: UploadValidator,
        processor: DocumentProcessor,
        chunk_store,
        indexing_service: IndexingService,
    ):
        self._store = store
        self._validator = validator
        self._processor = processor
        self._chunk_store = chunk_store
        self._indexing = indexing_service
        self._vector_store = indexing_service.vector_store
        self._jobs: dict[str, threading.Thread] = {}
        self._cancelled: set[str] = set()

    def list_documents(self) -> list[dict]:
        """Tüm belgeleri API DTO olarak döner."""
        return [doc.to_api_dict() for doc in self._store.list_documents()]

    def upload(self, filename: str, file_bytes: bytes) -> dict:
        """Dosyayı doğrular, kaydeder ve iş kuyruğuna alır."""
        self._validator.validate(filename, len(file_bytes))

        document = Document(
            name=filename,
            size_bytes=len(file_bytes),
            mime_kind=mime_kind_from_filename(filename),
            status="queued",
            progress=0,
            chunk_count=0,
        )
        self._store.save_file(document, file_bytes)
        self._enqueue_processing(document.id)
        return self._store.get(document.id).to_api_dict()

    def get_status(self, document_id: str) -> dict:
        """Belge işleme durumunu döner."""
        doc = self._store.get(document_id)
        return {"status": doc.status, "progress": doc.progress}

    def delete(self, document_id: str) -> None:
        """Belgeyi, chunk JSON'unu ve Chroma vektörlerini kaldırır (TC_DEL_01)."""
        self._cancelled.add(document_id)
        self._store.get(document_id)

        self._purge_vectors(document_id)
        self._purge_chunks(document_id)
        self._store.delete(document_id)
        self._jobs.pop(document_id, None)
        self._cancelled.discard(document_id)
        _log.info("Belge silindi: %s (chunk + Chroma temizlendi)", document_id)

    def _purge_vectors(self, document_id: str) -> None:
        before = self._vector_store.count_by_document(document_id)
        if before:
            self._vector_store.delete_by_document(document_id)
        remaining = self._vector_store.count_by_document(document_id)
        if remaining:
            raise RuntimeError(
                f"Chroma vektörleri silinemedi: {document_id} ({remaining} kaldı)"
            )

    def _purge_chunks(self, document_id: str) -> None:
        if self._chunk_store.exists(document_id):
            self._chunk_store.delete(document_id)
        if self._chunk_store.exists(document_id):
            raise RuntimeError(f"Chunk dosyası silinemedi: {document_id}")

    def _enqueue_processing(self, document_id: str) -> None:
        """Belgeyi arka planda Docling + indeksleme ile işler."""
        if document_id in self._jobs and self._jobs[document_id].is_alive():
            return

        thread = threading.Thread(
            target=self._run_processing_job,
            args=(document_id,),
            daemon=True,
        )
        self._jobs[document_id] = thread
        thread.start()

    def _document_still_active(self, document_id: str) -> bool:
        if document_id in self._cancelled:
            return False
        try:
            self._store.get(document_id)
            return True
        except NotFoundError:
            return False

    def _cleanup_orphan_artifacts(self, document_id: str) -> None:
        """Silme sırasında oluşan chunk / vektör artıklarını temizler."""
        if self._chunk_store.exists(document_id):
            self._chunk_store.delete(document_id)
        if self._vector_store.count_by_document(document_id) > 0:
            self._vector_store.delete_by_document(document_id)

    def _run_processing_job(self, document_id: str) -> None:
        """Docling + bölütleme + Chroma indeksleme job'u."""
        try:
            if not self._document_still_active(document_id):
                return
            try:
                doc = self._store.get(document_id)
            except NotFoundError:
                return

            doc.status = "processing"
            doc.progress = 5
            self._store.update(doc)

            def on_progress(progress: int) -> None:
                if not self._document_still_active(document_id):
                    return
                try:
                    current = self._store.get(document_id)
                    current.progress = progress
                    if progress >= 100:
                        current.status = "ready"
                    elif current.status != "ready":
                        current.status = "processing"
                    self._store.update(current)
                except Exception:
                    pass

            chunks = self._processor.process(document_id, on_progress=on_progress)
            if not self._document_still_active(document_id):
                self._cleanup_orphan_artifacts(document_id)
                return

            doc = self._store.get(document_id)
            indexed = self._indexing.index(
                document_id,
                doc.name,
                chunks,
                on_progress=on_progress,
            )

            if not self._document_still_active(document_id):
                self._cleanup_orphan_artifacts(document_id)
                return

            doc = self._store.get(document_id)
            doc.chunk_count = indexed
            doc.status = "ready"
            doc.progress = 100
            self._store.update(doc)
            on_progress(100)
        except Exception as exc:
            if is_quota_exhausted(exc):
                _log.error(
                    "Belge %s: %s — %s",
                    document_id,
                    messages.EMBEDDING_QUOTA_EXCEEDED,
                    exc,
                )
            else:
                _log.exception("Belge işleme hatası %s: %s", document_id, exc)
            try:
                doc = self._store.get(document_id)
                doc.status = "error"
                doc.progress = 0
                self._store.update(doc)
            except Exception:
                return
