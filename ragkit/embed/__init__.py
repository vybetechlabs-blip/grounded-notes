"""Embedding providers behind a common interface."""

from ragkit.embed.base import EmbeddingProvider
from ragkit.embed.local import SentenceTransformersEmbedder

__all__ = ["EmbeddingProvider", "SentenceTransformersEmbedder"]
