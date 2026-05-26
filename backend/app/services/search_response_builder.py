import re
from uuid import uuid4

from app.constants import messages
from app.domain.search_hit import SearchHit
from app.services.citation_sync import append_sources_footer

_SNIPPET_LEN = 160


class SearchResponseBuilder:
    """Arama / RAG sonuçlarını frontend QueryResponse DTO'suna çevirir."""

    def build_no_context(self) -> dict:
        return {
            "message": {
                "id": f"msg-{uuid4()}",
                "role": "assistant",
                "content": messages.NO_CONTEXT_ACTIVITY,
            },
            "sources": [],
        }

    def build_sources_and_citations(
        self, hits: list[SearchHit]
    ) -> tuple[list[dict], list[dict]]:
        sources: list[dict] = []
        citations: list[dict] = []
        for ref_index, hit in enumerate(hits, start=1):
            snippet = _snippet_from_text(hit.text)
            sources.append(
                {
                    "documentId": hit.document_id,
                    "documentName": hit.document_name,
                    "page": hit.page,
                    "section": hit.section,
                    "highlightText": snippet,
                    "refIndex": ref_index,
                }
            )
            citations.append(
                {
                    "refIndex": ref_index,
                    "page": hit.page,
                    "section": hit.section,
                    "excerpt": snippet,
                }
            )
        return sources, citations

    def build_search_summary(self, hits: list[SearchHit]) -> dict:
        """B4 şablon özeti (LLM yok)."""
        if not hits:
            return self.build_no_context()
        sources, citations = self.build_sources_and_citations(hits)
        summary = (
            f"Belgelerinizde {len(hits)} ilgili parça bulundu. "
            "Kaynak panelinden inceleyebilirsiniz.\n\n"
        )
        for c in citations:
            summary += f"[{c['refIndex']}] Sayfa {c['page']}"
            if c.get("section"):
                summary += f" — {c['section']}"
            summary += "\n"
        return {
            "message": {
                "id": f"msg-{uuid4()}",
                "role": "assistant",
                "content": summary.strip(),
                "citations": citations,
            },
            "sources": sources,
        }

    def build_rag_answer(
        self,
        hits: list[SearchHit],
        llm_text: str,
    ) -> dict:
        """LLM yanıtı + kaynak kartları (tüm parçalar panelde ve Kaynaklar satırında)."""
        if not hits:
            return self.build_no_context()
        sources, citations = self.build_sources_and_citations(hits)
        content = append_sources_footer(llm_text, citations)
        return {
            "message": {
                "id": f"msg-{uuid4()}",
                "role": "assistant",
                "content": content,
                "citations": citations,
            },
            "sources": sources,
        }

    def build(self, hits: list[SearchHit]) -> dict:
        return self.build_search_summary(hits)


def _snippet_from_text(text: str, max_len: int = _SNIPPET_LEN) -> str:
    """Kaynak kartında gösterilecek kısa alıntı."""
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_len:
        return cleaned
    cut = cleaned[:max_len]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"
