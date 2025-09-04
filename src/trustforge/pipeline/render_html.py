from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..common.md import md_to_html, parse_policy_markdown
from ..common.theme import load_theme, tokens_to_css_vars
from ..config import load_settings


def render_html(policy_path: Path) -> Path:
    settings = load_settings()
    tokens = load_theme(settings.theme_path)

    env = Environment(
        loader=FileSystemLoader("templates/html"), autoescape=select_autoescape(["html"])
    )
    template = env.get_template("base.html")

    text = Path(policy_path).read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text)
    body_html = md_to_html(body_md)
    css_vars = tokens_to_css_vars(tokens)

    out_dir = Path(settings.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Mirror assets (fonts+logo) to out/
    src_assets = Path("assets")
    brand_logo_rel = ""
    if src_assets.exists() and src_assets.is_dir():
        dst_assets = out_dir / "assets"
        shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
        if tokens.brand.logo_path:
            p = Path(tokens.brand.logo_path)
            if p.name:
                brand_logo_rel = f"assets/{p.name}"

    out_html = template.render(
        title=meta.title,
        subtitle=getattr(meta, "subtitle", None),
        footer_text=getattr(meta, "footer", None),
        version=meta.version,
        owner=meta.owner,
        last_reviewed=meta.last_reviewed,
        body_html=body_html,
        css_vars=css_vars,
        brand_name=tokens.brand.name,
        brand_logo=brand_logo_rel,
        background=tokens.color.background,
        primary=tokens.color.primary,
        primary_dark=getattr(tokens.color, "primary_dark", tokens.color.primary),
    )
    out_path = out_dir / (policy_path.stem + ".html")
    out_path.write_text(out_html, encoding="utf-8")
    return out_path
