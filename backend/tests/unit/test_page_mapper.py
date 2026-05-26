from app.domain.chunk import Chunk
from app.services.page_mapper import (
    assign_pages_from_document,
    _normalize,
    _parse_toc_page_map,
)


TOC_MARKDOWN = """**İÇİNDEKİLER** :

1.\tBÖLÜM TÜRKİYE'DE TRAFİK KURALLARI\t3

1.1. Yasal Dayanak ve Kapsam\t3

1.2. Temel Tanımlar\t3

2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI\t5

2.4. Durma ve Park Etme İşaretleri (P Grubu) \t8

3. BÖLÜM TRAFİK CEZALARI\t10

KAYNAKLAR\t13

## 1 BÖLÜM TÜRKİYE'DE TRAFİK KURALLARI

### 1.1. Yasal Dayanak ve Kapsam

İçerik bölüm 1.

## 2. BÖLÜM TRAFİK UYARI

### 2.4. Durma ve Park Etme İşaretleri (P Grubu)

İçerik bölüm 2.

## 3. BÖLÜM TRAFİK CEZALARI

Cezalar metni.
"""


def test_parse_toc_with_turkish_heading():
    toc = _parse_toc_page_map(TOC_MARKDOWN)
    assert len(toc) >= 6
    assert any(p == 3 for p in toc.values())
    assert any(p == 8 for p in toc.values())


def test_assign_pages_from_toc():
    chunks = [
        Chunk(text="içindekiler", chunk_index=0, page=1, section=None),
        Chunk(
            text="## 1 BÖLÜM",
            chunk_index=1,
            page=1,
            section="1 BÖLÜM TÜRKİYE'DE TRAFİK KURALLARI",
        ),
        Chunk(
            text="### 1.1. Yasal",
            chunk_index=2,
            page=1,
            section="1.1. Yasal Dayanak ve Kapsam",
        ),
        Chunk(
            text="## 2. BÖLÜM",
            chunk_index=3,
            page=1,
            section="2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI",
        ),
        Chunk(
            text="### 2.4. Durma",
            chunk_index=4,
            page=1,
            section="2.4. Durma ve Park Etme İşaretleri (P Grubu)",
        ),
        Chunk(
            text="## 3. BÖLÜM",
            chunk_index=5,
            page=1,
            section="3. BÖLÜM TRAFİK CEZALARI",
        ),
    ]
    assign_pages_from_document(TOC_MARKDOWN, chunks)
    assert chunks[1].page == 3
    assert chunks[2].page == 3
    assert chunks[3].page == 5
    assert chunks[4].page == 8
    assert chunks[5].page == 10
    assert all(c.paragraph is None for c in chunks)


def test_assign_pages_from_chunk0_toc_only():
    """TOC yalnızca ilk chunk'ta gömülüyse (tam markdown boş TOC)."""
    chunk0_text = """**İÇİNDEKİLER** :

1.\tBÖLÜM TÜRKİYE'DE TRAFİK KURALLARI\t3
1.1. Yasal Dayanak ve Kapsam\t4
2. BÖLÜM TRAFİK UYARI\t5
"""
    chunks = [
        Chunk(text=chunk0_text, chunk_index=0, page=1, section=None),
        Chunk(
            text="### 1.1. Yasal",
            chunk_index=1,
            page=1,
            section="1.1. Yasal Dayanak ve Kapsam",
        ),
        Chunk(
            text="## 2. BÖLÜM",
            chunk_index=2,
            page=1,
            section="2. BÖLÜM TRAFİK UYARI",
        ),
    ]
    assign_pages_from_document("", chunks)
    assert chunks[1].page == 4
    assert chunks[2].page == 5


PROJECT_TOC_CHUNK = """## Takım Üyeleri:

| 1 . GİRİŞ                                               |   3 |
|---------------------------------------------------------|-----|
| 2. Literatür Taraması                                   |   3 |
| 2.1. Executable and Linkable Format (ELF) İncelemesi    |   3 |
| 5. Linker Algoritması                                   |  11 |
| 8. Kaynakça                                             |  16 |
"""


def test_parse_markdown_table_toc():
    toc = _parse_toc_page_map(PROJECT_TOC_CHUNK)
    assert toc[_normalize("1 . GİRİŞ")] == 3
    assert toc[_normalize("5. Linker Algoritması")] == 11
    assert toc[_normalize("8. Kaynakça")] == 16


