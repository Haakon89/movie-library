"""The web API. Run with:  uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs to try every endpoint in your browser.
"""

import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import connect, get_db, init_db
from .scanner import scan_library


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: make sure the tables exist.
    conn = connect()
    init_db(conn)
    conn.close()
    yield


app = FastAPI(title="Movie Library", lifespan=lifespan)

# Lets the React dev server (stage 2, port 5173) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    """A simple 'is the server alive?' check."""
    return {
        "status": "ok",
        "library_path": str(config.MOVIE_LIBRARY_PATH) if config.MOVIE_LIBRARY_PATH else None,
        "tmdb_key_set": bool(config.TMDB_API_KEY),
    }


@app.post("/api/scan")
def scan(conn: sqlite3.Connection = Depends(get_db)):
    """Scan MOVIE_LIBRARY_PATH for film files and update the database."""
    root = config.MOVIE_LIBRARY_PATH
    if root is None:
        raise HTTPException(400, "MOVIE_LIBRARY_PATH is not set in backend/.env")
    if not root.is_dir():
        raise HTTPException(400, f"Folder not found: {root}")
    return scan_library(conn, root)


@app.get("/api/movies")
def list_movies(q: str | None = None, conn: sqlite3.Connection = Depends(get_db)):
    """List films, optionally filtered by a search term (?q=matrix)."""
    sql = "SELECT * FROM movies WHERE missing = 0"
    params: list = []
    if q:
        # Search both the TMDB title (later) and the title from the file name.
        sql += " AND (title LIKE ? OR parsed_title LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY COALESCE(title, parsed_title) COLLATE NOCASE"
    return [dict(row) for row in conn.execute(sql, params)]


@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Movie not found")
    return dict(row)
