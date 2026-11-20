"""SQLite database: connection handling and the table layout."""

import sqlite3
from pathlib import Path

from . import config

# One row per film file. The "parsed_" columns come from the file name (stage 1).
# The metadata columns (title, overview, poster...) get filled from TMDB in stage 3,
# or by hand with the editing tool later.
SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,

    -- The file on disk
    file_path      TEXT    NOT NULL UNIQUE,
    file_name      TEXT    NOT NULL,
    file_size      INTEGER,
    missing        INTEGER NOT NULL DEFAULT 0,   -- 1 if the file has disappeared

    -- What we read from the file name
    parsed_title   TEXT,
    parsed_year    INTEGER,

    -- Metadata (from TMDB or edited by hand)
    title          TEXT,
    year           INTEGER,
    overview       TEXT,
    runtime        INTEGER,
    tmdb_id        INTEGER,
    poster_path    TEXT,
    backdrop_path  TEXT,
    trailer_url    TEXT,

    -- 'unmatched', 'matched' or 'needs_review'
    match_status   TEXT    NOT NULL DEFAULT 'unmatched',
    -- JSON list of field names the user edited by hand, e.g. '["overview"]'.
    -- A TMDB refresh must never overwrite these.
    locked_fields  TEXT    NOT NULL DEFAULT '[]',

    added_at       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open the database. Rows come back as dict-like objects: row["title"]."""
    db_path = db_path or config.DATABASE_PATH
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: FastAPI may use the connection from a worker thread
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create the tables if they don't exist yet. Safe to call every startup."""
    conn.executescript(SCHEMA)
    conn.commit()


def get_db():
    """FastAPI dependency: gives each request its own connection, then closes it."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