def test_assign_pages_from_embedded_markdown_table():
    """İçindekiler ayrı başlık olmadan chunk içi markdown tabloda."""
    chunks = [
        Chunk(text=PROJECT_TOC_CHUNK, chunk_index=3, page=1, section="Takım Üyeleri:"),
        Chunk(
            text="## 1 . GİRİŞ\n\nGiriş metni.",
            chunk_index=4,
            page=1,
            section="1 . GİRİŞ",
        ),
        Chunk(
            text="## 5. Linker Algoritması\n\nLinker.",
            chunk_index=5,
            page=1,
            section="5. Linker Algoritması",
        ),
        Chunk(
            text="## 8. Kaynakça\n\nKaynaklar.",
            chunk_index=6,
            page=1,
            section="8. Kaynakça",
        ),
    ]
    assign_pages_from_document("", chunks)
    assert chunks[1].page == 3
    assert chunks[2].page == 11
    assert chunks[3].page == 16


TRAFFIC_TOC_CHUNK = """## İÇİNDEKİLER :

| 1. BÖLÜM TÜRKİYE'DE TRAFİK KURALLARI........................................................3                                        |
|--------------------------------------------------------------------------------------------------------------------------------------|
| 1.1. Yasal Dayanak ve Kapsam..........................................................................................3              |
| 1.2. Temel Tanımlar...........................................................................................................3      |
| 1.3. Hız Kuralları ................................................................................................................4 |
| 1.4. Alkol ve Madde Kullanımı ..........................................................................................4            |
| 2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI.......................................5                                              |
| 2.1. Tehlike Uyarı İşaretleri (T Grubu)..............................................................................6               |
| 2.4. Durma ve Park Etme İşaretleri (P Grubu) ..................................................................8                     |
| 3. BÖLÜM TRAFİK CEZALARI.......................................................................................10                    |
| KAYNAKLAR....................................................................................................................13      |"""


def test_parse_dot_leader_table_toc():
    toc = _parse_toc_page_map(TRAFFIC_TOC_CHUNK)
    assert len(toc) >= 8
    assert toc[_normalize("1.1. Yasal Dayanak ve Kapsam")] == 3
    assert toc[_normalize("1.3. Hız Kuralları")] == 4
    assert toc[_normalize("2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI")] == 5
    assert toc[_normalize("2.4. Durma ve Park Etme İşaretleri (P Grubu)")] == 8
    assert toc[_normalize("3. BÖLÜM TRAFİK CEZALARI")] == 10
    assert toc[_normalize("KAYNAKLAR")] == 13


def test_assign_pages_from_dot_leader_toc_chunk():
    chunks = [
        Chunk(text=TRAFFIC_TOC_CHUNK, chunk_index=3, page=1, section="İÇİNDEKİLER :"),
        Chunk(
            text="## 1.1. Yasal Dayanak ve Kapsam\n\nMetin.",
            chunk_index=5,
            page=1,
            section="1.1. Yasal Dayanak ve Kapsam",
        ),
        Chunk(
            text="## 1.3. Hız Kuralları\n\nMetin.",
            chunk_index=7,
            page=1,
            section="1.3. Hız Kuralları",
        ),
        Chunk(
            text="## 2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI\n\nMetin.",
            chunk_index=9,
            page=1,
            section="2. BÖLÜM TRAFİK UYARI, İKAZ İŞARET VE LEVHALARI",
        ),
        Chunk(
            text="## 2.4. Durma ve Park Etme İşaretleri (P Grubu)\n\nMetin.",
            chunk_index=13,
            page=1,
            section="2.4. Durma ve Park Etme İşaretleri (P Grubu)",
        ),
        Chunk(
            text="## 3. BÖLÜM TRAFİK CEZALARI\n\nMetin.",
            chunk_index=15,
            page=1,
            section="3. BÖLÜM TRAFİK CEZALARI",
        ),
        Chunk(
            text="## KAYNAKLAR\n\nKaynak listesi.",
            chunk_index=17,
            page=1,
            section="KAYNAKLAR",
        ),
    ]
    assign_pages_from_document("", chunks)
    assert chunks[1].page == 3
    assert chunks[2].page == 4
    assert chunks[3].page == 5
    assert chunks[4].page == 8
    assert chunks[5].page == 10
    assert chunks[6].page == 13


def test_section_pages_override_toc():
    chunks = [
        Chunk(
            text="## 1.1. Yasal Dayanak ve Kapsam\n\nMetin.",
            chunk_index=1,
            page=1,
            section="1.1. Yasal Dayanak ve Kapsam",
        ),
    ]
    assign_pages_from_document(
        TOC_MARKDOWN,
        chunks,
        section_pages={"1.1. Yasal Dayanak ve Kapsam": 99},
    )
    assert chunks[0].page == 99
