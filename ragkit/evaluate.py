"""Eval harness: retrieval hit-rate and grounding accuracy over committed cases.

Two numbers gate every retrieval or prompt change:

- **hit-rate@k** — for answerable questions, did any expected source appear
  in the top-k citations?
- **grounding accuracy** — answerable questions answered AND out-of-corpus
  questions refused. The refusal half is expected to stay at 100%; a guessing
  assistant fails the whole point of the project.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel

from ragkit.pipeline import Pipeline


class EvalCase(BaseModel):
    """One committed question with its expectations."""

    question: str
    expected_sources: list[str] = []
    answerable: bool = True


class CaseResult(BaseModel):
    """Outcome of one case."""

    case: EvalCase
    hit: bool | None
    """Expected source in top-k (answerable cases only)."""
    grounding_ok: bool
    best_score: float
    top_source: str


class EvalReport(BaseModel):
    """Aggregate metrics plus per-case detail."""

    results: list[CaseResult]

    @property
    def answerable(self) -> list[CaseResult]:
        return [r for r in self.results if r.case.answerable]

    @property
    def unanswerable(self) -> list[CaseResult]:
        return [r for r in self.results if not r.case.answerable]

    @property
    def hit_rate(self) -> float:
        answerable = self.answerable
        if not answerable:
            return 0.0
        return sum(1 for r in answerable if r.hit) / len(answerable)

    @property
    def refusal_rate(self) -> float:
        unanswerable = self.unanswerable
        if not unanswerable:
            return 1.0
        return sum(1 for r in unanswerable if r.grounding_ok) / len(unanswerable)

    @property
    def grounding_accuracy(self) -> float:
        return sum(1 for r in self.results if r.grounding_ok) / len(self.results)


def load_cases(path: Path) -> list[EvalCase]:
    """Load eval cases from YAML."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [EvalCase(**case) for case in payload["cases"]]


def run_eval(pipeline: Pipeline, cases: list[EvalCase]) -> EvalReport:
    """Run every case through the pipeline and score it."""
    results: list[CaseResult] = []
    for case in cases:
        answer = pipeline.ask(case.question)
        cited = [c.source for c in answer.citations]
        hit = any(src in cited for src in case.expected_sources) if case.answerable else None
        grounding_ok = answer.grounded if case.answerable else not answer.grounded
        results.append(
            CaseResult(
                case=case,
                hit=hit,
                grounding_ok=grounding_ok,
                best_score=answer.decision.best_score,
                top_source=cited[0] if cited else "(none)",
            )
        )
    return EvalReport(results=results)
