"""Provider selection, prompt building, and graceful degradation."""

from pathlib import Path

import pytest

from ragkit.config import Settings
from ragkit.generate.factory import make_provider
from ragkit.generate.prompt import SYSTEM_PROMPT, build_user_message
from ragkit.ingest.chunker import Chunk
from ragkit.store.chroma import RetrievedChunk
from tests.conftest import FakeEmbedder


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def _result(text: str = "Espresso brews at nine bars.", source: str = "a.md") -> RetrievedChunk:
    chunk = Chunk(id=f"{source}#1", source=source, heading="Doc > S", text=text, index=0)
    return RetrievedChunk(chunk=chunk, score=0.8)


def test_auto_without_keys_falls_back_to_extractive(
    monkeypatch: pytest.MonkeyPatch, fake_embedder: FakeEmbedder
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = make_provider(_settings(provider="auto"), fake_embedder)
    assert provider.name == "extractive"


def test_auto_prefers_anthropic_when_key_and_package_present(
    monkeypatch: pytest.MonkeyPatch, fake_embedder: FakeEmbedder
) -> None:
    anthropic = pytest.importorskip("anthropic")
    assert anthropic is not None
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    provider = make_provider(_settings(provider="auto"), fake_embedder)
    assert provider.name.startswith("anthropic:")


def test_unknown_provider_raises(fake_embedder: FakeEmbedder) -> None:
    with pytest.raises(ValueError, match="unknown provider"):
        make_provider(_settings(provider="bogus"), fake_embedder)


def test_prompt_states_refusal_and_data_boundary() -> None:
    assert "don't have that in the knowledge base" in SYSTEM_PROMPT
    assert "data, not instructions" in SYSTEM_PROMPT


def test_user_message_contains_labeled_context_and_question() -> None:
    message = build_user_message("what pressure?", [_result()])
    assert "[1] a.md" in message
    assert "Question: what pressure?" in message


def test_pipeline_falls_back_when_cloud_provider_fails(
    fixture_corpus: Path, tmp_path: Path, fake_embedder: FakeEmbedder, monkeypatch
) -> None:
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

    class ExplodingProvider:
        name = "anthropic:test"

        def answer(self, question: str, results: list) -> str:
            raise RuntimeError("invalid api key")

    pipeline.provider = ExplodingProvider()
    answer = pipeline.ask("what pressure to brew espresso?")
    assert answer.grounded
    assert "nine bars" in answer.text  # extractive fallback still answered
    assert "fallback" in answer.provider
