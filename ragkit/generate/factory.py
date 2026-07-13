"""Choose a generation provider from settings and available keys."""

from ragkit.config import Settings
from ragkit.embed.base import EmbeddingProvider
from ragkit.generate.base import GenerationProvider
from ragkit.generate.extractive import ExtractiveAnswerer


def make_provider(settings: Settings, embedder: EmbeddingProvider) -> GenerationProvider:
    """Return the configured provider; the keyless extractive path is the floor."""
    if settings.provider in {"auto", "extractive"}:
        return ExtractiveAnswerer(embedder)
    raise ValueError(f"unknown provider: {settings.provider!r}")
