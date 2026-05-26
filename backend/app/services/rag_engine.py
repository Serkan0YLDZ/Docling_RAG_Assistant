import logging

from app.domain.search_hit import SearchHit
from app.ports.llm import LLMPort
from app.services.citation_sync import append_sources_footer, strip_invalid_refs
from app.services.query_pipeline import QueryPipeline
from app.services.rag_prompt import build_rag_prompt
from app.services.search_response_builder import SearchResponseBuilder

_log = logging.getLogger(__name__)

_CONTEXT_CHAR_LIMIT = 12000


class RAGEngine:
    """RAG: retrieval + sohbet geçmişi + LLM (§3.3)."""

    def __init__(
        self,
        pipeline: QueryPipeline,
        llm: LLMPort,
        response_builder: SearchResponseBuilder,
        max_history_turns: int = 10,
        temperature: float = 0.2,
    ):
        self._pipeline = pipeline
        self._llm = llm
        self._builder = response_builder
        self._max_history_turns = max(1, max_history_turns)
        self._temperature = temperature

    def generate(
        self,
        message: str,
        document_ids: list[str] | None,
        history: list[dict],
    ) -> dict:
        hits = self._pipeline.retrieve_hits(message, document_ids)
        if not hits:
            return self._builder.build_no_context()

        context_blocks, included_hits = self._context_blocks(hits)
        if not included_hits:
            return self._builder.build_no_context()

        prompt = build_rag_prompt(
            context_blocks,
            history[-self._max_history_turns * 2 :],
            message,
        )
        answer = self._llm.generate(prompt, temperature=self._temperature)
        valid_refs = set(range(1, len(included_hits) + 1))
        answer = strip_invalid_refs(answer, valid_refs)
        _log.info("RAG yanıt üretildi (%d kaynak parçası)", len(included_hits))
        return self._builder.build_rag_answer(included_hits, answer)

    def _context_blocks(
        self, hits: list[SearchHit]
    ) -> tuple[list[tuple[int, str]], list[SearchHit]]:
        """Prompt'a giren parçalar; ref 1..N sıralı (panel ile aynı)."""
        blocks: list[tuple[int, str]] = []
        included: list[SearchHit] = []
        total = 0

        for hit in hits:
            text = hit.text.strip()
            if not text:
                continue

            ref_index = len(blocks) + 1
            if total + len(text) > _CONTEXT_CHAR_LIMIT:
                remaining = _CONTEXT_CHAR_LIMIT - total
                if remaining > 200:
                    blocks.append((ref_index, text[:remaining] + "…"))
                    included.append(hit)
                break

            blocks.append((ref_index, text))
            included.append(hit)
            total += len(text)

        return blocks, included
