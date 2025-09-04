from __future__ import annotations

import re
from typing import cast

import yaml
from markdown_it import MarkdownIt

from ..models import PolicyMeta

# Robust frontmatter:
# - optional UTF-8 BOM
# - allow spaces after '---'
# - handle \n or \r\n
FRONTMATTER_RE = re.compile(
    r"^\ufeff?---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z",
    re.S,
)


def parse_policy_markdown(text: str) -> tuple[PolicyMeta, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(
            "Missing or invalid frontmatter (--- ... ---) at top of file. "
            "Ensure the file begins with a YAML block delimited by '---' lines."
        )
    meta_raw, body = m.group(1), m.group(2)
    meta = PolicyMeta(**(yaml.safe_load(meta_raw) or {}))
    return meta, body


def md_to_html(body_md: str) -> str:
    md = MarkdownIt("commonmark")
    return cast(str, md.render(body_md))
