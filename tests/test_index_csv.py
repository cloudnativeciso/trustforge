from __future__ import annotations

import csv
from pathlib import Path

from trustforge.pipeline.metadata import build_index_csv


def test_index_csv(tmp_path: Path) -> None:
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "a.md").write_text(
        """---
title: "A"
version: "1"
owner: "x"
last_reviewed: "2025-01-01"
applies_to: ["All"]
refs: ["R"]
---
# A
""",
        encoding="utf-8",
    )
    out_csv = tmp_path / "out.csv"
    p = build_index_csv(policies, out_csv)
    assert p.exists()
    rows = list(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    assert rows and rows[0]["title"] == "A"
