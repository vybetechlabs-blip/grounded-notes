"""Assemble retrieved chunks into a context block with source attribution.

The block format is shared by every generation path (extractive and LLM):
chunks arrive clearly delimited and labeled with a citation number, source
path, and heading trail, so answers can cite real locations.
"""

from ragkit.store.chroma import RetrievedChunk


def assemble_context(results: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as numbered, source-labeled context blocks."""
    blocks = [
        f"[{i}] {r.chunk.source} — {r.chunk.heading}\n{r.chunk.text}"
        for i, r in enumerate(results, start=1)
    ]
    return "\n\n---\n\n".join(blocks)
