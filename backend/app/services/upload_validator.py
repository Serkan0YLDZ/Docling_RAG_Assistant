from pathlib import Path

from app.constants import messages
from app.domain.errors import ValidationError


class UploadValidator:
    """Yüklenen dosya boyutu ve uzantısını doğrular."""

    def __init__(self, max_bytes: int, allowed_extensions: frozenset[str]):
        self._max_bytes = max_bytes
        self._allowed = allowed_extensions

    def validate(self, filename: str, size_bytes: int) -> None:
        """Boş dosya, boyut ve uzantı kurallarını uygular."""
        if size_bytes == 0:
            raise ValidationError(messages.EMPTY_FILE, status_code=400)

        if size_bytes > self._max_bytes:
            raise ValidationError(messages.MAX_FILE_SIZE, status_code=413)

        ext = Path(filename).suffix.lstrip(".").lower()
        if ext not in self._allowed:
            raise ValidationError(messages.INVALID_EXTENSION, status_code=400)
