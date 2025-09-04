from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import yaml
from markdown_it import MarkdownIt

from trustforge.common.errors import FrontmatterError
from trustforge.models import PolicyMeta

# Robust frontmatter:
# - optional UTF-8 BOM
# - allow spaces after '---'
# - handle \n or \r\n
FRONTMATTER_RE = re.compile(
    r"^\ufeff?---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z",
    re.S,
)


def parse_policy_markdown(text: str, source: str | Path = "<memory>") -> tuple[PolicyMeta, str]:
    """
    Parse a markdown string with YAML frontmatter and return (meta, body).
    Raises FrontmatterError if the frontmatter block is missing/invalid.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise FrontmatterError(
            source,
            "Missing or invalid frontmatter (--- ... ---) at top of file. "
            "Ensure the file begins with a YAML block delimited by '---' lines.",
        )
    meta_raw, body = m.group(1), m.group(2)
    meta = PolicyMeta(**(yaml.safe_load(meta_raw) or {}))
    return meta, body


def md_to_html(body_md: str) -> str:
    md = MarkdownIt("commonmark")
    # markdown-it types return Any; cast it to keep mypy happy.
    return cast(str, md.render(body_md))
