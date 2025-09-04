from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """
    Runtime configuration for Trustforge.
    Values come from environment variables or fall back to defaults.
    """

    theme_path: Path = Path("themes/neutral.yaml")
    out_dir: Path = Path("out")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("theme_path", mode="before")
    @classmethod
    def _expand_theme_path(cls, v: str | Path) -> Path:
        # Normalize to absolute path for downstream consumers
        return Path(v).expanduser().resolve()

    @field_validator("out_dir", mode="before")
    @classmethod
    def _expand_out_dir(cls, v: str | Path) -> Path:
        return Path(v).expanduser().resolve()


def load_settings() -> Settings:
    """
    Load runtime settings from environment variables with sane defaults.
    Ensures the constructed types match `Settings` (Path + Literal).
    """
    theme_env = os.getenv("TRUSTFORGE_THEME")
    out_env = os.getenv("TRUSTFORGE_OUT")
    log_env = os.getenv("TRUSTFORGE_LOG")

    theme_path = Path(theme_env) if theme_env else Path("themes/neutral.yaml")
    out_dir = Path(out_env) if out_env else Path("out")

    # Explicitly narrow to a Literal for mypy
    if log_env == "DEBUG":
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    elif log_env == "INFO":
        log_level = "INFO"
    elif log_env == "WARNING":
        log_level = "WARNING"
    elif log_env == "ERROR":
        log_level = "ERROR"
    elif log_env == "CRITICAL":
        log_level = "CRITICAL"
    else:
        log_level = "INFO"

    return Settings(theme_path=theme_path, out_dir=out_dir, log_level=log_level)
