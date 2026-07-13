"""The grounding hard-fail.

An assistant that answers everything is worse than no assistant: users can't
tell confident-right from confident-wrong. Grounding requires TWO independent
signals before the pipeline is allowed to answer:

1. **Vector confidence** — the best retrieved chunk's cosine similarity must
   clear ``min_score``. Catches off-topic questions.
2. **Lexical coverage** — the question's informative vocabulary (IDF-weighted)
   must actually occur in the retrieved chunks. Catches the harder case:
   questions *about* the corpus's entities whose answers the corpus doesn't
   contain ("what is the company's street address?") — topically similar to
   everything, answerable by nothing.

If either signal fails, the pipeline refuses instead of generating — and
still shows what it found, so the refusal is useful.
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
    coverage: float
    score_threshold: float
    coverage_threshold: float

    @property
    def reason(self) -> str:
        """One-line explanation suitable for logs and UI footers."""
        score_ok = self.best_score >= self.score_threshold
        coverage_ok = self.coverage >= self.coverage_threshold
        parts = [
            f"similarity {self.best_score:.3f} {'>=' if score_ok else '<'} "
            f"{self.score_threshold:.2f}",
            f"term coverage {self.coverage:.3f} {'>=' if coverage_ok else '<'} "
            f"{self.coverage_threshold:.2f}",
        ]
        return " | ".join(parts)


def check_grounding(
    results: list[RetrievedChunk],
    score_threshold: float,
    coverage: float,
    coverage_threshold: float,
) -> GroundingDecision:
    """Decide whether retrieval is confident enough to answer at all."""
    best = max((r.score for r in results), default=0.0)
    return GroundingDecision(
        grounded=best >= score_threshold and coverage >= coverage_threshold,
        best_score=best,
        coverage=coverage,
        score_threshold=score_threshold,
        coverage_threshold=coverage_threshold,
    )
