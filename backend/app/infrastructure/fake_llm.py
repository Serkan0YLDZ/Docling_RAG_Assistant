"""Test ortamı için deterministik LLM yanıtı."""


class FakeLLM:
    """RAG ve birim testlerinde gerçek API çağrısı yapmaz."""

    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        grounded = "Ar-Ge yatirimlari en buyuk harcama kalemidir [1]."
        if "SOHBET GEÇMİŞİ:" in prompt:
            return f"Önceki mesajlarınızı dikkate alarak: {grounded}"
        return grounded
