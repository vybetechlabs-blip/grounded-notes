"""Optional cross-encoder reranking of the fused candidate list.

Why it exists (measured, not speculative): on the eval set, the query
"Which discounts does Lanternfish offer?" embeds far from its answer chunk
(bi-encoder cosine 0.18 — "discounts" vs "fee credited / 15% off" is a
paraphrase gap), while BM25 ranks that chunk #3; reciprocal-rank fusion
alone still drowned it below the top-5. A cross-encoder reads the query and
chunk *together* and bridges exactly this gap. Still local, CPU, keyless.

Ordering comes from the cross-encoder; each chunk's ``score`` stays its
bi-encoder cosine similarity so the grounding threshold keeps one meaning.
"""

from functools import cached_property
from typing import Any

from ragkit.store.chroma import RetrievedChunk


class CrossEncoderReranker:
    """Reorders retrieved chunks by cross-encoder relevance."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model_name = model_name

    @property
    def name(self) -> str:
        return self._model_name

    @cached_property
    def _model(self) -> Any:
        from sentence_transformers import CrossEncoder

        return CrossEncoder(self._model_name, device="cpu")

    def rerank(self, query: str, results: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Return ``results`` reordered by cross-encoder score, best first."""
        if len(results) <= 1:
            return results
        pairs = [(query, r.chunk.context_text) for r in results]
        scores = self._model.predict(pairs)
        order = sorted(range(len(results)), key=lambda i: float(scores[i]), reverse=True)
        return [results[i] for i in order]
