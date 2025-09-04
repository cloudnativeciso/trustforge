from __future__ import annotations

import csv
from pathlib import Path

from trustforge.common.errors import CSVIndexError
from trustforge.common.md import parse_policy_markdown


def build_index_csv(policies_dir: Path, out_csv: Path) -> Path:
    if not policies_dir.exists():
        raise CSVIndexError(policies_dir, "Policies directory does not exist.")
    rows: list[dict[str, str]] = []
    for p in sorted(policies_dir.glob("*.md")):
        meta, _ = parse_policy_markdown(p.read_text(encoding="utf-8"), source=p)
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
    if not rows:
        raise CSVIndexError(policies_dir, "No policy markdown files found (*.md).")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer: csv.DictWriter[str] = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return out_csv
