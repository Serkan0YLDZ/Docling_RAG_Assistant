from typing import Protocol


class LLMPort(Protocol):
    """Dış LLM ile metin üretimi."""

    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        """Prompt için model yanıtı üretir."""
        ...
