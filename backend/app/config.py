"""Runtime settings. Read from the environment on every call (no caching) so
tests can redirect storage paths via ROTAVIVA_* env vars."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROTAVIVA_")

    # Directory of bundled, read-only preset maps (shipped in the repo).
    presets_dir: Path = _APP_DIR / "maps" / "presets"
    # Directory where user-registered maps are persisted (gitignored).
    data_dir: Path = _APP_DIR.parent / "data" / "maps"
    # SQLite database of optimization runs (gitignored).
    runs_db: Path = _APP_DIR.parent / "data" / "runs.db"
    # Brute force is skipped for subsets with N >= this guard.
    brute_force_guard: int = 10
    # Default random-restart count when the request omits it.
    default_restarts: int = 20


def get_settings() -> Settings:
    """Build a fresh Settings from the current environment."""
    return Settings()
