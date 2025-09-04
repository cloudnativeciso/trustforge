from __future__ import annotations

import yaml

from ..models import ThemeTokens
from .types import PathLike


def load_theme(path: PathLike) -> ThemeTokens:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return ThemeTokens(**data)


def tokens_to_css_vars(tokens: ThemeTokens) -> dict[str, str]:
    return {
        "color_text": tokens.color.text,
        "color_muted": tokens.color.muted,
        "color_border": tokens.color.border,
        "max_width": f"{tokens.html.max_width_px}px",
        "line_height": str(tokens.typography.line_height),
        "font_body": tokens.typography.font_body,
        "font_heading": tokens.typography.font_heading,
        "font_logo": getattr(tokens.typography, "font_logo", tokens.typography.font_heading),
        "font_mono": tokens.typography.font_mono,
        "heading_weight": str(tokens.html.heading_weight),
    }


def tokens_to_latex_vars(tokens: ThemeTokens) -> dict[str, str]:
    return {
        "PAGE_MARGIN": str(tokens.layout.page_margins_mm),
        "LINK_COLOR_HTML": tokens.pdf.link_color.lstrip("#"),
        "HEADING_COLOR_HTML": tokens.pdf.heading_color.lstrip("#"),
        "TEXT_COLOR_HTML": tokens.color.text.lstrip("#"),
        "LOGO_HEIGHT_MM": str(getattr(tokens.brand, "logo_height_mm", 18)),
    }
