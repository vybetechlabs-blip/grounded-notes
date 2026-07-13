"""Default keyless embedder: sentence-transformers on CPU."""

from functools import cached_property
from typing import Any


class SentenceTransformersEmbedder:
    """CPU-friendly local embeddings via sentence-transformers.

    The model (default ``all-MiniLM-L6-v2``, ~90 MB) is downloaded once on
    first use and cached by huggingface hub. Import and model load are lazy so
    that CLI startup and unit tests stay fast.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self._model_name = model_name

    @property
    def name(self) -> str:
        return self._model_name

    @cached_property
    def _model(self) -> Any:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(self._model_name, device="cpu")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]
