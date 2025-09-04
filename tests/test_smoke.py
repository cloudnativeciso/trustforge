from __future__ import annotations

from pathlib import Path

from trustforge.pipeline.render_html import render_html


def test_html_smoke(tmp_path: Path) -> None:
    """Basic integration: ensure a markdown file renders to valid HTML."""
    md = """---
title: "Doc"
version: "1"
owner: "O"
last_reviewed: "2025-01-01"
applies_to: ["All"]
refs: ["R"]
---
# Hi
This is **bold** and `code`.
"""
    src = tmp_path / "doc.md"
    src.write_text(md, encoding="utf-8")

    out = render_html(src)

    # File exists and is HTML
    assert out.exists()
    assert out.suffix == ".html"

    html = out.read_text(encoding="utf-8")

    # Minimal sanity checks: title, heading, inline markup survive
    assert "Doc" in html
    assert "<h1" in html and "Hi" in html
    assert "<strong>" in html or "<b>" in html  # depending on renderer
    assert "<code>" in html
    # Check at least one CSS var token was injected
    assert "--tf-primary" in html
