from __future__ import annotations

from pathlib import Path
from shutil import copy2
from typing import Final

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..common.md import md_to_html, parse_policy_markdown
from ..common.theme import load_theme, tokens_to_css_vars
from ..config import Settings
from ..errors import (
    AssetMissingError,
    HTMLBuildError,
    InvalidFrontmatterError,
    ThemeLoadError,
)
from ..models import ThemeTokens

TEMPLATES_DIR: Final[Path] = Path("templates/html")
BASE_TEMPLATE: Final[str] = "base.html"


def _ensure_exists(p: Path, what: str) -> None:
    if not p.exists():
        raise AssetMissingError(f"Missing {what}: {p}")


def render_html(policy_path: Path) -> Path:
    """
    Render a policy Markdown file to themed HTML.
    Raises:
      InvalidFrontmatterError, ThemeLoadError, AssetMissingError, HTMLBuildError
    """
    try:
        text = policy_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise AssetMissingError(f"Policy file not found: {policy_path}") from e

    # Frontmatter + body
    try:
        meta, body_md = parse_policy_markdown(text)
    except ValueError as e:
        raise InvalidFrontmatterError(str(e)) from e

    # Theme
    settings = Settings()
    try:
        tokens: ThemeTokens = load_theme(settings.theme_path)
    except Exception as e:
        raise ThemeLoadError(f"Failed to load theme '{settings.theme_path}': {e}") from e

    # HTML conversion
    body_html = md_to_html(body_md)

    # Templates
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template(BASE_TEMPLATE)
    except TemplateNotFound as e:
        raise AssetMissingError(f"HTML template not found: {TEMPLATES_DIR / BASE_TEMPLATE}") from e
    except Exception as e:
        raise HTMLBuildError(f"Failed to load HTML template: {e}") from e

    css_vars = tokens_to_css_vars(tokens)

    html = template.render(
        meta=meta,
        body_html=body_html,
        css_vars=css_vars,
        tokens=tokens,
        title=meta.title,
    )

    # Output dir
    out_dir = Path(settings.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy web assets (logo & webfonts) if present
    # (best effort; missing logo is not fatal for HTML)
    assets_root = Path("assets")
    if assets_root.exists():
        for rel in [
            Path("logo.png"),
            Path("fonts/dm-sans/DMSans-Regular.woff2"),
            Path("fonts/dm-sans/DMSans-Bold.woff2"),
            Path("fonts/inter/Inter-Regular.woff2"),
            Path("fonts/inter/Inter-Bold.woff2"),
            Path("fonts/fira-code/FiraCode-Regular.woff2"),
            Path("fonts/fira-code/FiraCode-Bold.woff2"),
            Path("fonts/satoshi/Satoshi-Regular.woff2"),
            Path("fonts/satoshi/Satoshi-Bold.woff2"),
        ]:
            src = assets_root / rel
            dst = out_dir / rel
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                copy2(src, dst)

    # Write file
    out_path = out_dir / f"{policy_path.stem}.html"
    try:
        out_path.write_text(html, encoding="utf-8")
    except Exception as e:
        raise HTMLBuildError(f"Failed to write HTML output: {e}") from e

    return out_path
