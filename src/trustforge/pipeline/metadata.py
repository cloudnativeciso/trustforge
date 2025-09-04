from __future__ import annotations

import csv
from pathlib import Path

from trustforge.common.errors import CSVIndexError
from trustforge.common.md import parse_policy_markdown

# Fixed header order for determinism
_HEADERS: list[str] = [
    "file",
    "title",
    "version",
    "owner",
    "last_reviewed",
    "applies_to",
    "refs",
]


def build_index_csv(policies_dir: Path, out_csv: Path) -> Path:
    """
    Scan `policies_dir` for *.md files, parse YAML frontmatter, and write a CSV index.
    Raises CSVIndexError with a helpful message if:
      - the directory is missing,
      - there are no *.md files,
      - a policy file has invalid or missing frontmatter.
    """
    if not policies_dir.exists():
        raise CSVIndexError(policies_dir, "Policies directory does not exist.")

    markdown_files = sorted(policies_dir.glob("*.md"))
    if not markdown_files:
        raise CSVIndexError(policies_dir, "No policy markdown files found (*.md).")

    rows: list[dict[str, str]] = []
    for p in markdown_files:
        try:
            meta, _ = parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
        except Exception as e:
            # Surface which file broke and why
            raise CSVIndexError(p, f"Failed to parse frontmatter: {e}") from e

        # Basic sanity: ensure essential fields exist
        if not meta.title:
            raise CSVIndexError(p, "Missing required field: 'title'")
        if not meta.version:
            raise CSVIndexError(p, "Missing required field: 'version'")
        if not meta.owner:
            raise CSVIndexError(p, "Missing required field: 'owner'")

        rows.append(
            {
                "file": p.name,
                "title": meta.title,
                "version": meta.version,
                "owner": meta.owner,
                "last_reviewed": str(meta.last_reviewed),
                "applies_to": ";".join(meta.applies_to or []),
                "refs": ";".join(meta.refs or []),
            }
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer: csv.DictWriter[str] = csv.DictWriter(f, fieldnames=_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    return out_csv
