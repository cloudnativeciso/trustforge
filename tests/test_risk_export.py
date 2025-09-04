from __future__ import annotations

import csv
from pathlib import Path

from trustforge.pipeline.risk_export import load_risks_from_yaml, write_risks_csv


def _sample_risks_yaml(tmp_path: Path) -> Path:
    y = tmp_path / "risks.yaml"
    y.write_text(
        """\
- id: R-001
  title: Public S3 bucket exposure
  description: "Misconfigured S3 bucket may expose sensitive customer data."
  severity: High
  likelihood: Possible
  owner: CISO
  status: Open
  treatment: Mitigate
  target_date: "2025-10-31"
  control_refs: ["PR.AC-01", "DE.AE-01"]

- id: R-002
  title: Model prompt injection
  description: "LLM-based agent may follow adversarial instructions."
  severity: High
  likelihood: Likely
  owner: Security Engineering
  status: Mitigating
  treatment: Mitigate
  control_refs: ["ID.GV-01"]
""",
        encoding="utf-8",
    )
    return y


def test_load_and_export_risks(tmp_path: Path) -> None:
    src = _sample_risks_yaml(tmp_path)
    risks = load_risks_from_yaml(src)
    assert len(risks) == 2
    assert risks[0].id == "R-001"
    assert risks[1].likelihood == "Likely"

    out = tmp_path / "risks.csv"
    result = write_risks_csv(out, risks)
    assert result == out
    assert out.exists()

    rows = list(csv.DictReader(out.read_text(encoding="utf-8").splitlines()))
    assert [r["id"] for r in rows] == ["R-001", "R-002"]
    # control refs are ';' joined
    assert rows[0]["control_refs"] == "PR.AC-01;DE.AE-01"
    # columns exist
    for col in [
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
    ]:
        assert col in rows[0]
