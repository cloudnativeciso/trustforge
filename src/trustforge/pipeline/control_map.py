from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ..nist.csf20_map import CsfControl, nist_csf20_controls


def write_control_map_csv(out_csv: Path, controls: Iterable[CsfControl] | None = None) -> Path:
    rows = []
    for c in controls or nist_csf20_controls():
        rows.append(
            {
                "framework": "NIST CSF 2.0",
                "function": c.function,
                "category": c.category,
                "control_id": c.subcategory_id,
                "title": c.title,
                "description": c.description,
            }
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "framework",
                "function",
                "category",
                "control_id",
                "title",
                "description",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return out_csv
