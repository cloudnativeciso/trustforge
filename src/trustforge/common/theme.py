# src/trustforge/common/theme.py
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from trustforge.common.errors import TemplateError

# --- Data models ----------------------------------------------------------------


@dataclass
class Brand:
    name: str = "Trustforge"
    logo_path: str = ""
    logo_height_mm: int = 24  # used by PDF cover


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
    accent: str | None = None  # support for 'accent'


@dataclass
class Typography:
    font_body: str = "Inter"
    font_heading: str = "Inter"
    font_logo: str = "Inter"
    font_mono: str = "Menlo"
    scale: float = 1.0  # relative type scale
    line_height: float = 1.5  # paragraph line height


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


# --- Validation helpers ---------------------------------------------------------

_HEX6 = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _is_hex6(value: str) -> bool:
    return bool(_HEX6.match(value))


def _validate_required_hex(field: str, value: str, theme_path: Path) -> None:
    if not isinstance(value, str) or not _is_hex6(value):
        raise TemplateError(
            str(theme_path),
            f"Invalid color for '{field}': '{value}'. Expected 6-digit hex like #AABBCC.",
        )


def _validate_optional_hex(field: str, value: str | None, theme_path: Path) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not _is_hex6(value):
        raise TemplateError(
            str(theme_path),
            f"Invalid color for optional '{field}': '{value}'. Expected 6-digit hex like #AABBCC.",
        )


def _validate_positive_int(field: str, value: int, theme_path: Path) -> None:
    if not isinstance(value, int) or value <= 0:
        raise TemplateError(str(theme_path), f"'{field}' must be a positive integer (got {value}).")


def _validate_positive_float(field: str, value: float, theme_path: Path) -> None:
    if not isinstance(value, (int, float)) or float(value) <= 0:
        raise TemplateError(str(theme_path), f"'{field}' must be a positive number (got {value}).")


def _validate_heading_weight(value: int, theme_path: Path) -> None:
    # Common sensible bounds (CSS weights)
    if not isinstance(value, int) or not (100 <= value <= 900):
        raise TemplateError(
            str(theme_path),
            f"'html.heading_weight' should be between 100 and 900 (got {value}).",
        )


def _validate_fonts(t: Typography, theme_path: Path) -> None:
    # Keep this lightweight: just ensure non-empty strings.
    for field_name in ("font_body", "font_heading", "font_logo", "font_mono"):
        value = getattr(t, field_name)
        if not isinstance(value, str) or not value.strip():
            raise TemplateError(str(theme_path), f"'{field_name}' must be a non-empty string.")


def _validate_tokens(tokens: ThemeTokens, theme_path: Path) -> None:
    # Colors
    c = tokens.color
    _validate_required_hex("color.primary", c.primary, theme_path)
    _validate_required_hex("color.text", c.text, theme_path)
    _validate_required_hex("color.muted", c.muted, theme_path)
    _validate_required_hex("color.border", c.border, theme_path)
    _validate_required_hex("color.background", c.background, theme_path)
    _validate_optional_hex("color.primary_light", c.primary_light, theme_path)
    _validate_optional_hex("color.primary_dark", c.primary_dark, theme_path)
    _validate_optional_hex("color.secondary", c.secondary, theme_path)
    _validate_optional_hex("color.accent", c.accent, theme_path)

    # PDF colors
    _validate_required_hex("pdf.link_color", tokens.pdf.link_color, theme_path)
    _validate_required_hex("pdf.heading_color", tokens.pdf.heading_color, theme_path)

    # Typography & layout & HTML
    _validate_fonts(tokens.typography, theme_path)
    _validate_positive_float("typography.scale", tokens.typography.scale, theme_path)
    _validate_positive_float("typography.line_height", tokens.typography.line_height, theme_path)
    _validate_positive_int("layout.page_margins_mm", tokens.layout.page_margins_mm, theme_path)
    _validate_positive_int("html.max_width_px", tokens.html.max_width_px, theme_path)
    _validate_heading_weight(tokens.html.heading_weight, theme_path)


# --- Public API ----------------------------------------------------------------


def load_theme(path: str | Path) -> ThemeTokens:
    """
    Load a YAML theme file into ThemeTokens with validation.
    Raises TemplateError with a helpful message if the file is missing,
    malformed, or contains invalid values.
    """
    theme_path = Path(path)
    try:
        raw = theme_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise TemplateError(str(theme_path), "Theme file not found.") from e
    except OSError as e:
        raise TemplateError(str(theme_path), f"Unable to read theme file: {e}") from e

    try:
        data: dict[str, Any] = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            raise TemplateError(str(theme_path), "Theme root must be a mapping/object.")
    except yaml.YAMLError as e:
        raise TemplateError(str(theme_path), f"YAML parse error: {e}") from e

    tokens = ThemeTokens(
        brand=Brand(**(data.get("brand") or {})),
        color=Color(**(data.get("color") or {})),
        typography=Typography(**(data.get("typography") or {})),
        layout=Layout(**(data.get("layout") or {})),
        pdf=PDF(**(data.get("pdf") or {})),
        html=HTML(**(data.get("html") or {})),
    )

    # Validate & normalize
    _validate_tokens(tokens, theme_path)
    return tokens


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
