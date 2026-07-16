"""Keyless default answerer: extractive, so a fresh clone never hard-crashes.

Rather than generating text, it selects the sentences from the retrieved
chunks most similar to the question and quotes them with citation markers.
Less fluent than an LLM, but zero-cost, zero-key, and incapable of saying
anything the corpus doesn't say.

Markdown tables get special handling: flattening them into a "sentence"
destroys their line structure, and a table nested inside a bullet doesn't
render anyway (tables must start at column zero with blank lines around
them). Table-shaped content is therefore kept intact and emitted as its own
block, with the citation marker on an adjacent attribution line.
"""

import re

from ragkit.embed.base import EmbeddingProvider
from ragkit.store.chroma import RetrievedChunk

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|$")
_MAX_QUOTES = 4
_MIN_CANDIDATE_CHARS = 30


class ExtractiveAnswerer:
    """Selects and quotes the most relevant sentences from retrieved chunks."""

    def __init__(self, embedder: EmbeddingProvider) -> None:
        self._embedder = embedder

    @property
    def name(self) -> str:
        return "extractive"

    def answer(self, question: str, results: list[RetrievedChunk]) -> str:
        # Candidates: (kind, render_text, score_text, citation number).
        candidates: list[tuple[str, str, str, int]] = []
        for number, result in enumerate(results, start=1):
            for kind, segment in _split_segments(result.chunk.text):
                flat = re.sub(r"\s+", " ", segment).strip()
                if kind == "table":
                    if len(flat) >= _MIN_CANDIDATE_CHARS:
                        candidates.append((kind, segment, flat, number))
                    continue
                for sentence in _SENTENCE_RE.split(flat):
                    sentence = sentence.strip("-• ").strip()
                    if len(sentence) >= _MIN_CANDIDATE_CHARS:
                        candidates.append(("sentence", sentence, sentence, number))
        if not candidates:
            return "The retrieved documents contain no quotable content."

        query_vec = self._embedder.embed_query(question)
        vectors = self._embedder.embed_texts([c[2] for c in candidates])
        scored = sorted(
            zip(candidates, vectors, strict=True),
            key=lambda pair: _dot(query_vec, pair[1]),
            reverse=True,
        )

        blocks: list[str] = []
        seen: set[str] = set()
        for (kind, render_text, score_text, number), _vec in scored:
            key = score_text.lower()
            if key in seen:
                continue
            seen.add(key)
            if kind == "table":
                # Tables render at column zero with blank lines around them;
                # the citation marker rides on an adjacent attribution line.
                blocks.append(f"\n{render_text}\n\n*Table from [{number}]*\n")
            else:
                blocks.append(f"- {render_text} [{number}]")
            if len(blocks) >= _MAX_QUOTES:
                break
        return "From the knowledge base:\n\n" + "\n".join(blocks)


def _split_segments(text: str) -> list[tuple[str, str]]:
    """Split chunk text into ("table" | "prose", segment) parts, in order.

    A table is two or more consecutive ``|``-prefixed lines that include a
    markdown separator row (``| --- | --- |``). Pipe-prefixed lines without a
    separator row are treated as prose.
    """
    segments: list[tuple[str, str]] = []
    prose: list[str] = []

    def flush_prose() -> None:
        body = "\n".join(prose).strip()
        if body:
            segments.append(("prose", body))
        prose.clear()

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            block = [line.strip() for line in lines[i:j]]
            if len(block) >= 2 and any(_TABLE_SEPARATOR_RE.match(b) for b in block):
                flush_prose()
                segments.append(("table", "\n".join(block)))
            else:
                prose.extend(block)
            i = j
        else:
            prose.append(lines[i])
            i += 1
    flush_prose()
    return segments


def _dot(a: list[float], b: list[float]) -> float:
    """Dot product (vectors are unit-normalized, so this is cosine similarity)."""
    return sum(x * y for x, y in zip(a, b, strict=True))
