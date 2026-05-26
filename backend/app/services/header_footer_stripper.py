import re
from collections import Counter


class HeaderFooterStripper:
    """Tekrarlayan üst/alt bilgi satırlarını metinden çıkarır."""

    def __init__(self, min_repeats: int = 3, max_line_len: int = 120):
        self._min_repeats = min_repeats
        self._max_line_len = max_line_len

    def strip(self, text: str) -> str:
        """Sık tekrarlanan kısa satırları kaldırır."""
        lines = text.splitlines()
        normalized = [
            line.strip()
            for line in lines
            if line.strip() and len(line.strip()) <= self._max_line_len
        ]
        if len(normalized) < self._min_repeats:
            return text

        counts = Counter(normalized)
        noise = {
            line
            for line, count in counts.items()
            if count >= self._min_repeats
            and not line.startswith("#")
        }
        if not noise:
            return text

        cleaned: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped in noise:
                continue
            cleaned.append(line)
        return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()
