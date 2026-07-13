"""Hybrid retrieval: BM25 + vector search fused with reciprocal-rank fusion.

Corpora are full of exact tokens that matter — part numbers, names, error
strings. Vector similarity smears these; BM25 nails them but misses
paraphrase. RRF fuses the two rankings without any score normalization
gymnastics: each candidate scores sum(1 / (k + rank)) across the lists it
appears in.

Ranking and confidence are deliberately separated: RRF decides the *order*,
but every returned chunk's ``score`` is its true cosine similarity to the
query, so the grounding threshold keeps a stable, interpretable meaning.
"""

from ragkit.embed.base import EmbeddingProvider
from ragkit.ingest.chunker import Chunk
from ragkit.retrieve.bm25 import BM25Index
from ragkit.store.chroma import ChromaStore, RetrievedChunk

_RRF_K = 60
_CANDIDATE_MULTIPLIER = 3
"""Each leg retrieves top_k * this many candidates before fusion."""


class HybridRetriever:
    """Fuses BM25 and vector rankings; scores stay cosine similarities."""

    def __init__(self, store: ChromaStore, embedder: EmbeddingProvider) -> None:
        self._store = store
        self._embedder = embedder
        self._bm25: BM25Index | None = None
        self._bm25_count = -1

    def _bm25_index(self) -> BM25Index:
        count = self._store.count()
        if self._bm25 is None or self._bm25_count != count:
            self._bm25 = BM25Index(self._store.all_chunks())
            self._bm25_count = count
        return self._bm25

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return top-k chunks by RRF rank, scored by cosine similarity."""
        n_candidates = top_k * _CANDIDATE_MULTIPLIER
        query_vec = self._embedder.embed_query(query)

        vector_hits = self._store.query(query_vec, top_k=n_candidates)
        bm25_hits = self._bm25_index().search(query, top_k=n_candidates)

        chunks: dict[str, Chunk] = {}
        rrf: dict[str, float] = {}
        cosine: dict[str, float] = {}

        for rank, hit in enumerate(vector_hits, start=1):
            chunks[hit.chunk.id] = hit.chunk
            rrf[hit.chunk.id] = rrf.get(hit.chunk.id, 0.0) + 1.0 / (_RRF_K + rank)
            cosine[hit.chunk.id] = hit.score
        for rank, (chunk, _score) in enumerate(bm25_hits, start=1):
            chunks[chunk.id] = chunk
            rrf[chunk.id] = rrf.get(chunk.id, 0.0) + 1.0 / (_RRF_K + rank)

        missing = [cid for cid in chunks if cid not in cosine]
        cosine.update(self._store.similarities(missing, query_vec))

        ordered = sorted(rrf, key=lambda cid: rrf[cid], reverse=True)
        selected = self._ensure_term_coverage(query, ordered, top_k)
        return [
            RetrievedChunk(chunk=chunks[cid], score=cosine.get(cid, 0.0)) for cid in selected
        ]

    def _ensure_term_coverage(self, query: str, ordered: list[str], top_k: int) -> list[str]:
        """Guarantee the top-k covers the query's most informative term.

        Measured failure this prevents: a rare query term ("discounts") whose
        chunk BM25 ranks highly gets drowned in RRF by chunks matching common
        terms (the company name) on both legs. If the cut top-k entirely
        lacks the rarest informative query term and a lower-ranked candidate
        has it, that candidate replaces the weakest selection. One swap, one
        term — retrieval tries to satisfy the same coverage signal the
        grounding guard will demand.
        """
        selected = list(ordered[:top_k])
        index = self._bm25_index()
        for term in index.informative_terms(query):
            if any(index.chunk_has_term(cid, term) for cid in selected):
                continue
            champion = next(
                (cid for cid in ordered[top_k:] if index.chunk_has_term(cid, term)), None
            )
            if champion is not None:
                selected[-1] = champion
            break
        return selected

    def coverage(self, query: str, results: list[RetrievedChunk]) -> float:
        """IDF-weighted query-term coverage of the retrieved chunks (0..1)."""
        return self._bm25_index().coverage(query, [r.chunk.context_text for r in results])
