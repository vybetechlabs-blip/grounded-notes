"""Citations: file + heading references attached to every answer."""

from pydantic import BaseModel

from ragkit.store.chroma import RetrievedChunk


class Citation(BaseModel):
    """A pointer into the corpus: source file, heading trail, and score."""

    number: int
    source: str
    heading: str
    score: float

    def render(self) -> str:
        """Human-readable one-liner, e.g. ``[2] sops/x.md — Title > Steps``."""
        return f"[{self.number}] {self.source} — {self.heading}"


def citations_from_results(results: list[RetrievedChunk]) -> list[Citation]:
    """Number retrieved chunks in rank order; numbering matches the context block."""
    return [
        Citation(number=i, source=r.chunk.source, heading=r.chunk.heading, score=r.score)
        for i, r in enumerate(results, start=1)
    ]
