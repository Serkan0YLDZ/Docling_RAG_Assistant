class NoOpChunkEnricher:
    """LLM zenginleştirme kapalıyken metni olduğu gibi geçirir."""

    def enrich(self, markdown: str, document_name: str = "") -> str:
        return markdown
