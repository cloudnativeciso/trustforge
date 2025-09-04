from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import yaml

from ..risk.models import RiskItem


def load_risks_from_yaml(path: Path) -> list[RiskItem]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    risks: list[RiskItem] = []
    for row in data:
        risks.append(
            RiskItem(
                id=str(row["id"]),
                title=row["title"],
                description=row.get("description", ""),
                severity=row["severity"],
                likelihood=row["likelihood"],
                owner=row.get("owner", "CISO"),
                status=row.get("status", "Open"),
                treatment=row.get("treatment", "Mitigate"),
                target_date=row.get("target_date"),
                control_refs=row.get("control_refs") or None,
            )
        )
    return risks


def write_risks_csv(out_csv: Path, risks: Iterable[RiskItem]) -> Path:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "title",
                "description",
                "severity",
                "likelihood",
                "owner",
                "status",
                "treatment",
                "target_date",
                "control_refs",
            ],
        )
        writer.writeheader()
        for r in risks:
            writer.writerow(
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "severity": r.severity,
                    "likelihood": r.likelihood,
                    "owner": r.owner,
                    "status": r.status,
                    "treatment": r.treatment,
                    "target_date": r.target_date or "",
                    "control_refs": ";".join(r.control_refs) if r.control_refs else "",
                }
            )
    return out_csv
