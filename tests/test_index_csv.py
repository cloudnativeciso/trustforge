from pathlib import Path

from src.trustforge.pipeline.metadata import build_index_csv


def test_index(tmp_path: Path):
    out = tmp_path / "policies.csv"
    p = build_index_csv(Path("policies"), out)
    assert p.exists()
    assert p.read_text(encoding="utf-8").startswith("file,title,version")
