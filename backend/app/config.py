"""App settings, read from environment variables / the backend/.env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# The backend/ folder (this file lives in backend/app/config.py)
BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BACKEND_DIR / ".env")


def _resolve(path_str: str) -> Path:
    """Relative paths in .env are treated as relative to the backend/ folder."""
    path = Path(path_str).expanduser()
    return (path if path.is_absolute() else BACKEND_DIR / path).resolve()


MOVIE_LIBRARY_PATH: Path | None = (
    _resolve(os.environ["MOVIE_LIBRARY_PATH"]) if os.environ.get("MOVIE_LIBRARY_PATH") else None
)
DATABASE_PATH: Path = _resolve(os.environ.get("DATABASE_PATH", "data/library.db"))
TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "")
