"""The generation interface every provider implements."""

from typing import Protocol, runtime_checkable

from ragkit.store.chroma import RetrievedChunk


@runtime_checkable
class GenerationProvider(Protocol):
    """Produces an answer from a question plus retrieved, cited context."""

    @property
    def name(self) -> str:
        """Short label shown to users, e.g. ``extractive`` or ``anthropic``."""
        ...

    def answer(self, question: str, results: list[RetrievedChunk]) -> str:
        """Answer ``question`` using only ``results``; cite with [n] markers."""
        ...
