"""A small, dependency-free BM25 (Okapi) index.

Why hand-rolled: the corpus fits in memory, the algorithm is ~60 lines, and
owning it means no extra dependency and full visibility into scoring. Built
from the chunks already in the vector store, so the two indexes can't drift.
"""

import math
import re
from collections import Counter

from ragkit.ingest.chunker import Chunk

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-\.]*")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, keeping in-word hyphens/dots (part numbers, SKUs)."""
    return _TOKEN_RE.findall(text.lower())


class BM25Index:
    """Okapi BM25 over chunk ``context_text`` (heading trail + body)."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self._chunks = chunks
        self._k1 = k1
        self._b = b
        self._doc_tokens = [Counter(tokenize(c.context_text)) for c in chunks]
        self._doc_lens = [sum(counts.values()) for counts in self._doc_tokens]
        self._avg_len = (sum(self._doc_lens) / len(self._doc_lens)) if chunks else 0.0
        doc_freq: Counter[str] = Counter()
        for counts in self._doc_tokens:
            doc_freq.update(counts.keys())
        n = len(chunks)
        self._idf = {
            term: math.log((n - df + 0.5) / (df + 0.5) + 1.0) for term, df in doc_freq.items()
        }
        self._terms_by_id = {
            chunk.id: set(counts) for chunk, counts in zip(chunks, self._doc_tokens, strict=True)
        }

    def informative_terms(self, query: str) -> list[str]:
        """Query terms rare enough to be retrieval-critical, rarest first.

        A term qualifies when it occurs in the corpus with an IDF of at least
        60% of a singleton term's IDF. Terms absent from the corpus entirely
        are excluded — nothing could cover them, and their absence is the
        grounding guard's business, not the retriever's.
        """
        if not self._chunks:
            return []
        n = len(self._chunks)
        floor = 0.6 * math.log((n - 0.5) / 1.5 + 1.0)
        terms = {(t, self._idf.get(t, 0.0)) for t in tokenize(query)}
        return [t for t, idf in sorted(terms, key=lambda x: -x[1]) if idf >= floor]

    def chunk_has_term(self, chunk_id: str, term: str) -> bool:
        """Whether the indexed chunk contains the token."""
        return term in self._terms_by_id.get(chunk_id, ())

    def coverage(self, query: str, texts: list[str]) -> float:
        """IDF-weighted fraction of query terms that occur in ``texts``.

        The second grounding signal: cosine similarity says "these chunks are
        about the same topic"; coverage says "the question's informative
        vocabulary actually occurs in them". Terms absent from the whole
        corpus get the maximum IDF, so a question hinging on a word the
        corpus never uses (an address, a revenue figure) scores low even
        when it names entities the corpus talks about constantly.
        """
        query_terms = set(tokenize(query))
        if not query_terms:
            return 0.0
        max_idf = math.log((len(self._chunks) + 0.5) / 0.5 + 1.0)
        present = set()
        for text in texts:
            present.update(tokenize(text))
        total = sum(self._idf.get(term, max_idf) for term in query_terms)
        covered = sum(self._idf.get(term, max_idf) for term in query_terms if term in present)
        return covered / total if total else 0.0

    def search(self, query: str, top_k: int = 10) -> list[tuple[Chunk, float]]:
        """Return (chunk, bm25 score) pairs, best first, zero-score hits dropped."""
        query_terms = tokenize(query)
        scored: list[tuple[Chunk, float]] = []
        for chunk, counts, doc_len in zip(
            self._chunks, self._doc_tokens, self._doc_lens, strict=True
        ):
            score = 0.0
            for term in query_terms:
                tf = counts.get(term, 0)
                if tf == 0:
                    continue
                idf = self._idf.get(term, 0.0)
                denom = tf + self._k1 * (1 - self._b + self._b * doc_len / self._avg_len)
                score += idf * tf * (self._k1 + 1) / denom
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
