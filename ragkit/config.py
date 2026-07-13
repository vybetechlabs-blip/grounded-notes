"""Application settings, loaded from environment variables / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Every field can be overridden with a ``RAGKIT_``-prefixed environment
    variable (e.g. ``RAGKIT_TOP_K=8``) or a ``.env`` file in the working
    directory. Defaults are chosen so a fresh clone works with no setup.
    """

    model_config = SettingsConfigDict(env_prefix="RAGKIT_", env_file=".env", extra="ignore")

    corpus_dir: Path = Path("corpus")
    data_dir: Path = Path("data")

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    collection_name: str = "grounded_notes"

    chunk_size: int = 1200
    """Target chunk size in characters (soft limit, split on paragraph bounds)."""
    chunk_overlap: int = 200

    top_k: int = 5
    min_score: float = 0.35
    """Grounding signal 1: refuse if the best cosine similarity is below this."""
    min_coverage: float = 0.4
    """Grounding signal 2: refuse if IDF-weighted query-term coverage is below this."""

    rerank: bool = False
    """Rerank fused candidates with a local cross-encoder (keyless, CPU).

    Off by default: on this corpus's eval set the ms-marco cross-encoder
    improved nothing and demoted paraphrase matches that lack the query's
    entity tokens (see README design decisions). Kept as an option because
    larger/messier corpora may reach a different verdict — measure first.
    """
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_candidates: int = 15
    """How many fused candidates the reranker reads before cutting to top_k."""

    provider: str = "auto"
    """Generation provider: auto | extractive | anthropic | openai."""


def get_settings() -> Settings:
    """Return settings loaded from the environment (fresh each call)."""
    return Settings()
