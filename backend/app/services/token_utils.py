import re

_WORD_RE = re.compile(r"\S+")


def estimate_tokens(text: str) -> int:
    """Yaklaşık token sayısı (kelime tabanlı, testlerle uyumlu)."""
    if not text.strip():
        return 0
    return len(_WORD_RE.findall(text))


def take_last_tokens(text: str, token_count: int) -> str:
    """Metnin son N token'ını döner."""
    words = _WORD_RE.findall(text)
    if token_count <= 0 or not words:
        return ""
    return " ".join(words[-token_count:])
