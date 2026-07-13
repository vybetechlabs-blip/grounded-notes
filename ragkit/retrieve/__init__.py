"""Retrieval: vector search, lexical BM25, hybrid fusion, context assembly."""

from ragkit.retrieve.context import assemble_context
from ragkit.retrieve.vector import VectorRetriever

__all__ = ["VectorRetriever", "assemble_context"]
