from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    theme_path: str = "themes/neutral.yaml"
    out_dir: str = "out"
    log_level: str = "INFO"


def load_settings() -> Settings:
    theme = os.getenv("TRUSTFORGE_THEME", "themes/neutral.yaml")
    out_dir = os.getenv("TRUSTFORGE_OUT", "out")
    log_level = os.getenv("TRUSTFORGE_LOG", "INFO")
    return Settings(theme_path=theme, out_dir=out_dir, log_level=log_level)
