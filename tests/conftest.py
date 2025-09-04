from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# Ensure 'src' is importable during CI runs
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse=True)
def chdir_project_root() -> None:
    """
    Run tests from the project root so relative template/assets paths resolve.
    """
    os.chdir(PROJECT_ROOT)
