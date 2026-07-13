"""Loader and chunker behavior."""

from pathlib import Path

from ragkit.ingest.chunker import chunk_document
from ragkit.ingest.loader import Document, load_corpus


def test_loader_finds_md_and_txt(fixture_corpus: Path) -> None:
    docs = load_corpus(fixture_corpus)
    assert [d.source for d in docs] == [
        "guides/espresso.md",
        "guides/kayaking.md",
        "notes.txt",
    ]


def test_loader_skips_corpus_root_readme(fixture_corpus: Path) -> None:
    (fixture_corpus / "README.md").write_text("# About this corpus\n\nMeta.", encoding="utf-8")
    (fixture_corpus / "guides" / "readme.md").write_text(
        "# Guide Index\n\nNested readmes are real content.", encoding="utf-8"
    )
    sources = [d.source for d in load_corpus(fixture_corpus)]
    assert "README.md" not in sources
    assert "guides/readme.md" in sources


def test_loader_parses_frontmatter_title(fixture_corpus: Path) -> None:
    docs = {d.source: d for d in load_corpus(fixture_corpus)}
    assert docs["guides/espresso.md"].title == "Espresso Guide"
    assert "---" not in docs["guides/espresso.md"].text


def test_chunker_builds_heading_trails(fixture_corpus: Path) -> None:
    doc = next(d for d in load_corpus(fixture_corpus) if "espresso" in d.source)
    chunks = chunk_document(doc)
    trails = {c.heading for c in chunks}
    assert "Espresso Guide > Grinding" in trails
    assert "Espresso Guide > Brewing" in trails
    assert all(c.source == "guides/espresso.md" for c in chunks)


def test_chunker_context_text_prepends_heading(fixture_corpus: Path) -> None:
    doc = load_corpus(fixture_corpus)[0]
    chunk = chunk_document(doc)[0]
    assert chunk.context_text.startswith(chunk.heading)
    assert chunk.text in chunk.context_text


def test_chunker_ids_are_deterministic(fixture_corpus: Path) -> None:
    doc = load_corpus(fixture_corpus)[0]
    first = [c.id for c in chunk_document(doc)]
    second = [c.id for c in chunk_document(doc)]
    assert first == second
    assert len(set(first)) == len(first)


def test_chunker_splits_long_sections_with_overlap() -> None:
    paragraphs = "\n\n".join(f"Paragraph number {i} about topic {i}." for i in range(60))
    doc = Document(source="long.md", title="Long", text=f"# Long\n\n{paragraphs}")
    chunks = chunk_document(doc, chunk_size=300, overlap=80)
    assert len(chunks) > 1
    assert all(len(c.text) <= 300 + 100 for c in chunks)
    # Overlap: the tail of chunk N appears at the head of chunk N+1.
    assert chunks[0].text[-40:] in chunks[1].text
