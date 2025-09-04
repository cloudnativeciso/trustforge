from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Brand:
    name: str = "Trustforge"
    logo_path: str = ""
    logo_height_mm: int = 24


@dataclass
class Color:
    primary: str = "#222222"
    text: str = "#222222"
    muted: str = "#555555"
    border: str = "#DDDDDD"
    background: str = "#FFFFFF"
    # Optional extras used by cnciso theme(s)
    primary_light: str | None = None
    primary_dark: str | None = None
    secondary: str | None = None
    accent: str | None = None  # <— add support for 'accent'


@dataclass
class Typography:
    font_body: str = "Inter"
    font_heading: str = "Inter"
    font_logo: str = "Inter"
    font_mono: str = "Menlo"
    scale: float = 1.0
    line_height: float = 1.5


@dataclass
class Layout:
    page_margins_mm: int = 20
    header: bool = True
    footer: bool = True
    watermark: str = ""


@dataclass
class PDF:
    link_color: str = "#1A73E8"
    heading_color: str = "#000000"


@dataclass
class HTML:
    max_width_px: int = 800
    heading_weight: int = 700


@dataclass
class ThemeTokens:
    brand: Brand
    color: Color
    typography: Typography
    layout: Layout
    pdf: PDF
    html: HTML


def load_theme(path: str | Path) -> ThemeTokens:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return ThemeTokens(
        brand=Brand(**(data.get("brand") or {})),
        color=Color(**(data.get("color") or {})),
        typography=Typography(**(data.get("typography") or {})),
        layout=Layout(**(data.get("layout") or {})),
        pdf=PDF(**(data.get("pdf") or {})),
        html=HTML(**(data.get("html") or {})),
    )


def tokens_to_css_vars(tokens: ThemeTokens) -> dict[str, str]:
    """Flatten theme tokens into CSS custom properties for HTML template."""
    t = tokens
    vars_map: dict[str, str] = {
        "--tf-primary": t.color.primary,
        "--tf-text": t.color.text,
        "--tf-muted": t.color.muted,
        "--tf-border": t.color.border,
        "--tf-bg": t.color.background,
        "--tf-link": t.pdf.link_color,
        "--tf-heading": t.pdf.heading_color,
        "--tf-font-body": t.typography.font_body,
        "--tf-font-heading": t.typography.font_heading,
        "--tf-font-logo": t.typography.font_logo,
        "--tf-font-mono": t.typography.font_mono,
        "--tf-max-width": f"{t.html.max_width_px}px",
        "--tf-heading-weight": str(t.html.heading_weight),
    }
    if t.color.primary_light:
        vars_map["--tf-primary-light"] = t.color.primary_light
    if t.color.primary_dark:
        vars_map["--tf-primary-dark"] = t.color.primary_dark
    if t.color.secondary:
        vars_map["--tf-secondary"] = t.color.secondary
    if t.color.accent:
        vars_map["--tf-accent"] = t.color.accent
    return vars_map
