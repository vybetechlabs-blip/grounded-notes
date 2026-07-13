"""Corpus ingestion: loading documents and chunking them for retrieval."""

from ragkit.ingest.chunker import Chunk, chunk_document
from ragkit.ingest.loader import Document, load_corpus

__all__ = ["Chunk", "Document", "chunk_document", "load_corpus"]
