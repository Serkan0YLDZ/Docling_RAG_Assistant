import json
from pathlib import Path
import tempfile
import threading

from app.domain.document import Document
from app.domain.errors import NotFoundError


class FileStore:
    """Belge dosyalarını ve meta kaydını diskte tutar."""

    def __init__(self, upload_dir: Path, registry_path: Path):
        self._upload_dir = upload_dir
        self._registry_path = registry_path
        self._lock = threading.Lock()
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._registry_path.exists():
            self._write_registry([])

    def list_documents(self) -> list[Document]:
        """Tüm belgeleri yüklenme tarihine göre yeniden eskiye döner."""
        records = self._read_registry()
        docs = [Document.from_dict(r) for r in records]
        return sorted(docs, key=lambda d: d.uploaded_at, reverse=True)

    def get(self, document_id: str) -> Document:
        """Kimliğe göre belge meta verisini getirir."""
        records = self._read_registry()
        for record in records:
            if record.get("id") == document_id:
                return Document.from_dict(record)
        raise NotFoundError(f"Belge bulunamadı: {document_id}")

    def save_file(self, document: Document, file_bytes: bytes) -> Path:
        """Dosyayı belge klasörüne yazar ve kaydı günceller."""
        doc_dir = self._upload_dir / document.id
        doc_dir.mkdir(parents=True, exist_ok=True)
        path = doc_dir / document.name
        path.write_bytes(file_bytes)

        with self._lock:
            records = self._read_registry_unlocked()
            records = [r for r in records if r.get("id") != document.id]
            records.append(document.to_store_dict())
            self._write_registry_unlocked(records)
        return path

    def update(self, document: Document) -> None:
        """Mevcut belge kaydını günceller."""
        with self._lock:
            records = self._read_registry_unlocked()
            updated = False
            for i, record in enumerate(records):
                if record.get("id") == document.id:
                    records[i] = document.to_store_dict()
                    updated = True
                    break
            if not updated:
                records.append(document.to_store_dict())
            self._write_registry_unlocked(records)

    def get_file_path(self, document_id: str) -> Path:
        """Belge dosyasının disk yolunu döner."""
        doc = self.get(document_id)
        path = self._upload_dir / document_id / doc.name
        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")
        return path

    def delete(self, document_id: str) -> None:
        """Belge dosyasını ve kaydını siler."""
        self.get(document_id)
        doc_dir = self._upload_dir / document_id
        if doc_dir.exists():
            for child in doc_dir.iterdir():
                child.unlink()
            doc_dir.rmdir()

        with self._lock:
            records = [
                r for r in self._read_registry_unlocked() if r.get("id") != document_id
            ]
            self._write_registry_unlocked(records)

    def _read_registry(self) -> list[dict]:
        with self._lock:
            return self._read_registry_unlocked()

    def _read_registry_unlocked(self) -> list[dict]:
        raw = self._registry_path.read_text(encoding="utf-8")
        return json.loads(raw) if raw.strip() else []

    def _write_registry(self, records: list[dict]) -> None:
        with self._lock:
            self._write_registry_unlocked(records)

    def _write_registry_unlocked(self, records: list[dict]) -> None:
        payload = json.dumps(records, ensure_ascii=False, indent=2)
        tmp_dir = self._registry_path.parent
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=tmp_dir,
            delete=False,
        ) as tmp:
            tmp.write(payload)
            tmp_path = Path(tmp.name)
        tmp_path.replace(self._registry_path)
