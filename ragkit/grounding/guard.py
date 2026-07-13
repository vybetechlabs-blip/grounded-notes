"""The grounding hard-fail.

An assistant that answers everything is worse than no assistant: users can't
tell confident-right from confident-wrong. If the best retrieval score falls
below a threshold, the pipeline refuses instead of generating — and says what
it *did* find, so the refusal is still useful.
"""

from pydantic import BaseModel

from ragkit.store.chroma import RetrievedChunk

REFUSAL_TEXT = (
    "I don't have that in the knowledge base. "
    "The closest documents I found are listed below, but none of them "
    "answer the question confidently."
)


class GroundingDecision(BaseModel):
    """Outcome of the grounding check for one question."""

    grounded: bool
    best_score: float
    threshold: float

    @property
    def reason(self) -> str:
        """One-line explanation suitable for logs and UI footers."""
        comparison = ">=" if self.grounded else "<"
        return f"best score {self.best_score:.3f} {comparison} threshold {self.threshold:.2f}"


def check_grounding(results: list[RetrievedChunk], threshold: float) -> GroundingDecision:
    """Decide whether retrieval is confident enough to answer at all."""
    best = max((r.score for r in results), default=0.0)
    return GroundingDecision(grounded=best >= threshold, best_score=best, threshold=threshold)
