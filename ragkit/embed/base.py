"""The embedding interface every provider implements.

Swapping embedders (sentence-transformers → Ollama → OpenAI) is a config
concern, not an architecture change: anything with this interface plugs into
the store and retrievers unchanged.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Turns text into unit-normalized vectors."""

    @property
    def name(self) -> str:
        """Identifier persisted with the index (guards against model mixing)."""
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed documents for indexing."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a query. Separate from documents: some models use prefixes."""
        ...
