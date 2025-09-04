from __future__ import annotations

import csv
from pathlib import Path

from trustforge.nist.csf20_map import nist_csf20_controls
from trustforge.pipeline.control_map import write_control_map_csv


def test_control_map_csv_writes(tmp_path: Path) -> None:
    out = tmp_path / "control_map.csv"
    result = write_control_map_csv(out)
    assert result == out
    assert out.exists()

    rows = list(csv.DictReader(out.read_text(encoding="utf-8").splitlines()))
    # minimal sanity checks
    assert len(rows) == len(list(nist_csf20_controls()))
    assert rows[0]["framework"] == "NIST CSF 2.0"
    for r in rows:
        # required columns present and non-empty
        assert r["function"]
        assert r["category"]
        assert r["control_id"]
        assert r["title"]
        assert r["description"]
