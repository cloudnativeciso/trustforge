from __future__ import annotations

from pathlib import Path
from shutil import copy2

from jinja2 import Environment, FileSystemLoader, select_autoescape

from trustforge.common.errors import AssetNotFoundError, TemplateError
from trustforge.common.md import md_to_html, parse_policy_markdown
from trustforge.common.theme import load_theme, tokens_to_css_vars
from trustforge.config import Settings


def render_html(policy_path: Path) -> Path:
    settings = Settings()
    tokens = load_theme(settings.theme_path)
    env = Environment(
        loader=FileSystemLoader("templates/html"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    try:
        template = env.get_template("base.html")
    except Exception as e:  # jinja2.TemplateNotFound or syntax errors
        raise TemplateError("templates/html/base.html", str(e)) from e

    text = policy_path.read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text, source=policy_path)
    body_html = md_to_html(body_md)
    css_vars = tokens_to_css_vars(tokens)

    out_dir = Path(settings.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Mirror assets (fonts+logo) to out/
    if tokens.brand.logo_path:
        src_logo = Path(tokens.brand.logo_path)
        if src_logo.exists():
            (out_dir / "assets").mkdir(exist_ok=True)
            copy2(src_logo, out_dir / "assets" / src_logo.name)
        else:
            raise AssetNotFoundError(src_logo)

    html = template.render(
        meta=meta,
        body=body_html,
        css_vars=css_vars,
        tokens=tokens,
    )
    out_path = out_dir / (policy_path.stem + ".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path
