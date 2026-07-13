"""Typer CLI: ingest, query, eval."""

import typer
from rich.console import Console

app = typer.Typer(
    name="ragkit",
    help="Grounded RAG knowledge assistant: ingest a corpus, ask cited questions.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main() -> None:
    """Grounded RAG knowledge assistant: ingest a corpus, ask cited questions."""


@app.command()
def version() -> None:
    """Print the ragkit version."""
    from ragkit import __version__

    console.print(f"ragkit {__version__}")


if __name__ == "__main__":
    app()
