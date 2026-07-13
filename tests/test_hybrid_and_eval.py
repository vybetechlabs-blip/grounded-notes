"""BM25 scoring, RRF fusion, and the eval harness on the fixture corpus."""

from pathlib import Path

from ragkit.evaluate import EvalCase, EvalReport, run_eval
from ragkit.ingest.chunker import Chunk, chunk_document
from ragkit.ingest.loader import load_corpus
from ragkit.retrieve.bm25 import BM25Index, tokenize
from ragkit.retrieve.hybrid import HybridRetriever
from ragkit.store.chroma import ChromaStore
from tests.conftest import FakeEmbedder


def _chunk(text: str, source: str) -> Chunk:
    return Chunk(id=f"{source}#1", source=source, heading=source, text=text, index=0)


def test_tokenize_keeps_part_numbers() -> None:
    assert "tw-4417" in tokenize("torque spec for TW-4417 gasket")


def test_bm25_ranks_exact_token_match_first() -> None:
    chunks = [
        _chunk("The TW-4417 gasket torque spec is 12 newton meters.", "parts.md"),
        _chunk("General maintenance spec advice for marine engines.", "general.md"),
        _chunk("Espresso brewing pressure guidance.", "coffee.md"),
    ]
    results = BM25Index(chunks).search("TW-4417 torque spec", top_k=3)
    assert results[0][0].source == "parts.md"
    assert results[0][1] > results[-1][1]


def test_bm25_returns_empty_for_unknown_vocabulary() -> None:
    chunks = [_chunk("Espresso brewing pressure guidance.", "coffee.md")]
    assert BM25Index(chunks).search("quantum chromodynamics lattice") == []


def test_hybrid_fuses_and_keeps_cosine_scores(
    fixture_corpus: Path, tmp_path: Path, fake_embedder: FakeEmbedder
) -> None:
    chunks = [c for d in load_corpus(fixture_corpus) for c in chunk_document(d)]
    store = ChromaStore(tmp_path / "data", "test")
    store.sync(chunks, fake_embedder.embed_texts([c.context_text for c in chunks]))

    retriever = HybridRetriever(store, fake_embedder)
    results = retriever.retrieve("espresso brewing pressure", top_k=3)
    assert results
    assert results[0].chunk.source == "guides/espresso.md"
    # Scores are cosine similarities, not RRF values (RRF maxes out ~2/61).
    assert all(-1.0 <= r.score <= 1.0 for r in results)
    assert results[0].score > 0.3


def test_informative_terms_ranks_rare_terms_first() -> None:
    chunks = [
        _chunk("acme services overview with acme pricing", "a.md"),
        _chunk("acme delivery process and acme staffing", "b.md"),
        _chunk("special discounts for nonprofits", "c.md"),
    ]
    terms = BM25Index(chunks).informative_terms("which discounts does acme offer")
    assert terms and terms[0] == "discounts"
    assert "acme" not in terms  # too common to be retrieval-critical
    assert "offer" not in terms  # absent from corpus: the guard's job, not ours


def test_hybrid_swaps_in_lexical_champion_for_rare_term(
    tmp_path: Path, fake_embedder: FakeEmbedder
) -> None:
    # Many chunks share the company-name vocabulary; exactly one contains the
    # rare query term, and vector similarity alone would never surface it.
    chunks = [
        _chunk(f"acme consulting overview number {i} about acme offer services", f"common{i}.md")
        for i in range(8)
    ]
    chunks.append(_chunk("nonprofits receive discounts on every fixed fee", "rare.md"))
    store = ChromaStore(tmp_path / "data", "test")
    store.sync(chunks, fake_embedder.embed_texts([c.context_text for c in chunks]))

    results = HybridRetriever(store, fake_embedder).retrieve(
        "which discounts does acme offer", top_k=3
    )
    assert "rare.md" in [r.chunk.source for r in results]


def test_reranker_reorders_without_touching_scores() -> None:
    from ragkit.retrieve.rerank import CrossEncoderReranker
    from ragkit.store.chroma import RetrievedChunk

    results = [
        RetrievedChunk(chunk=_chunk("first by cosine", "a.md"), score=0.9),
        RetrievedChunk(chunk=_chunk("second by cosine", "b.md"), score=0.5),
    ]

    class StubModel:
        def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
            return [0.1, 0.8]  # cross-encoder prefers the second chunk

    reranker = CrossEncoderReranker()
    reranker.__dict__["_model"] = StubModel()
    reordered = reranker.rerank("q", results)
    assert [r.chunk.source for r in reordered] == ["b.md", "a.md"]
    # Cosine scores travel with their chunks, unchanged.
    assert reordered[0].score == 0.5


def test_eval_report_metrics(
    fixture_corpus: Path, tmp_path: Path, fake_embedder: FakeEmbedder, monkeypatch
) -> None:
    from ragkit.config import Settings
    from ragkit.pipeline import Pipeline

    monkeypatch.setattr(
        "ragkit.pipeline.SentenceTransformersEmbedder", lambda _model: fake_embedder
    )
    settings = Settings(
        _env_file=None,
        corpus_dir=fixture_corpus,
        data_dir=tmp_path / "data",
        min_score=0.3,
        rerank=False,
    )
    pipeline = Pipeline(settings)
    pipeline.ingest()

    cases = [
        EvalCase(
            question="what pressure to brew espresso?",
            expected_sources=["guides/espresso.md"],
        ),
        EvalCase(question="how to paddle a kayak safely?", expected_sources=["guides/kayaking.md"]),
        EvalCase(question="quantum chromodynamics lattice gauge theory", answerable=False),
    ]
    report = run_eval(pipeline, cases)
    assert report.hit_rate == 1.0
    assert report.refusal_rate == 1.0
    assert report.grounding_accuracy == 1.0


def test_eval_report_counts_misses() -> None:
    good = EvalCase(question="q1", expected_sources=["a.md"])
    report = EvalReport(
        results=[
            {  # type: ignore[list-item]
                "case": good,
                "hit": False,
                "grounding_ok": True,
                "best_score": 0.5,
                "top_source": "b.md",
            }
        ]
    )
    assert report.hit_rate == 0.0
    assert report.grounding_accuracy == 1.0
