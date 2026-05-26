import logging

from app.infrastructure.gemini_llm import GeminiLLM
from app.ports.chunk_enrichment import ChunkEnrichmentPort

_log = logging.getLogger(__name__)

_ENRICH_PROMPT = """Sen bir doküman yapılandırma uzmanısın. Aşağıdaki markdown metni PDF ayrıştırıcıdan gelmiştir.
Görevin:
1. Yanlış veya tekrarlayan bölüm başlıklarını (sayfa üstbilgisi gibi) kaldır veya düzelt.
2. Çok sayfaya bölünmüş tabloların satırlarını bütünleştir (markdown tablo sözdizimini koru).
3. H1/H2 hiyerarşisini anlamlı hale getir.
4. Sadece düzeltilmiş markdown döndür; açıklama ekleme.

Belge adı: {document_name}

---
{markdown}
"""


class ContextualChunkEnricher:
    """Bağlamsal bölütleme via LLM (rapor §3.1 Contextual Chunking)."""

    def __init__(
        self,
        llm: GeminiLLM,
        max_input_chars: int = 24_000,
    ):
        self._llm = llm
        self._max_input_chars = max_input_chars

    def enrich(self, markdown: str, document_name: str = "") -> str:
        if not markdown.strip():
            return markdown

        body = markdown[: self._max_input_chars]
        if len(markdown) > self._max_input_chars:
            _log.warning(
                "LLM chunk enrich kısaltıldı: %d -> %d karakter",
                len(markdown),
                self._max_input_chars,
            )

        prompt = _ENRICH_PROMPT.format(
            document_name=document_name or "belge",
            markdown=body,
        )
        result = self._llm.generate(prompt, temperature=0.1)
        return result if result else markdown
