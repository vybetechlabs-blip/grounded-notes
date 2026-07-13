"""Extractive answering, citations, and the grounding guard."""

from ragkit.generate.extractive import ExtractiveAnswerer
from ragkit.grounding.citations import citations_from_results
from ragkit.grounding.guard import check_grounding
from ragkit.ingest.chunker import Chunk
from ragkit.retrieve.context import assemble_context
from ragkit.store.chroma import RetrievedChunk
from tests.conftest import FakeEmbedder


def _result(text: str, source: str = "doc.md", score: float = 0.8) -> RetrievedChunk:
    chunk = Chunk(id=f"{source}#x", source=source, heading="Doc > Section", text=text, index=0)
    return RetrievedChunk(chunk=chunk, score=score)


def test_extractive_answer_cites_the_right_chunk(fake_embedder: FakeEmbedder) -> None:
    results = [
        _result("Espresso is brewed at nine bars of pressure for thirty seconds.", "a.md"),
        _result("Kayak paddles should be held with a relaxed grip on the water.", "b.md"),
    ]
    answer = ExtractiveAnswerer(fake_embedder).answer("what pressure for espresso?", results)
    assert "[1]" in answer
    assert "nine bars" in answer


def test_citations_number_in_rank_order() -> None:
    results = [_result("first", "a.md", 0.9), _result("second", "b.md", 0.7)]
    citations = citations_from_results(results)
    assert [c.number for c in citations] == [1, 2]
    assert citations[0].source == "a.md"
    assert "a.md" in citations[0].render()


def test_grounding_passes_above_threshold() -> None:
    decision = check_grounding([_result("t", score=0.62)], threshold=0.35)
    assert decision.grounded
    assert decision.best_score == 0.62


def test_grounding_hard_fails_below_threshold() -> None:
    decision = check_grounding([_result("t", score=0.11)], threshold=0.35)
    assert not decision.grounded
    assert "0.110" in decision.reason


def test_grounding_hard_fails_on_empty_results() -> None:
    assert not check_grounding([], threshold=0.35).grounded


def test_context_assembly_labels_sources() -> None:
    context = assemble_context([_result("Some text.", "sops/x.md")])
    assert context.startswith("[1] sops/x.md — Doc > Section")
    assert "Some text." in context
