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
# - handle \n or \r\n uniformly
FRONTMATTER_RE = re.compile(
    r"^\ufeff?---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z",
    re.S,
)


def _strip_bom(s: str) -> str:
    """Remove a UTF-8 BOM if present."""
    return s[1:] if s.startswith("\ufeff") else s


def _normalize_newlines(s: str) -> str:
    """Normalize CRLF to LF for consistent parsing and hashing."""
    return s.replace("\r\n", "\n")


def parse_policy_markdown(text: str, source: str | Path = "<memory>") -> tuple[PolicyMeta, str]:
    """
    Parse a markdown string with YAML frontmatter and return (meta, body).

    Expected structure (YAML frontmatter followed by Markdown body):

        ---
        title: "..."
        version: "..."
        # ...any other fields...
        ---
        # Markdown starts here

    Raises:
        FrontmatterError: if the frontmatter block is missing or YAML is invalid.
    """
    # Pre-normalize input to make the regex deterministic across platforms.
    text = _normalize_newlines(_strip_bom(text))

    m = FRONTMATTER_RE.match(text)
    if not m:
        raise FrontmatterError(
            source,
            "Missing or invalid frontmatter (--- ... ---) at top of file. "
            "Ensure the document begins with a YAML block delimited by '---' lines.",
        )

    meta_raw, body = m.group(1), m.group(2)

    # Parse YAML with clear diagnostics.
    try:
        meta_dict = yaml.safe_load(meta_raw) or {}
        if not isinstance(meta_dict, dict):
            # Guard against YAML producing non-dict (e.g., a list or string).
            raise TypeError(
                f"Frontmatter must be a mapping object, got {type(meta_dict).__name__}."
            )
    except (yaml.YAMLError, TypeError) as err:
        # Surface line/column info when available.
        detail = str(err)
        if isinstance(err, yaml.MarkedYAMLError) and err.problem_mark is not None:
            mark = err.problem_mark
            detail = f"{detail} (line {mark.line + 1}, column {mark.column + 1})"
        raise FrontmatterError(source, f"Invalid YAML frontmatter: {detail}") from err

    # Delegate schema validation to PolicyMeta (pydantic model).
    meta = PolicyMeta(**meta_dict)

    # Return body as-is (but normalized to LF newlines).
    return meta, body


def md_to_html(body_md: str) -> str:
    """
    Convert Markdown (CommonMark) to HTML using markdown-it-py.

    Notes:
        - We intentionally keep the renderer minimal and deterministic.
        - If you later want tables, task lists, etc., consider enabling plugins here.
    """
    md = MarkdownIt("commonmark")
    # markdown-it's render is typed as Any; cast to str for mypy.
    return cast(str, md.render(body_md))
