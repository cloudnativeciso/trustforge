from __future__ import annotations

from pathlib import Path


def resolve_theme_path(
    theme_arg: str | None, default_relative: str = "themes/neutral.yaml"
) -> Path:
    """
    Resolve the theme file path.

    Priority:
      1) Explicit --theme argument (absolute or relative to CWD)
      2) Default relative path (e.g., themes/neutral.yaml)
      3) Package-relative default (if running from another CWD)

    Returns the first existing path; raises FileNotFoundError otherwise.
    """
    candidates: list[Path] = []

    if theme_arg:
        p = Path(theme_arg)
        candidates.append(p if p.is_absolute() else Path.cwd() / p)

    candidates.append(Path.cwd() / default_relative)

    for c in candidates:
        if c.exists():
            return c

    pkg_default = Path(__file__).resolve().parents[1] / default_relative
    if pkg_default.exists():
        return pkg_default

    tried = ", ".join(str(c) for c in candidates + [pkg_default])
    raise FileNotFoundError(f"Theme file not found. Tried: {tried}")
