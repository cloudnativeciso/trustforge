from __future__ import annotations

from pathlib import Path

from trustforge.pipeline.render_html import render_html


def test_html_smoke(tmp_path: Path) -> None:
    md = """---
title: "Doc"
version: "1"
owner: "O"
last_reviewed: "2025-01-01"
applies_to: ["All"]
refs: ["R"]
---
# Hi
"""
    policies = tmp_path / "policies"
    policies.mkdir()
    src = policies / "doc.md"
    src.write_text(md, encoding="utf-8")

    # We rely on default theme path in Settings; ensure cwd is project root via conftest.
    out = render_html(src)
    assert out.exists()
    assert out.suffix == ".html"
