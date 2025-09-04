from __future__ import annotations

import sys
import traceback
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer

from .common.errors import (
    AssetNotFoundError,
    CSVIndexError,
    LaTeXError,
    MissingDependencyError,
    TemplateError,
    TrustforgeError,
)
from .pipeline.metadata import build_index_csv
from .pipeline.render_html import render_html
from .pipeline.render_pdf import render_pdf

# Configure Typer app
app = typer.Typer(
    help="Trustforge Policy Foundry — build polished security artifacts (HTML, PDF, CSV).",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _pkg_version() -> str:
    try:
        return version("trustforge")
    except PackageNotFoundError:
        return "0.0.0-dev"


def _echo_err(msg: str, *, color: str = "red") -> None:
    # typer.secho uses click underneath; no extra dependencies needed.
    typer.secho(msg, err=True, fg=color)


def _fail_user(msg: str, *, code: int = 2) -> None:
    _echo_err(msg, color="red")
    raise typer.Exit(code=code)


def _fail_dep_msg(e: MissingDependencyError) -> None:
    # Don’t assume .tool exists; rely on the exception’s str() message.
    _echo_err(str(e), color="yellow")
    raise typer.Exit(code=3)


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show full Python tracebacks for unexpected errors.",
    ),
    show_version: bool = typer.Option(
        False,
        "--version",
        help="Print the trustforge version and exit.",
        is_flag=True,
        is_eager=True,
    ),
) -> None:
    """
    Global options (verbose, version). Commands are: html, pdf, index.
    """
    if show_version:
        typer.echo(_pkg_version())
        raise typer.Exit(0)
    # No-op otherwise


def _handle_known_errors(e: TrustforgeError) -> None:
    """
    Map known TrustforgeError subclasses to friendly messages and exit codes.
    """
    if isinstance(e, MissingDependencyError):
        _fail_dep_msg(e)
    elif isinstance(e, (TemplateError, AssetNotFoundError, CSVIndexError, LaTeXError)):
        _fail_user(str(e), code=2)
    else:
        # Generic domain error
        _fail_user(str(e), code=2)


def _handle_unexpected(e: Exception, verbose: bool) -> None:
    if verbose:
        _echo_err("Unexpected error (traceback follows):", color="red")
        traceback.print_exc()
    else:
        _echo_err(f"Unexpected error: {e}", color="red")
    raise typer.Exit(code=1)


@app.command()
def html(
    policy: str = typer.Argument(
        ..., help="Path to a policy Markdown file (with YAML frontmatter)."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full tracebacks on error."),
) -> None:
    """
    Render a policy Markdown file to **themed HTML**.
    """
    policy_path = Path(policy)
    if not policy_path.exists() or not policy_path.is_file():
        _fail_user(f"Policy not found: {policy_path}", code=2)

    try:
        out = render_html(policy_path)
    except TrustforgeError as e:
        _handle_known_errors(e)
        return  # for type-checkers
    except Exception as e:  # safety net
        _handle_unexpected(e, verbose)
        return
    typer.echo(f"HTML -> {out}")


@app.command()
def pdf(
    policy: str = typer.Argument(
        ..., help="Path to a policy Markdown file (with YAML frontmatter)."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full tracebacks on error."),
) -> None:
    """
    Render a policy Markdown file to **themed PDF** (XeLaTeX required).
    """
    policy_path = Path(policy)
    if not policy_path.exists() or not policy_path.is_file():
        _fail_user(f"Policy not found: {policy_path}", code=2)

    try:
        out = render_pdf(policy_path)
    except TrustforgeError as e:
        _handle_known_errors(e)
        return
    except Exception as e:
        _handle_unexpected(e, verbose)
        return
    typer.echo(f"PDF -> {out}")


@app.command()
def index(
    out: str = typer.Option("out/policies.csv", "--out", help="Destination CSV path."),
    policies_dir: str = typer.Option(
        "policies", "--policies-dir", help="Directory containing *.md policies."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full tracebacks on error."),
) -> None:
    """
    Build a **CSV index** of policy frontmatter across all markdown files.
    """
    policies_path = Path(policies_dir)
    try:
        csv_path = build_index_csv(policies_path, Path(out))
    except TrustforgeError as e:
        _handle_known_errors(e)
        return
    except Exception as e:
        _handle_unexpected(e, verbose)
        return
    typer.echo(f"Index -> {csv_path}")


if __name__ == "__main__":
    # Typer uses SystemExit; this guard ensures clean non-zero codes propagate.
    try:
        app()
    except SystemExit as e:
        sys.exit(e.code)
