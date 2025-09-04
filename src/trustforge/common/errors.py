from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

# Simple alias to clarify the intent in signatures
PathLike = Union[str, Path]


class TrustforgeError(Exception):
    """Base class for all Trustforge errors."""


class FrontmatterError(TrustforgeError):
    """Raised when a policy markdown file has missing/invalid YAML frontmatter."""

    __slots__ = ("source",)

    def __init__(self, source: PathLike, message: str) -> None:
        self.source = str(source)
        super().__init__(f"{self.source}: {message}")


class TemplateError(TrustforgeError):
    """Raised when a template (HTML/LaTeX) is missing or malformed."""

    __slots__ = ("template",)

    def __init__(self, template: PathLike, message: str) -> None:
        self.template = str(template)
        super().__init__(f"Template error [{self.template}]: {message}")


class AssetNotFoundError(TrustforgeError):
    """Raised when a referenced asset (logo, font, etc.) cannot be found."""

    __slots__ = ("asset",)

    def __init__(self, asset: PathLike) -> None:
        self.asset = str(asset)
        super().__init__(f"Asset not found: {self.asset}")


class MissingDependencyError(TrustforgeError):
    """Raised when a required system dependency is missing (e.g., xelatex)."""

    __slots__ = ("binary",)

    def __init__(self, binary: str) -> None:
        self.binary = binary
        super().__init__(
            f"Missing required dependency: {self.binary}. Please install it and retry."
        )


class LaTeXError(TrustforgeError):
    """Raised when XeLaTeX returns a non-zero exit status."""

    __slots__ = ("tex_file", "log_file")

    def __init__(self, tex_file: PathLike, log_file: Optional[PathLike] = None) -> None:
        self.tex_file = str(tex_file)
        self.log_file = str(log_file) if log_file is not None else None
        msg = f"LaTeX failed compiling: {self.tex_file}"
        if self.log_file:
            msg += f" (see log: {self.log_file})"
        super().__init__(msg)


class CSVIndexError(TrustforgeError):
    """Raised for CSV index build problems (e.g., missing policies dir)."""

    __slots__ = ("location",)

    def __init__(self, location: PathLike, message: str) -> None:
        self.location = str(location)
        super().__init__(f"CSV index error at [{self.location}]: {message}")


class RenderError(TrustforgeError):
    """Generic render pipeline error wrapper."""

    __slots__ = ("stage",)

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(f"Render error during '{self.stage}': {message}")


__all__ = [
    "PathLike",
    "TrustforgeError",
    "FrontmatterError",
    "TemplateError",
    "AssetNotFoundError",
    "MissingDependencyError",
    "LaTeXError",
    "CSVIndexError",
    "RenderError",
]
