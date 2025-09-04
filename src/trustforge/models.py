from __future__ import annotations

import datetime

from pydantic import BaseModel


class PolicyMeta(BaseModel):
    title: str
    version: str
    owner: str
    last_reviewed: datetime.date
    applies_to: list[str] | None = None
    refs: list[str] | None = None
    # New optional fields
    subtitle: str | None = None
    footer: str | None = None


# Theme token models (trimmed to only fields we use in patches)
class Brand(BaseModel):
    name: str
    logo_path: str | None = None
    logo_height_mm: int | None = 18


class Color(BaseModel):
    primary: str
    text: str
    muted: str
    border: str
    background: str
    primary_light: str | None = None
    primary_dark: str | None = None


class Typography(BaseModel):
    font_body: str
    font_heading: str
    font_logo: str | None = None
    font_mono: str
    scale: float
    line_height: float


class Layout(BaseModel):
    page_margins_mm: int
    header: bool
    footer: bool
    watermark: str | None = None


class PDF(BaseModel):
    link_color: str
    heading_color: str


class HTML(BaseModel):
    max_width_px: int
    heading_weight: int


class ThemeTokens(BaseModel):
    brand: Brand
    color: Color
    typography: Typography
    layout: Layout
    pdf: PDF
    html: HTML
