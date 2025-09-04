from __future__ import annotations

import hashlib
from pathlib import Path


def ensure_dir(p: str | Path) -> Path:
    path = Path(p)
    path.mkdir(parents=True, exist_ok=True)
    return path


def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
