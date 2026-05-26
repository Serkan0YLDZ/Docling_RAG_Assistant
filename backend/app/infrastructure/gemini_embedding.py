import logging
import os

from google import genai
from google.genai import types

from app.constants.embedding import gemini_embedding_api_model
from app.constants import messages
from app.domain.errors import ValidationError
from app.infrastructure.gemini_retry import call_with_quota_retry
from app.ports.embedding import EmbeddingPort

_log = logging.getLogger(__name__)


class GeminiEmbedding:
    """Google Gemini embedding API (gemini-embedding-2)."""

    def __init__(
        self,
        api_key: str | None = None,
        batch_size: int = 32,
        dimension: int = 768,
        min_interval_sec: float = 0.7,
        max_retries: int = 8,
    ):
        key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        if not key:
            raise ValidationError(messages.MISSING_GEMINI_KEY, status_code=500)
        self._client = genai.Client(api_key=key)
        self._model = gemini_embedding_api_model()
        self._batch_size = max(1, batch_size)
        self._dimension = dimension
        self._min_interval_sec = max(0.0, min_interval_sec)
        self._max_retries = max(1, max_retries)
        self._last_request_at = [0.0]

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini embedding vektörlerine dönüştürür."""
        if not texts:
            return []

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            response = call_with_quota_retry(
                lambda b=batch: self._client.models.embed_content(
                    model=self._model,
                    contents=self._contents_for_batch(b),
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                    ),
                ),
                max_retries=self._max_retries,
                min_interval_sec=self._min_interval_sec,
                last_request_at=self._last_request_at,
                label="Gemini embedding",
            )
            batch_vectors = self._parse_embeddings(response, len(batch))
            vectors.extend(batch_vectors)

        if vectors:
            self._dimension = len(vectors[0])
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """Sorgu vektörü — indeks ile aynı uzay (RETRIEVAL_DOCUMENT)."""
        response = call_with_quota_retry(
            lambda: self._client.models.embed_content(
                model=self._model,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            ),
            max_retries=self._max_retries,
            min_interval_sec=self._min_interval_sec,
            last_request_at=self._last_request_at,
            label="Gemini query embedding",
        )
        vectors = self._parse_embeddings(response, 1)
        return vectors[0]

    @staticmethod
    def _contents_for_batch(texts: list[str]):
        """Her metin için ayrı vektör (gemini-embedding-2 birleşik vektör üretmez)."""
        if len(texts) == 1:
            return texts[0]
        return [
            types.Content(parts=[types.Part.from_text(text=t)]) for t in texts
        ]

    def _parse_embeddings(self, response, expected: int) -> list[list[float]]:
        embeddings = getattr(response, "embeddings", None) or []
        vectors: list[list[float]] = []
        for item in embeddings:
            values = getattr(item, "values", None)
            if values is None and isinstance(item, dict):
                values = item.get("values")
            if values is not None:
                vectors.append(list(values))
        if len(vectors) != expected:
            raise RuntimeError(
                f"Gemini embedding beklenen {expected}, alınan {len(vectors)} "
                f"(model={self._model}; çoklu metin için Content nesnesi gerekir)"
            )
        return vectors
