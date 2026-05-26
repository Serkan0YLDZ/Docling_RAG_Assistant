import re
import unicodedata

from app.domain.chunk import Chunk

_TOC_ENTRY = re.compile(
    r"^(?:\d+(?:\.\d+)*)?\s*(.+?)[\t ]+(\d+)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_TOC_TAB_PAIR = re.compile(r"([^\n\t]+?)\t(\d+)\b")
_TOC_TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|?\s*$")
_TOC_TABLE_SEP = re.compile(r"^\|[\s\-:|]+\|\s*$")
_TOC_DOT_LEADER = re.compile(
    r"^(.+?)(?:[.\u00b7·…]{2,}|\s{4,})(\d+)\s*$",
    re.UNICODE,
)
_HEADING_IN_TEXT = re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE)
_MIN_TOC_ENTRIES = 3


def _fold(text: str) -> str:
    """Türkçe İ/ı dahil karşılaştırma için ASCII-benzeri küçük harf."""
    folded = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in folded if not unicodedata.combining(c))


def _normalize(title: str) -> str:
    text = _fold(title.strip())
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"^\d+\s*\.\s*", "", text)
    while True:
        stripped = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text)
        if stripped == text:
            break
        text = stripped
    text = re.sub(r"^\d+\s+(?!\.)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_toc_heading(line: str) -> bool:
    compact = re.sub(r"[\s\*:#.]+", "", _fold(line))
    return "icindekiler" in compact


def _is_table_header_cell(title: str) -> bool:
    folded = _fold(title)
    return folded in {
        "bolum",
        "baslik",
        "title",
        "konu",
        "icerik",
        "sayfa",
        "page",
        "nr",
        "name",
    }


def _parse_dot_leader_toc_line(content: str) -> tuple[str, int] | None:
    """Tek hücreli içindekiler satırı: '1. GİRİŞ .............. 3'."""
    content = content.strip()
    if not content or _is_table_header_cell(content):
        return None
    match = _TOC_DOT_LEADER.match(content)
    if not match:
        return None
    title, page_str = match.group(1).strip(), match.group(2)
    if not title or len(title) < 3:
        return None
    return title, int(page_str)


def _store_toc_entry(pages: dict[str, int], title: str, page: int) -> None:
    if re.fullmatch(r"[-:]+", title):
        return
    pages[_normalize(title)] = page


def _parse_toc_markdown_tables(text: str) -> dict[str, int]:
    """Docling/OCR markdown tablo içindekiler: | 1 . GİRİŞ | 3 | veya | 1 . GİRİŞ...3 |"""
    pages: dict[str, int] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or _TOC_TABLE_SEP.match(line):
            continue
        match = _TOC_TABLE_ROW.match(line)
        if match:
            title, page_str = match.group(1).strip(), match.group(2)
            if title and not _is_table_header_cell(title):
                _store_toc_entry(pages, title, int(page_str))
            continue
        inner = line.strip("|").strip()
        parsed = _parse_dot_leader_toc_line(inner)
        if parsed:
            _store_toc_entry(pages, parsed[0], parsed[1])
    return pages


def _parse_toc_page_map(text: str) -> dict[str, int]:
    """İçindekiler tablosundan bölüm → sayfa eşlemesi."""
    pages: dict[str, int] = {}

    table_pages = _parse_toc_markdown_tables(text)
    pages.update(table_pages)

    in_toc = bool(table_pages)
    for line in text.splitlines():
        if _is_toc_heading(line):
            in_toc = True
            continue
        if in_toc and line.strip().startswith("## ") and "bolum" not in _fold(line):
            break
        if not in_toc:
            continue
        stripped = line.strip()
        match = _TOC_ENTRY.match(stripped)
        if match:
            _store_toc_entry(pages, match.group(1).strip(), int(match.group(2)))
            continue
        parsed = _parse_dot_leader_toc_line(stripped.lstrip("|").rstrip("|").strip())
        if parsed:
            _store_toc_entry(pages, parsed[0], parsed[1])

    if not pages:
        for title, page_str in _TOC_TAB_PAIR.findall(text):
            title = title.strip()
            if not title or len(title) < 3:
                continue
            _store_toc_entry(pages, title, int(page_str))

    return pages


def _lookup_page(section: str | None, toc: dict[str, int]) -> int | None:
    if not section or not toc:
        return None
    key = _normalize(section)
    if key in toc:
        return toc[key]
    for toc_key, page in toc.items():
        if not toc_key or not key:
            continue
        if key in toc_key or toc_key in key:
            return page
    section_folded = _fold(section)
    num_match = re.search(r"(\d+(?:\.\d+)*)", section_folded)
    if num_match:
        prefix = num_match.group(1)
        best: tuple[int, int] | None = None
        for toc_key, page in toc.items():
            toc_num = re.search(r"(\d+(?:\.\d+)*)", toc_key.replace(" ", ""))
            if not toc_num:
                continue
            if toc_num.group(1) == prefix or toc_num.group(1).startswith(prefix + "."):
                score = len(toc_key)
                if best is None or score > best[0]:
                    best = (score, page)
        if best:
            return best[1]
    return None


def _merge_toc(into: dict[str, int], extra: dict[str, int]) -> dict[str, int]:
    if len(extra) > len(into):
        into = {**into, **extra}
    else:
        into.update(extra)
    return into


def _build_toc(
    markdown: str,
    chunks: list[Chunk],
    section_pages: dict[str, int] | None = None,
) -> dict[str, int]:
    toc = _parse_toc_page_map(markdown)
    for chunk in chunks:
        if not chunk.text:
            continue
        partial = _parse_toc_page_map(chunk.text)
        if len(partial) >= _MIN_TOC_ENTRIES or (
            len(partial) > len(toc) and len(partial) >= 2
        ):
            toc = partial if len(partial) > len(toc) else _merge_toc(toc, partial)
    if section_pages:
        for title, page in section_pages.items():
            toc[_normalize(title)] = page
    return toc


def build_section_pages_from_docling(doc) -> dict[str, int]:
    """Docling provenance ile başlık sayfa eşlemesi (PDF/DOCX için birincil kaynak)."""
    from docling_core.types.doc.labels import DocItemLabel

    header_labels = {
        DocItemLabel.SECTION_HEADER,
        DocItemLabel.TITLE,
    }
    pages: dict[str, int] = {}
    seen_page_nos: list[int] = []
    for item, _level in doc.iterate_items():
        label = getattr(item, "label", None)
        if label not in header_labels:
            continue
        prov = getattr(item, "prov", None)
        text = getattr(item, "text", None)
        if not prov or not text or not text.strip():
            continue
        page_no = prov[0].page_no
        if page_no is None:
            continue
        page_int = int(page_no)
        seen_page_nos.append(page_int)
        pages[text.strip()] = page_int

    if pages and seen_page_nos and min(seen_page_nos) == 0:
        pages = {title: page + 1 for title, page in pages.items()}
    return pages


def assign_pages_from_document(
    markdown: str,
    chunks: list[Chunk],
    section_pages: dict[str, int] | None = None,
) -> None:
    """Chunk'lara Docling provenance ve/veya içindekilerden sayfa numarası atar."""
    toc = _build_toc(markdown, chunks, section_pages)
    current_page = 1

    for chunk in chunks:
        page = _lookup_page(chunk.section, toc)
        if page is None and chunk.text:
            for match in _HEADING_IN_TEXT.finditer(chunk.text):
                page = _lookup_page(match.group(1).strip(), toc)
                if page:
                    break
        if page is not None:
            current_page = page
        chunk.page = max(1, int(current_page))
        chunk.paragraph = None
