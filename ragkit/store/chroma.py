"""Chroma-backed vector store with idempotent sync.

Persisted to ``data/chroma/`` (git-ignored). Ingestion is a *sync*, not an
append: chunk ids are content hashes, so unchanged chunks are upserted onto
themselves, changed content produces new ids, and ids no longer present in
the corpus are deleted. Running ingest twice is a no-op.

Upgrade path: this wrapper is the only file that talks to Chroma; a pgvector
implementation with the same four methods would drop in behind it.
"""

from pathlib import Path

from pydantic import BaseModel

from ragkit.ingest.chunker import Chunk


class RetrievedChunk(BaseModel):
    """A chunk plus its retrieval score (cosine similarity, 0..1)."""

    chunk: Chunk
    score: float


class ChromaStore:
    """Thin wrapper around a persistent Chroma collection (cosine space)."""

    def __init__(self, data_dir: Path, collection_name: str = "grounded_notes") -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=str(data_dir / "chroma"))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Number of chunks currently indexed."""
        return self._collection.count()

    def sync(self, chunks: list[Chunk], embeddings: list[list[float]]) -> tuple[int, int]:
        """Upsert all chunks and delete stale ids. Returns (upserted, deleted)."""
        existing = set(self._collection.get(include=[])["ids"])
        fresh = {c.id for c in chunks}
        stale = sorted(existing - fresh)
        if stale:
            self._collection.delete(ids=stale)
        if chunks:
            self._collection.upsert(
                ids=[c.id for c in chunks],
                embeddings=embeddings,
                documents=[c.text for c in chunks],
                metadatas=[
                    {"source": c.source, "heading": c.heading, "index": c.index} for c in chunks
                ],
            )
        return len(chunks), len(stale)

    def query(self, embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        """Return the top-k most similar chunks with cosine-similarity scores."""
        if self.count() == 0:
            return []
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, self.count()),
            include=["documents", "metadatas", "distances"],
        )
        retrieved: list[RetrievedChunk] = []
        for cid, text, meta, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
            strict=True,
        ):
            chunk = Chunk(
                id=cid,
                source=str(meta["source"]),
                heading=str(meta["heading"]),
                text=text,
                index=int(meta["index"]),  # type: ignore[call-overload]
            )
            retrieved.append(RetrievedChunk(chunk=chunk, score=1.0 - distance))
        return retrieved

    def all_chunks(self) -> list[Chunk]:
        """Return every indexed chunk (used to build the lexical index)."""
        result = self._collection.get(include=["documents", "metadatas"])
        return [
            Chunk(
                id=cid,
                source=str(meta["source"]),
                heading=str(meta["heading"]),
                text=text,
                index=int(meta["index"]),  # type: ignore[call-overload]
            )
            for cid, text, meta in zip(
                result["ids"], result["documents"], result["metadatas"], strict=True
            )
        ]
