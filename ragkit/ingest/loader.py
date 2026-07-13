"""Folder-agnostic markdown/text loader with frontmatter support."""

from pathlib import Path

import frontmatter
from pydantic import BaseModel

SUPPORTED_SUFFIXES = {".md", ".txt"}


class Document(BaseModel):
    """A loaded source document, before chunking."""

    source: str
    """Path relative to the corpus root, POSIX-style (stable across OSes)."""
    title: str
    text: str
    metadata: dict[str, str] = {}


def load_corpus(corpus_dir: Path) -> list[Document]:
    """Load every ``.md``/``.txt`` file under ``corpus_dir``, recursively.

    Markdown frontmatter is parsed; a ``title`` key becomes the document
    title, otherwise the first ``#`` heading or the filename is used.
    Results are sorted by path so ingestion order is deterministic.
    """
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {corpus_dir}")

    docs: list[Document] = []
    for path in sorted(corpus_dir.rglob("*")):
        if path.suffix.lower() not in SUPPORTED_SUFFIXES or not path.is_file():
            continue
        post = frontmatter.load(path)
        text = post.content.strip()
        if not text:
            continue
        meta = {k: str(v) for k, v in post.metadata.items()}
        docs.append(
            Document(
                source=path.relative_to(corpus_dir).as_posix(),
                title=meta.get("title") or _first_heading(text) or path.stem,
                text=text,
                metadata=meta,
            )
        )
    return docs


def _first_heading(text: str) -> str | None:
    """Return the first markdown ``#`` heading, if any."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None
