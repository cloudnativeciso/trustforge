from __future__ import annotations

from pathlib import Path

from trustforge.common.md import parse_policy_markdown


def test_frontmatter_parse(tmp_path: Path) -> None:
    md = """---
title: "T"
version: "1.0.0"
owner: "O"
last_reviewed: "2025-01-01"
applies_to: ["All"]
refs: ["X"]
---
# Body
"""
    p = tmp_path / "p.md"
    p.write_text(md, encoding="utf-8")
    meta, body = parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
    assert meta.title == "T"
    assert "Body" in body
