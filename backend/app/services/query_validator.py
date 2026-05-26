from app.constants import messages
from app.domain.errors import ValidationError


class QueryValidator:
    """Sorgu uzunluğu doğrulaması (10–500 karakter)."""

    def __init__(self, min_length: int = 10, max_length: int = 500):
        self._min = min_length
        self._max = max_length

    def validate(self, message: str) -> str:
        text = (message or "").strip()
        if len(text) < self._min:
            raise ValidationError(messages.QUERY_TOO_SHORT, status_code=400)
        if len(text) > self._max:
            raise ValidationError(messages.QUERY_TOO_LONG, status_code=400)
        return text
