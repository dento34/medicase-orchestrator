"""Project-root-aware .env loader."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def project_root() -> Path:
    """Repo root (parent of `agents/`)."""
    return Path(__file__).resolve().parents[2]


def load(env_file: str = ".env") -> None:
    """Load .env from project root into os.environ."""
    load_dotenv(project_root() / env_file)


def get(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Required env var missing: {key}")
    return val
