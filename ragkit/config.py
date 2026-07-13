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
    """Grounding threshold: best hybrid-normalized score below this → refuse."""

    provider: str = "auto"
    """Generation provider: auto | extractive | anthropic | openai."""


def get_settings() -> Settings:
    """Return settings loaded from the environment (fresh each call)."""
    return Settings()
