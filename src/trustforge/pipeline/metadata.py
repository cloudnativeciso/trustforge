from __future__ import annotations

import csv
from pathlib import Path

from ..common.md import parse_policy_markdown


def build_index_csv(policies_dir: Path, out_csv: Path) -> Path:
    rows = []
    for p in sorted(policies_dir.glob("*.md")):
        meta, _ = parse_policy_markdown(p.read_text(encoding="utf-8"))
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
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
            if rows
            else ["file", "title", "version", "owner", "last_reviewed", "applies_to", "refs"],
        )
        writer.writeheader()
        if rows:
            writer.writerows(rows)
    return out_csv
