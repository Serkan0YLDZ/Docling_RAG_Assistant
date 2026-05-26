import logging
import os

from google import genai
from google.genai import types

from app.constants import messages
from app.domain.errors import ValidationError
from app.infrastructure.gemini_retry import call_with_quota_retry

_log = logging.getLogger(__name__)


class GeminiLLM:
    """Google Gemini metin üretimi (RAG ve chunk zenginleştirme)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        min_interval_sec: float = 1.0,
        max_retries: int = 8,
    ):
        key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        if not key:
            raise ValidationError(messages.MISSING_GEMINI_KEY, status_code=500)
        self._client = genai.Client(api_key=key)
        self._model = model if model.startswith("models/") else f"models/{model}"
        self._min_interval_sec = max(0.0, min_interval_sec)
        self._max_retries = max(1, max_retries)
        self._last_request_at = [0.0]

    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        response = call_with_quota_retry(
            lambda: self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            ),
            max_retries=self._max_retries,
            min_interval_sec=self._min_interval_sec,
            last_request_at=self._last_request_at,
            label="Gemini LLM",
        )
        text = getattr(response, "text", None) or ""
        if not text.strip():
            raise RuntimeError("Gemini boş yanıt döndü")
        return text.strip()
