from __future__ import annotations

from pathlib import Path

import typer

from .errors import (
    AssetMissingError,
    DependencyMissingError,
    HTMLBuildError,
    InvalidFrontmatterError,
    PDFBuildError,
    ThemeLoadError,
    TrustforgeError,
)
from .pipeline.metadata import build_index_csv
from .pipeline.render_html import render_html
from .pipeline.render_pdf import render_pdf

app = typer.Typer(help="Trustforge Policy Foundry")


def _bail(msg: str, code: int = 1) -> None:
    typer.secho(msg, fg=typer.colors.RED, err=True)
    raise typer.Exit(code)


@app.command()
def html(policy: str) -> None:
    """Render a policy Markdown file to themed HTML."""
    try:
        out = render_html(Path(policy))
        typer.secho(f"HTML -> {out}", fg=typer.colors.GREEN)
    except InvalidFrontmatterError as e:
        _bail(f"[frontmatter] {e}")
    except (AssetMissingError, ThemeLoadError) as e:
        _bail(f"[theme/assets] {e}")
    except HTMLBuildError as e:
        _bail(f"[html] {e}")
    except TrustforgeError as e:
        _bail(f"[trustforge] {e}")
    except Exception as e:  # safety net
        _bail(f"[unexpected] {e.__class__.__name__}: {e}")


@app.command()
def pdf(policy: str) -> None:
    """Render a policy Markdown file to themed PDF (xelatex required)."""
    try:
        out = render_pdf(Path(policy))
        typer.secho(f"PDF -> {out}", fg=typer.colors.GREEN)
    except InvalidFrontmatterError as e:
        _bail(f"[frontmatter] {e}")
    except DependencyMissingError as e:
        _bail(f"[deps] {e}\nHint: install TeX Live (XeLaTeX).")
    except AssetMissingError as e:
        _bail(f"[assets] {e}")
    except ThemeLoadError as e:
        _bail(f"[theme] {e}")
    except PDFBuildError as e:
        _bail(f"[pdf] {e}")
    except TrustforgeError as e:
        _bail(f"[trustforge] {e}")
    except Exception as e:  # safety net
        _bail(f"[unexpected] {e.__class__.__name__}: {e}")


@app.command()
def index(out: str = "out/policies.csv", policies_dir: str = "policies") -> None:
    """Build CSV index of policy frontmatter across all markdown files."""
    try:
        p = build_index_csv(Path(policies_dir), Path(out))
        typer.secho(f"Index -> {p}", fg=typer.colors.GREEN)
    except InvalidFrontmatterError as e:
        _bail(f"[frontmatter] {e}")
    except TrustforgeError as e:
        _bail(f"[trustforge] {e}")
    except FileNotFoundError:
        _bail(f"[inputs] Policies dir not found: {policies_dir}")
    except Exception as e:  # safety net
        _bail(f"[unexpected] {e.__class__.__name__}: {e}")


if __name__ == "__main__":
    app()
