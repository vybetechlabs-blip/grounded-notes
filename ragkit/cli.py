"""Typer CLI: ingest, query, eval."""

import typer
from rich.console import Console
from rich.panel import Panel

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


@app.command()
def ingest() -> None:
    """Load, chunk, embed, and index the corpus (idempotent sync)."""
    from ragkit.pipeline import Pipeline

    pipeline = Pipeline()
    with console.status("Ingesting corpus (first run downloads the embedding model)..."):
        docs, chunks, deleted = pipeline.ingest()
    console.print(
        f"Ingested [bold]{docs}[/bold] documents -> [bold]{chunks}[/bold] chunks "
        f"({deleted} stale removed) into {pipeline.settings.data_dir}/chroma"
    )


@app.command()
def query(
    question: str,
    top_k: int = typer.Option(None, help="Chunks to retrieve (default from settings)."),
    show_chunks: bool = typer.Option(False, help="Print the retrieved chunks too."),
) -> None:
    """Ask a question; get a cited answer or an honest refusal."""
    from ragkit.pipeline import Pipeline
    from ragkit.retrieve.context import assemble_context

    pipeline = Pipeline()
    if pipeline.store.count() == 0:
        console.print("[red]Index is empty — run `ragkit ingest` first.[/red]")
        raise typer.Exit(code=1)

    answer = pipeline.ask(question, top_k=top_k)
    style = "green" if answer.grounded else "yellow"
    title = f"answer · {answer.provider}" if answer.grounded else "refused (not grounded)"
    console.print(Panel(answer.text, title=title, border_style=style))
    console.print(f"[dim]{answer.decision.reason}[/dim]")
    console.print("\n[bold]Sources[/bold]")
    for citation in answer.citations:
        console.print(f"  {citation.render()}  [dim](score {citation.score:.3f})[/dim]")
    if show_chunks:
        console.print("\n[bold]Retrieved context[/bold]")
        console.print(assemble_context(pipeline.retriever.retrieve(question, top_k)))


if __name__ == "__main__":
    app()
