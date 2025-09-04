from __future__ import annotations

import datetime as _dt
from typing import Any, Iterable, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _re_split(value: str, delims: tuple[str, ...]) -> list[str]:
    """Lightweight multi-delimiter split."""
    import re as _re

    escaped = "".join(_re.escape(d) for d in delims)
    pat = f"[{escaped}]"
    return _re.split(pat, value)


class PolicyMeta(BaseModel):
    """
    Strongly-typed metadata parsed from the YAML front matter of a policy.

    Required:
      - title:         Human-friendly policy name
      - version:       Semantic or doc version string
      - owner:         Role or person ultimately responsible
      - last_reviewed: ISO date (YYYY-MM-DD)

    Optional:
      - applies_to:    List of audiences (string or list in YAML; normalized)
      - refs:          List of reference IDs/standards (string or list; normalized)
      - subtitle:      Short tagline/subtitle for PDF cover
      - footer:        Footer line for PDF (e.g., contact info)
    """

    # --- Core, required fields ---
    title: str = Field(..., description="Human-friendly policy name.")
    version: str = Field(..., description="Document version string.")
    owner: str = Field(..., description="Responsible role or person.")
    last_reviewed: _dt.date = Field(..., description="ISO date YYYY-MM-DD.")

    # --- Optional fields ---
    applies_to: Optional[List[str]] = Field(
        default=None, description="Audiences; may be a string or list in YAML."
    )
    refs: Optional[List[str]] = Field(
        default=None, description="Reference IDs/standards; string or list."
    )
    subtitle: Optional[str] = Field(default=None, description="Short subtitle for PDF cover.")
    footer: Optional[str] = Field(default=None, description="Footer line for PDF pages.")

    # Forbid unknown keys so front-matter typos fail fast
    model_config = ConfigDict(extra="forbid")

    # ------------------------
    # Validators / Normalizers
    # ------------------------

    @field_validator("title", "version", "owner", mode="before")
    @classmethod
    def _trim_non_empty(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("must be a string")
        s = v.strip()
        if not s:
            raise ValueError("may not be empty")
        return s

    @field_validator("last_reviewed", mode="before")
    @classmethod
    def _parse_iso_date(cls, v: Any) -> _dt.date:
        if isinstance(v, _dt.date):
            return v
        if isinstance(v, str):
            s = v.strip()
            try:
                return _dt.date.fromisoformat(s)
            except ValueError as e:
                raise ValueError("last_reviewed must be an ISO date (YYYY-MM-DD)") from e
        raise TypeError("last_reviewed must be a date or ISO date string")

    @staticmethod
    def _split_to_list(value: str) -> list[str]:
        parts = [p.strip() for p in _re_split(value, (",", ";", "|"))]
        return [p for p in parts if p]

    @field_validator("applies_to", "refs", mode="before")
    @classmethod
    def _normalize_listish(cls, v: Any) -> Optional[List[str]]:
        if v is None:
            return None
        if isinstance(v, str):
            items = cls._split_to_list(v)
            return items or None
        if isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
            items = [str(x).strip() for x in v]
            items = [x for x in items if x]
            return items or None
        raise TypeError("must be a string or list of strings")
