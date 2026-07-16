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


def test_extractive_renders_table_as_block_not_bullet(fake_embedder: FakeEmbedder) -> None:
    table = (
        "| Service | Price (USD) |\n"
        "| ------- | ----------- |\n"
        "| Automation Sprint | $9,500 |\n"
        "| Assistant Build | $18,000 |"
    )
    results = [
        _result(f"Prices are fixed fee.\n\n{table}", "pricing.md"),
        _result("Kayak paddles need a relaxed grip on open water.", "b.md"),
    ]
    answer = ExtractiveAnswerer(fake_embedder).answer(
        "service price automation sprint fixed fee", results
    )
    # The table survives as real markdown: separator row intact, rows at
    # column zero (not flattened into a "- ..." bullet).
    assert "| ------- | ----------- |" in answer
    assert "\n| Automation Sprint | $9,500 |" in answer
    assert "- | Service" not in answer
    # Citation marker stays adjacent to the table block.
    assert "*Table from [1]*" in answer


def test_extractive_pipe_lines_without_separator_stay_prose(
    fake_embedder: FakeEmbedder,
) -> None:
    results = [_result("| just one stray pipe line with enough characters here |", "a.md")]
    answer = ExtractiveAnswerer(fake_embedder).answer("stray pipe line characters", results)
    assert "*Table from" not in answer
    assert answer.count("- ") >= 1  # rendered as an ordinary bullet


def test_citations_number_in_rank_order() -> None:
    results = [_result("first", "a.md", 0.9), _result("second", "b.md", 0.7)]
    citations = citations_from_results(results)
    assert [c.number for c in citations] == [1, 2]
    assert citations[0].source == "a.md"
    assert "a.md" in citations[0].render()


def test_grounding_passes_when_both_signals_clear() -> None:
    decision = check_grounding(
        [_result("t", score=0.62)], score_threshold=0.35, coverage=0.9, coverage_threshold=0.4
    )
    assert decision.grounded
    assert decision.best_score == 0.62


def test_grounding_hard_fails_below_score_threshold() -> None:
    decision = check_grounding(
        [_result("t", score=0.11)], score_threshold=0.35, coverage=0.9, coverage_threshold=0.4
    )
    assert not decision.grounded
    assert "0.110" in decision.reason


def test_grounding_hard_fails_on_low_coverage_despite_high_similarity() -> None:
    # The hard case: topically-similar chunks, but the question's vocabulary
    # (e.g. "street address") never occurs in the corpus.
    decision = check_grounding(
        [_result("t", score=0.75)], score_threshold=0.35, coverage=0.15, coverage_threshold=0.4
    )
    assert not decision.grounded
    assert "coverage" in decision.reason


def test_grounding_hard_fails_on_empty_results() -> None:
    decision = check_grounding([], score_threshold=0.35, coverage=0.0, coverage_threshold=0.4)
    assert not decision.grounded


def test_context_assembly_labels_sources() -> None:
    context = assemble_context([_result("Some text.", "sops/x.md")])
    assert context.startswith("[1] sops/x.md — Doc > Section")
    assert "Some text." in context
