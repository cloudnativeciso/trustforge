from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from jinja2 import Environment, FileSystemLoader, select_autoescape

from trustforge.common.errors import AssetNotFoundError, TemplateError
from trustforge.common.md import md_to_html, parse_policy_markdown
from trustforge.common.theme import load_theme, tokens_to_css_vars
from trustforge.config import Settings


def render_html(policy_path: Path) -> Path:
    """
    Render a policy Markdown file to themed HTML.

    Steps:
      1) Load theme tokens (colors, fonts, sizes)
      2) Parse Markdown frontmatter + body
      3) Convert Markdown body -> HTML
      4) Render Jinja template with CSS vars + tokens
      5) Mirror `assets/` (fonts, logo) to out/assets
    """
    settings = Settings()
    tokens = load_theme(settings.theme_path)

    # Jinja environment
    try:
        env = Environment(
            loader=FileSystemLoader("templates/html"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template("base.html")
    except Exception as e:
        # Wrap any template lookup/syntax error with a consistent repo-level error
        raise TemplateError("templates/html/base.html", str(e)) from e

    # Read and parse the policy markdown
    text = policy_path.read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text, source=policy_path)
    body_html = md_to_html(body_md)
    css_vars = tokens_to_css_vars(tokens)

    # Prepare output directory
    out_dir = Path(settings.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Mirror assets (fonts, logo) to out/assets.
    # This ensures the generated HTML can reference local fonts/logo without external paths.
    src_assets_dir = Path("assets")
    dst_assets_dir = out_dir / "assets"
    if src_assets_dir.exists():
        # copytree with dirs_exist_ok=True keeps idempotency on rebuilds
        copytree(src_assets_dir, dst_assets_dir, dirs_exist_ok=True)
    else:
        # If the theme expects a logo but assets/ is missing or the file doesn't exist, surface a clear error.
        if tokens.brand.logo_path:
            maybe_logo = Path(tokens.brand.logo_path)
            if not maybe_logo.exists():
                raise AssetNotFoundError(maybe_logo)

    # Additionally, if a custom logo path is provided that is OUTSIDE of assets/,
    # copy it into out/assets/ to keep links stable.
    if tokens.brand.logo_path:
        logo_src = Path(tokens.brand.logo_path)
        if logo_src.exists():
            dst_assets_dir.mkdir(parents=True, exist_ok=True)
            copy2(logo_src, dst_assets_dir / logo_src.name)
        else:
            # Only raise if we actually referenced a custom path (not covered by assets/ copy)
            if not (src_assets_dir.exists() and (src_assets_dir / logo_src.name).exists()):
                raise AssetNotFoundError(logo_src)

    # Render final HTML
    html = template.render(
        meta=meta,
        body=body_html,
        css_vars=css_vars,
        tokens=tokens,
    )

    out_path = out_dir / (policy_path.stem + ".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path
