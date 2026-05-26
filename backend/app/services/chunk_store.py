import json
from pathlib import Path

from app.domain.chunk import Chunk


class ChunkStore:
    """Belge chunk'larını JSON dosyasında saklar."""

    def __init__(self, base_dir: Path):
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, document_id: str, chunks: list[Chunk]) -> None:
        """Chunk listesini diske yazar."""
        path = self._path(document_id)
        payload = [c.to_store_dict() for c in chunks]
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, document_id: str) -> list[Chunk]:
        """Belgeye ait chunk'ları okur."""
        path = self._path(document_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Chunk.from_store_dict(item) for item in data]

    def delete(self, document_id: str) -> None:
        """Belge chunk dosyasını siler."""
        path = self._path(document_id)
        if path.exists():
            path.unlink()

    def exists(self, document_id: str) -> bool:
        """Chunk JSON dosyası mevcut mu."""
        return self._path(document_id).exists()

    def count(self, document_id: str) -> int:
        """Kayıtlı chunk sayısı."""
        return len(self.load(document_id))

    def _path(self, document_id: str) -> Path:
        return self._base_dir / f"{document_id}.json"
