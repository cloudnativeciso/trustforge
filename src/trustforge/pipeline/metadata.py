from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ..common.md import parse_policy_markdown
from ..errors import InvalidFrontmatterError, TrustforgeError


def _join_safe(values: Iterable[str] | None) -> str:
    return ";".join(values or [])


def build_index_csv(policies_dir: Path, out_csv: Path) -> Path:
    if not policies_dir.exists():
        raise FileNotFoundError(policies_dir)

    rows = []
    for p in sorted(policies_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        try:
            meta, _ = parse_policy_markdown(text)
        except ValueError as e:
            raise InvalidFrontmatterError(f"{p.name}: {e}") from e

        rows.append(
            {
                "file": p.name,
                "title": meta.title,
                "version": meta.version,
                "owner": meta.owner,
                "last_reviewed": str(meta.last_reviewed),
                "applies_to": _join_safe(meta.applies_to),
                "refs": _join_safe(meta.refs),
            }
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "file",
                    "title",
                    "version",
                    "owner",
                    "last_reviewed",
                    "applies_to",
                    "refs",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        raise TrustforgeError(f"Failed to write index CSV: {e}") from e

    return out_csv
