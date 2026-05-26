import hashlib
import math
import re
import struct
from typing import ClassVar

from app.ports.embedding import EmbeddingPort

_TOKEN_RE = re.compile(r"\b[\wçğıöşüÇĞİÖŞÜ]+\b", re.UNICODE)


class DeterministicEmbedding:
    """Test/CI için öngörülebilir embedding (gerçek API yok).

    Token çakışmasına dayalı vektör: benzer metinler yüksek kosinüs benzerliği alır.
    """

    dimension: ClassVar[int] = 768

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector_for(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector_for(text)

    def _tokens(self, text: str) -> list[str]:
        return [w.lower() for w in _TOKEN_RE.findall(text) if len(w) > 2]

    def _vector_for(self, text: str) -> list[float]:
        tokens = self._tokens(text)
        if tokens:
            weight = 1.0 / math.sqrt(len(tokens))
            values = [0.0] * self.dimension
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                extra = hashlib.sha256(digest).digest()
                for blob in (digest, extra):
                    for offset in range(0, len(blob) - 3, 4):
                        idx = struct.unpack(">I", blob[offset : offset + 4])[0] % self.dimension
                        values[idx] += weight
            norm = math.sqrt(sum(v * v for v in values)) or 1.0
            return [v / norm for v in values]

        return self._hash_fallback_vector(text)

    def _hash_fallback_vector(self, text: str) -> list[float]:
        """Token yoksa tam metin hash vektörü."""
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < self.dimension:
            for i in range(0, len(seed) - 3, 4):
                raw = struct.unpack(">i", seed[i : i + 4])[0]
                values.append((raw % 10000) / 5000.0 - 1.0)
                if len(values) >= self.dimension:
                    break
            seed = hashlib.sha256(seed).digest()
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]
