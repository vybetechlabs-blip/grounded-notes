"""Chroma store sync (idempotency) and vector retrieval on the fixture corpus."""

from pathlib import Path

import pytest

from ragkit.ingest.chunker import Chunk, chunk_document
from ragkit.ingest.loader import load_corpus
from ragkit.retrieve.vector import VectorRetriever
from ragkit.store.chroma import ChromaStore
from tests.conftest import FakeEmbedder


@pytest.fixture()
def synced_store(
    fixture_corpus: Path, tmp_path: Path, fake_embedder: FakeEmbedder
) -> tuple[ChromaStore, list[Chunk]]:
    chunks = [c for d in load_corpus(fixture_corpus) for c in chunk_document(d)]
    store = ChromaStore(tmp_path / "data", "test")
    store.sync(chunks, fake_embedder.embed_texts([c.context_text for c in chunks]))
    return store, chunks


def test_sync_is_idempotent(
    synced_store: tuple[ChromaStore, list[Chunk]], fake_embedder: FakeEmbedder
) -> None:
    store, chunks = synced_store
    count_before = store.count()
    upserted, deleted = store.sync(
        chunks, fake_embedder.embed_texts([c.context_text for c in chunks])
    )
    assert store.count() == count_before
    assert deleted == 0
    assert upserted == len(chunks)


def test_sync_removes_stale_chunks(
    synced_store: tuple[ChromaStore, list[Chunk]], fake_embedder: FakeEmbedder
) -> None:
    store, chunks = synced_store
    kept = chunks[:2]
    _, deleted = store.sync(kept, fake_embedder.embed_texts([c.context_text for c in kept]))
    assert deleted == len(chunks) - 2
    assert store.count() == 2


def test_vector_retrieval_ranks_relevant_doc_first(
    synced_store: tuple[ChromaStore, list[Chunk]], fake_embedder: FakeEmbedder
) -> None:
    store, _ = synced_store
    retriever = VectorRetriever(store, fake_embedder)
    results = retriever.retrieve("what pressure to brew espresso?", top_k=3)
    assert results
    assert results[0].chunk.source == "guides/espresso.md"
    assert results[0].score >= results[-1].score


def test_retrieval_scores_are_cosine_similarities(
    synced_store: tuple[ChromaStore, list[Chunk]], fake_embedder: FakeEmbedder
) -> None:
    store, _ = synced_store
    results = VectorRetriever(store, fake_embedder).retrieve("espresso brewing pressure", top_k=5)
    assert all(-1.0 <= r.score <= 1.0 for r in results)
