from __future__ import annotations


class TrustforgeError(Exception):
    """Base class for all Trustforge domain errors."""


class ThemeLoadError(TrustforgeError):
    """Raised when a theme cannot be loaded or parsed."""


class AssetMissingError(TrustforgeError):
    """Raised when a required asset (logo, font, template) is missing."""


class DependencyMissingError(TrustforgeError):
    """Raised when a required external dependency is missing (e.g., xelatex)."""


class InvalidFrontmatterError(TrustforgeError):
    """Raised when a policy file is missing or has invalid YAML frontmatter."""


class HTMLBuildError(TrustforgeError):
    """Raised for unrecoverable errors while building HTML output."""


class PDFBuildError(TrustforgeError):
    """Raised for unrecoverable errors while building PDF output."""
