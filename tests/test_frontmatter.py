from __future__ import annotations

from pathlib import Path

import pytest

from trustforge.common.errors import FrontmatterError
from trustforge.common.md import parse_policy_markdown


def test_frontmatter_parse_valid(tmp_path: Path) -> None:
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
    assert meta.version == "1.0.0"
    assert "Body" in body


def test_frontmatter_missing_block(tmp_path: Path) -> None:
    md = "# No frontmatter"
    p = tmp_path / "p.md"
    p.write_text(md, encoding="utf-8")
    with pytest.raises(FrontmatterError) as e:
        parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
    assert "Missing or invalid frontmatter" in str(e.value)


def test_frontmatter_invalid_yaml(tmp_path: Path) -> None:
    # Missing colon after "title"
    md = """---
title "oops"
---
# Body
"""
    p = tmp_path / "bad.md"
    p.write_text(md, encoding="utf-8")
    with pytest.raises(Exception):  # YAML parser error, not our custom FrontmatterError
        parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)


def test_frontmatter_with_bom(tmp_path: Path) -> None:
    md = """\ufeff---
title: 'BOM Test'
version: "1.0.0"
owner: "O"
last_reviewed: "2025-01-01"
---
Body
"""
    p = tmp_path / "bom.md"
    p.write_text(md, encoding="utf-8")
    meta, body = parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
    assert meta.title == "BOM Test"
    assert meta.version == "1.0.0"
    assert meta.owner == "O"
    assert "Body" in body


def test_frontmatter_extra_fields(tmp_path: Path) -> None:
    md = """---
title: "With Subtitle"
version: "1.0.0"
owner: "O"
last_reviewed: "2025-01-01"
subtitle: "Optional subtitle"
footer: "Optional footer"
---
Content here
"""
    p = tmp_path / "extra.md"
    p.write_text(md, encoding="utf-8")
    meta, body = parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
    assert meta.subtitle == "Optional subtitle"
    assert meta.footer == "Optional footer"
    assert "Content" in body
