"""Choose a generation provider from settings and available keys.

Selection ladder for ``provider=auto``:

1. Claude, if ``ANTHROPIC_API_KEY`` is set and the ``anthropic`` package is
   installed (``uv sync --extra cloud``)
2. OpenAI, likewise with ``OPENAI_API_KEY`` and the ``openai`` package
3. The keyless extractive answerer — always available, so a fresh clone
   (or a revoked key) degrades gracefully instead of crashing.
"""

import importlib.util
import os

from ragkit.config import Settings
from ragkit.embed.base import EmbeddingProvider
from ragkit.generate.base import GenerationProvider
from ragkit.generate.extractive import ExtractiveAnswerer


def _available(env_var: str, package: str) -> bool:
    return bool(os.environ.get(env_var)) and importlib.util.find_spec(package) is not None


def make_provider(settings: Settings, embedder: EmbeddingProvider) -> GenerationProvider:
    """Return the configured provider; the keyless extractive path is the floor."""
    choice = settings.provider

    if choice == "auto":
        if _available("ANTHROPIC_API_KEY", "anthropic"):
            choice = "anthropic"
        elif _available("OPENAI_API_KEY", "openai"):
            choice = "openai"
        else:
            choice = "extractive"

    if choice == "extractive":
        return ExtractiveAnswerer(embedder)
    if choice == "anthropic":
        from ragkit.generate.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if choice == "openai":
        from ragkit.generate.openai_provider import OpenAIProvider

        return OpenAIProvider()
    raise ValueError(f"unknown provider: {settings.provider!r}")
