import re


class FakeChunkEnricher:
    """Test için deterministik markdown düzeltmeleri."""

    def enrich(self, markdown: str, document_name: str = "") -> str:
        text = markdown
        text = text.replace("WRONG_SECTION_TITLE", "Doğru Bölüm Başlığı")
        text = re.sub(
            r"^##\s*Sayfa\s*Üstbilgi\s*$",
            "",
            text,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        return text.strip()
