"""Keyless default answerer: extractive, so a fresh clone never hard-crashes.

Rather than generating text, it selects the sentences from the retrieved
chunks most similar to the question and quotes them with citation markers.
Less fluent than an LLM, but zero-cost, zero-key, and incapable of saying
anything the corpus doesn't say.
"""

import re

from ragkit.embed.base import EmbeddingProvider
from ragkit.store.chroma import RetrievedChunk

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_MAX_SENTENCES = 4
_MIN_SENTENCE_CHARS = 30


class ExtractiveAnswerer:
    """Selects and quotes the most relevant sentences from retrieved chunks."""

    def __init__(self, embedder: EmbeddingProvider) -> None:
        self._embedder = embedder

    @property
    def name(self) -> str:
        return "extractive"

    def answer(self, question: str, results: list[RetrievedChunk]) -> str:
        candidates: list[tuple[str, int]] = []  # (sentence, citation number)
        for number, result in enumerate(results, start=1):
            flat = re.sub(r"\s+", " ", result.chunk.text)
            for sentence in _SENTENCE_RE.split(flat):
                sentence = sentence.strip("-• ").strip()
                if len(sentence) >= _MIN_SENTENCE_CHARS:
                    candidates.append((sentence, number))
        if not candidates:
            return "The retrieved documents contain no quotable content."

        query_vec = self._embedder.embed_query(question)
        sentence_vecs = self._embedder.embed_texts([s for s, _ in candidates])
        scored = sorted(
            zip(candidates, sentence_vecs, strict=True),
            key=lambda pair: _dot(query_vec, pair[1]),
            reverse=True,
        )

        lines: list[str] = []
        seen: set[str] = set()
        for (sentence, number), _vec in scored:
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"- {sentence} [{number}]")
            if len(lines) >= _MAX_SENTENCES:
                break
        return "From the knowledge base:\n\n" + "\n".join(lines)


def _dot(a: list[float], b: list[float]) -> float:
    """Dot product (vectors are unit-normalized, so this is cosine similarity)."""
    return sum(x * y for x, y in zip(a, b, strict=True))
