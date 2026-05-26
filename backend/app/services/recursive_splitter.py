from app.domain.chunk import Chunk
from app.services.structural_chunker import TextBlock
from app.services.token_utils import estimate_tokens, take_last_tokens


class RecursiveSplitter:
    """Uzun blokları token sınırına göre parçalar; overlap uygular."""

    def __init__(self, max_tokens: int = 512, overlap_ratio: float = 0.15):
        self._max_tokens = max_tokens
        self._overlap_ratio = overlap_ratio

    def split_blocks(
        self,
        blocks: list[TextBlock],
        page_count: int = 1,
    ) -> list[Chunk]:
        """Yapısal blokları chunk listesine dönüştürür."""
        chunks: list[Chunk] = []
        index = 0
        for block in blocks:
            for part in self._split_text(block.text):
                if not part.strip():
                    continue
                chunks.append(
                    Chunk(
                        text=part.strip(),
                        chunk_index=index,
                        page=1,
                        section=block.section,
                        paragraph=None,
                    )
                )
                index += 1
        return chunks

    def _split_text(self, text: str) -> list[str]:
        """Tek metin bloğunu max_tokens altında parçalara ayırır."""
        if estimate_tokens(text) <= self._max_tokens:
            return [text]

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return self._split_by_words(text)

        merged: list[str] = []
        buffer = ""
        for para in paragraphs:
            candidate = f"{buffer}\n\n{para}".strip() if buffer else para
            if estimate_tokens(candidate) <= self._max_tokens:
                buffer = candidate
            else:
                if buffer:
                    merged.append(buffer)
                if estimate_tokens(para) > self._max_tokens:
                    merged.extend(self._split_by_words(para))
                    buffer = ""
                else:
                    buffer = para
        if buffer:
            merged.append(buffer)

        return self._apply_overlap(merged)

    def _split_by_words(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []
        step = max(1, self._max_tokens)
        return [
            " ".join(words[i : i + step])
            for i in range(0, len(words), step)
            if words[i : i + step]
        ]

    def _apply_overlap(self, parts: list[str]) -> list[str]:
        if len(parts) < 2:
            return parts

        overlap_tokens = max(1, int(self._max_tokens * self._overlap_ratio))
        result = [parts[0]]
        for i in range(1, len(parts)):
            prefix = take_last_tokens(parts[i - 1], overlap_tokens)
            merged = f"{prefix}\n\n{parts[i]}".strip() if prefix else parts[i]
            result.append(merged)
        return result
