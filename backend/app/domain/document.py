from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

DocumentStatus = Literal["queued", "processing", "ready", "error"]
MimeKind = Literal["pdf", "text", "doc"]


@dataclass
class Document:
    """Yüklenen belge meta verisi."""

    name: str
    size_bytes: int
    mime_kind: MimeKind
    id: str = field(default_factory=lambda: str(uuid4()))
    status: DocumentStatus = "queued"
    progress: int = 0
    uploaded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    chunk_count: int = 0

    def to_api_dict(self) -> dict:
        """Frontend DocumentItem DTO."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "uploadedAt": self.uploaded_at,
            "sizeLabel": format_file_size(self.size_bytes),
            "mimeKind": self.mime_kind,
            "chunkCount": self.chunk_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """JSON kaydından belge oluşturur."""
        return cls(
            id=data["id"],
            name=data["name"],
            size_bytes=data["size_bytes"],
            mime_kind=data["mime_kind"],
            status=data.get("status", "queued"),
            progress=data.get("progress", 0),
            uploaded_at=data.get("uploaded_at", datetime.now(timezone.utc).isoformat()),
            chunk_count=data.get("chunk_count", 0),
        )

    def to_store_dict(self) -> dict:
        """Kalıcı depolama için sözlük."""
        return {
            "id": self.id,
            "name": self.name,
            "size_bytes": self.size_bytes,
            "mime_kind": self.mime_kind,
            "status": self.status,
            "progress": self.progress,
            "uploaded_at": self.uploaded_at,
            "chunk_count": self.chunk_count,
        }


def format_file_size(size_bytes: int) -> str:
    """Bayt cinsinden boyutu okunabilir etikete çevirir."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024)} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def mime_kind_from_filename(filename: str) -> MimeKind:
    """Dosya uzantısından mime türünü çıkarır."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return "pdf"
    if ext == "txt":
        return "text"
    return "doc"
