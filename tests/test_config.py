"""Smoke tests for settings and CLI wiring."""

from typer.testing import CliRunner

from ragkit.cli import app
from ragkit.config import Settings


def test_default_settings() -> None:
    s = Settings(_env_file=None)
    assert s.top_k == 5
    assert s.provider == "auto"
    assert s.chunk_overlap < s.chunk_size


def test_cli_help_runs() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ingest" in result.output or "cited" in result.output


def test_cli_version() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ragkit" in result.output
