from __future__ import annotations

from pathlib import Path


class TrustforgeError(Exception):
    """Base class for all Trustforge errors."""


class FrontmatterError(TrustforgeError):
    """Raised when a policy markdown file has missing/invalid YAML frontmatter."""

    def __init__(self, source: str | Path, message: str) -> None:
        super().__init__(f"{source}: {message}")
        self.source = str(source)


class TemplateError(TrustforgeError):
    """Raised when a template (HTML/LaTeX) is missing or malformed."""

    def __init__(self, template: str | Path, message: str) -> None:
        super().__init__(f"Template error [{template}]: {message}")
        self.template = str(template)


class AssetNotFoundError(TrustforgeError):
    """Raised when a referenced asset (logo, font, etc.) cannot be found."""

    def __init__(self, asset: str | Path) -> None:
        super().__init__(f"Asset not found: {asset}")
        self.asset = str(asset)


class MissingDependencyError(TrustforgeError):
    """Raised when a required system dependency is missing (e.g., xelatex)."""

    def __init__(self, binary: str) -> None:
        super().__init__(f"Missing required dependency: {binary}. Please install it and retry.")
        self.binary = binary


class LaTeXError(TrustforgeError):
    """Raised when XeLaTeX returns a non-zero exit status."""

    def __init__(self, tex_file: str | Path, log_file: str | Path | None = None) -> None:
        msg = f"LaTeX failed compiling: {tex_file}"
        if log_file:
            msg += f" (see log: {log_file})"
        super().__init__(msg)
        self.tex_file = str(tex_file)
        self.log_file = str(log_file) if log_file else None


class CSVIndexError(TrustforgeError):
    """Raised for CSV index build problems (e.g., missing policies dir)."""

    def __init__(self, location: str | Path, message: str) -> None:
        super().__init__(f"CSV index error at [{location}]: {message}")
        self.location = str(location)


class RenderError(TrustforgeError):
    """Generic render pipeline error wrapper."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"Render error during '{stage}': {message}")
        self.stage = stage


__all__ = [
    "TrustforgeError",
    "FrontmatterError",
    "TemplateError",
    "AssetNotFoundError",
    "MissingDependencyError",
    "LaTeXError",
    "CSVIndexError",
    "RenderError",
]
