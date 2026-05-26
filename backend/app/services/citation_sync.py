import re

_REF_PATTERN = re.compile(r"\[\s*(\d+)\s*\]")


def extract_ref_indices(text: str) -> list[int]:
    """Metinde geçen benzersiz [n] referansları (sırayla)."""
    seen: set[int] = set()
    ordered: list[int] = []
    for match in _REF_PATTERN.finditer(text):
        ref = int(match.group(1))
        if ref not in seen:
            seen.add(ref)
            ordered.append(ref)
    return ordered


def append_sources_footer(content: str, citations: list[dict]) -> str:
    """Tüm kaynakları cevap sonuna ekler (panel ile uyumlu atıf satırları)."""
    if not citations:
        return content.strip()
    body = content.strip()
    if "**Kaynaklar:**" in body:
        return body
    lines = ["", "**Kaynaklar:**"]
    for citation in sorted(citations, key=lambda c: c["refIndex"]):
        line = f"[{citation['refIndex']}] Sayfa {citation['page']}"
        section = citation.get("section")
        if section:
            line += f" — {section}"
        lines.append(line)
    return body + "\n".join(lines)


def strip_invalid_refs(content: str, valid_refs: set[int]) -> str:
    """Bağlamda olmayan [n] referanslarını kaldırır."""
    if not valid_refs:
        return content

    def repl(match: re.Match) -> str:
        ref = int(match.group(1))
        return match.group(0) if ref in valid_refs else ""

    return _REF_PATTERN.sub(repl, content)
