from __future__ import annotations

import sys
from pathlib import Path

import typer

from .common.errors import TrustforgeError
from .pipeline.metadata import build_index_csv
from .pipeline.render_html import render_html
from .pipeline.render_pdf import render_pdf

app = typer.Typer(help="Trustforge Policy Foundry")


def _echo_err(msg: str) -> None:
    typer.echo(msg, err=True)


@app.command()
def html(policy: str) -> None:
    """
    Render a policy Markdown file to themed HTML.
    """
    try:
        out = render_html(Path(policy))
    except TrustforgeError as e:
        _echo_err(str(e))
        raise typer.Exit(code=2)
    except Exception as e:  # safety net
        _echo_err(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"HTML -> {out}")


@app.command()
def pdf(policy: str) -> None:
    """
    Render a policy Markdown file to themed PDF (XeLaTeX required).
    """
    try:
        out = render_pdf(Path(policy))
    except TrustforgeError as e:
        _echo_err(str(e))
        raise typer.Exit(code=2)
    except Exception as e:
        _echo_err(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"PDF -> {out}")


@app.command()
def index(out: str = "out/policies.csv", policies_dir: str = "policies") -> None:
    """
    Build CSV index of policy frontmatter across all markdown files.
    """
    try:
        p = build_index_csv(Path(policies_dir), Path(out))
    except TrustforgeError as e:
        _echo_err(str(e))
        raise typer.Exit(code=2)
    except Exception as e:
        _echo_err(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
    typer.echo(f"Index -> {p}")


if __name__ == "__main__":
    # Typer uses SystemExit; this guard ensures clean non-zero codes propagate.
    try:
        app()
    except SystemExit as e:
        # Allow GH Actions to display a non-zero exit when appropriate.
        sys.exit(e.code)
