from __future__ import annotations

from pathlib import Path

import typer

from .pipeline.metadata import build_index_csv
from .pipeline.render_html import render_html
from .pipeline.render_pdf import render_pdf

app = typer.Typer(help="Trustforge Policy Foundry")


@app.command()
def html(policy: str) -> None:
    """Render a policy Markdown file to themed HTML."""
    out = render_html(Path(policy))
    typer.echo(f"HTML -> {out}")


@app.command()
def pdf(policy: str) -> None:
    """Render a policy Markdown file to themed PDF (pandoc + xelatex required)."""
    out = render_pdf(Path(policy))
    typer.echo(f"PDF -> {out}")


@app.command()
def index(out: str = "out/policies.csv", policies_dir: str = "policies") -> None:
    """Build CSV index of policy frontmatter across all markdown files."""
    p = build_index_csv(Path(policies_dir), Path(out))
    typer.echo(f"Index -> {p}")


if __name__ == "__main__":
    app()
