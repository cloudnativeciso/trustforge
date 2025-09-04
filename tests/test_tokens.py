from __future__ import annotations

import re
from pathlib import Path

import pytest

from trustforge.common.theme import load_theme

THEME_FILES = [
    Path("themes/neutral.yaml"),
    Path("themes/cnciso.yaml"),  # optional
]

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


@pytest.mark.parametrize("theme_path", THEME_FILES)
def test_theme_contract(theme_path: Path):
    if not theme_path.exists():
        pytest.skip(f"{theme_path} not present; skipping")

    t = load_theme(str(theme_path))

    # Brand
    assert isinstance(t.brand.name, str) and t.brand.name.strip()
    assert isinstance(t.brand.logo_path, str)
    assert isinstance(t.brand.logo_height_mm, (int, float)) and t.brand.logo_height_mm > 0

    # Colors
    for name in ("primary", "text", "muted", "border", "background"):
        val = getattr(t.color, name)
        assert isinstance(val, str) and HEX.match(val), f"color.{name} must be hex"
    for name in ("primary_light", "primary_dark"):
        val = getattr(t.color, name, None)
        if val:
            assert HEX.match(val)

    # Typography
    assert isinstance(t.typography.font_body, str) and t.typography.font_body.strip()
    assert isinstance(t.typography.font_heading, str) and t.typography.font_heading.strip()
    assert isinstance(t.typography.font_logo, str) and t.typography.font_logo.strip()
    assert isinstance(t.typography.font_mono, str) and t.typography.font_mono.strip()
    assert isinstance(t.typography.scale, (int, float)) and t.typography.scale > 0
    assert isinstance(t.typography.line_height, (int, float)) and t.typography.line_height > 0

    # Layout
    assert isinstance(t.layout.page_margins_mm, (int, float)) and t.layout.page_margins_mm > 0
    assert isinstance(t.layout.header, bool)
    assert isinstance(t.layout.footer, bool)
    assert isinstance(t.layout.watermark, str)

    # PDF + HTML tokens
    assert HEX.match(t.pdf.link_color)
    assert HEX.match(t.pdf.heading_color)
    assert isinstance(t.html.max_width_px, int) and t.html.max_width_px > 0
    assert isinstance(t.html.heading_weight, int) and 100 <= t.html.heading_weight <= 900
