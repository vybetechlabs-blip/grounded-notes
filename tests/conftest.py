"""Shared test fixtures: a deterministic fake embedder and a tiny corpus.

The fake embedder hashes words into a fixed-size bag-of-words vector, so
texts sharing vocabulary get high cosine similarity. Tests never download
models or hit the network.
"""

import hashlib
import math
import re
from pathlib import Path

import pytest

_DIM = 128


class FakeEmbedder:
    """Deterministic bag-of-hashed-words embedder (unit-normalized)."""

    @property
    def name(self) -> str:
        return "fake-bow"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(text: str) -> list[float]:
        vec = [0.0] * _DIM
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.md5(word.encode()).digest()
            vec[digest[0] % _DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


@pytest.fixture()
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()


@pytest.fixture()
def fixture_corpus(tmp_path: Path) -> Path:
    """A three-document corpus with distinct vocabularies per document."""
    corpus = tmp_path / "corpus"
    (corpus / "guides").mkdir(parents=True)

    (corpus / "guides" / "espresso.md").write_text(
        "---\ntitle: Espresso Guide\n---\n"
        "# Espresso Guide\n\n"
        "## Grinding\n\n"
        "Grind espresso beans fine, similar to table salt texture.\n\n"
        "## Brewing\n\n"
        "Brew espresso at nine bars of pressure for thirty seconds.\n",
        encoding="utf-8",
    )
    (corpus / "guides" / "kayaking.md").write_text(
        "---\ntitle: Kayaking Basics\n---\n"
        "# Kayaking Basics\n\n"
        "## Paddling\n\n"
        "Hold the kayak paddle with relaxed grip and rotate your torso.\n\n"
        "## Safety\n\n"
        "Always wear a flotation vest when kayaking on open water.\n",
        encoding="utf-8",
    )
    (corpus / "notes.txt").write_text(
        "Plain text files are also loaded. Bread proofing takes two hours.\n",
        encoding="utf-8",
    )
    return corpus
