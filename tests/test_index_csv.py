from __future__ import annotations

import csv
from pathlib import Path

import pytest

from trustforge.common.errors import CSVIndexError
from trustforge.pipeline.metadata import build_index_csv


def test_index_csv_success(tmp_path: Path) -> None:
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


def test_index_csv_multiple_files(tmp_path: Path) -> None:
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
    (policies / "b.md").write_text(
        """---
title: "B"
version: "2"
owner: "y"
last_reviewed: "2025-02-01"
applies_to: ["Eng"]
refs: ["S"]
---
# B
""",
        encoding="utf-8",
    )
    out_csv = tmp_path / "out.csv"
    p = build_index_csv(policies, out_csv)
    rows = list(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    titles = [row["title"] for row in rows]
    assert "A" in titles and "B" in titles
    assert len(rows) == 2


def test_index_csv_missing_dir(tmp_path: Path) -> None:
    missing_dir = tmp_path / "does_not_exist"
    out_csv = tmp_path / "out.csv"
    with pytest.raises(CSVIndexError) as e:
        build_index_csv(missing_dir, out_csv)
    assert "does not exist" in str(e.value)


def test_index_csv_no_md_files(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    out_csv = tmp_path / "out.csv"
    with pytest.raises(CSVIndexError) as e:
        build_index_csv(empty_dir, out_csv)
    assert "No policy markdown files" in str(e.value)
