"""Dense retrieval over the vector store."""

from ragkit.embed.base import EmbeddingProvider
from ragkit.store.chroma import ChromaStore, RetrievedChunk


class VectorRetriever:
    """Embeds the query and returns nearest chunks by cosine similarity."""

    def __init__(self, store: ChromaStore, embedder: EmbeddingProvider) -> None:
        self._store = store
        self._embedder = embedder

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return the top-k chunks for ``query``, best first."""
        return self._store.query(self._embedder.embed_query(query), top_k=top_k)
