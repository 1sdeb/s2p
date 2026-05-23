"""Command-line entry point.

Settings come from config.toml; any flag below overrides the file.

    s2p migrate https://github.com/you/selenium-suite --out ./pw-suite
    s2p migrate ./local/repo --provider openai
    s2p migrate ./repo --config ./my-config.toml
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .config import load_settings
from .pipeline import run

app = typer.Typer(add_completion=False, help="Selenium -> Playwright migrator")


@app.command()
def migrate(
    repo: str = typer.Argument(..., help="GitHub URL or local path to the Selenium repo"),
    out: Optional[Path] = typer.Option(None, "--out", help="Output dir"),
    provider: Optional[str] = typer.Option(None, "--provider", help="anthropic | openai"),
    model: Optional[str] = typer.Option(None, "--model", help="Override model string"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to config.toml"),
    max_fix: Optional[int] = typer.Option(None, "--max-fix", help="Self-heal retries per file"),
    run_tests: Optional[bool] = typer.Option(
        None, "--run-tests/--no-run-tests", help="Attempt pytest after convert"
    ),
):
    settings = load_settings(
        repo,
        out_dir=out,
        provider=provider,
        model=model,
        max_fix_attempts=max_fix,
        run_tests=run_tests,
        config_path=config,
    )
    result = run(settings)
    typer.secho(f"\nDone. Converted repo at: {result}", fg=typer.colors.GREEN)
    typer.echo(f"See {result / 'MIGRATION_REPORT.md'} for details.")


if __name__ == "__main__":
    app()
