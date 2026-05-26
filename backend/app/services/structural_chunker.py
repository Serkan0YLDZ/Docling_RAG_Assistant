import re
from dataclasses import dataclass

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass
class TextBlock:
    """Başlık hiyerarşisine göre ayrılmış blok."""

    section: str | None
    text: str
    level: int = 0


class StructuralChunker:
    """Markdown başlıklarına (H1–H6) göre yapısal bölütleme."""

    def split(self, markdown: str) -> list[TextBlock]:
        """Metni başlık sınırlarında böler."""
        lines = markdown.splitlines()
        blocks: list[TextBlock] = []
        current_section: str | None = None
        current_level = 0
        buffer: list[str] = []

        def flush() -> None:
            nonlocal buffer
            body = "\n".join(buffer).strip()
            if body:
                blocks.append(
                    TextBlock(
                        section=current_section,
                        text=body,
                        level=current_level,
                    )
                )
            buffer = []

        for line in lines:
            match = _HEADING_RE.match(line.strip())
            if match:
                flush()
                current_level = len(match.group(1))
                current_section = match.group(2).strip()
                buffer = [line]
            else:
                buffer.append(line)

        flush()

        if not blocks and markdown.strip():
            blocks.append(TextBlock(section=None, text=markdown.strip()))

        return blocks
