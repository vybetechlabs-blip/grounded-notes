"""Heading-aware chunking with overlap.

A chunk that says "increase it to 40" is useless without its heading trail,
so every chunk carries (and is embedded with) its document title and heading
path. Chunk ids are content hashes, which makes re-ingestion idempotent:
unchanged content produces identical ids.
"""

import hashlib
import re

from pydantic import BaseModel

from ragkit.ingest.loader import Document

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


class Chunk(BaseModel):
    """A retrievable unit: a slice of one document under one heading trail."""

    id: str
    source: str
    heading: str
    """Heading trail, e.g. ``"Service Catalog > Automation Sprint"``."""
    text: str
    index: int

    @property
    def context_text(self) -> str:
        """Text with heading context prepended — what gets embedded/indexed."""
        return f"{self.heading}\n\n{self.text}"


def chunk_document(doc: Document, chunk_size: int = 1200, overlap: int = 200) -> list[Chunk]:
    """Split a document into overlapping chunks that respect heading sections.

    The document is first split into heading-scoped sections; sections longer
    than ``chunk_size`` characters are packed paragraph-by-paragraph into
    multiple chunks with ``overlap`` characters of tail carried forward.
    """
    chunks: list[Chunk] = []
    for heading, section_text in _sections(doc):
        for piece in _pack(section_text, chunk_size, overlap):
            index = len(chunks)
            digest = hashlib.md5(f"{doc.source}|{heading}|{index}|{piece}".encode()).hexdigest()[
                :16
            ]
            chunks.append(
                Chunk(
                    id=f"{doc.source}#{digest}",
                    source=doc.source,
                    heading=heading,
                    text=piece,
                    index=index,
                )
            )
    return chunks


def _sections(doc: Document) -> list[tuple[str, str]]:
    """Split markdown into (heading-trail, body) sections."""
    trail: dict[int, str] = {}
    sections: list[tuple[str, str]] = []
    current_lines: list[str] = []
    current_trail = doc.title

    def flush() -> None:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_trail, body))

    for line in doc.text.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            flush()
            current_lines = []
            level = len(match.group(1))
            trail[level] = match.group(2).strip()
            for deeper in [k for k in trail if k > level]:
                del trail[deeper]
            parts = [trail[k] for k in sorted(trail)]
            if 1 not in trail:
                # No H1 yet: fall back to the document title as the root.
                parts.insert(0, doc.title)
            current_trail = " > ".join(dict.fromkeys(parts))
        else:
            current_lines.append(line)
    flush()
    return sections


def _pack(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Pack paragraphs into chunks of at most ~chunk_size chars with overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) > chunk_size and current:
            pieces.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}".strip() if tail else para
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces
