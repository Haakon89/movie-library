"""Library scanner: finds film files on disk and reads title + year from their names.

YOUR PART: implement the two functions marked TODO below.
    find_video_files()  - walk a folder and return the film files
    parse_filename()    - turn "The.Matrix.1999.1080p.mkv" into title + year

Check your work with:
    pytest                    (runs tests/test_scanner.py)
    python -m app.scanner     (prints what it finds in MOVIE_LIBRARY_PATH)

scan_library() at the bottom is already written: it uses your two functions
to save the results to the database.
"""

import sqlite3
from pathlib import Path

from guessit import guessit  # noqa: F401  (you'll use this in parse_filename)

# File extensions we treat as films. Compare in lowercase: ".MKV" counts too.
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".wmv", ".webm", ".mpg", ".mpeg"}


def find_video_files(root: Path) -> list[Path]:
    """Return every film file under `root`, including in subfolders, sorted.

    Rules (the tests check each one):
      - Only files whose extension is in VIDEO_EXTENSIONS (case-insensitive).
      - Look in subfolders too, at any depth.
      - Skip "sample" clips: files whose name contains the word "sample"
        (any case), e.g. "Heat.1995.sample.mkv" or "sample-heat.mkv".
      - Return a sorted list, so results are the same every time.

    Hints:
      - Path.rglob("*") walks a folder recursively.
      - path.is_file(), path.suffix, path.name and str.lower() are useful.
    """
    # TODO: implement this
    raise NotImplementedError("find_video_files is your job!")


def parse_filename(path: Path) -> dict:
    """Read the film title and year out of a file name.

    Returns a dict like {"title": "The Matrix", "year": 1999}.
    If there is no year in the name, "year" should be None.

    Hints:
      - guessit("The.Matrix.1999.1080p.BluRay.mkv") returns a dict-like object.
        Try it in a Python shell first and look at what comes back!
      - guess.get("title") and guess.get("year") return None if missing.
      - Pass just path.name, not the full path: folder names can confuse it.
      - If guessit finds no title, fall back to the file name without its
        extension (path.stem), so every film gets *some* title.
    """
    # TODO: implement this
    raise NotImplementedError("parse_filename is your job!")


# --------------------------------------------------------------------------
# Already written: saves scan results to the database.
# --------------------------------------------------------------------------

def scan_library(conn: sqlite3.Connection, root: Path) -> dict:
    """Scan `root` and update the movies table. Returns a summary of what changed.

    New files are added; files that already exist get their parsed info refreshed;
    files that have disappeared are marked missing=1 instead of deleted, so any
    metadata you've added by hand isn't lost if a drive is temporarily unplugged.
    """
    known = {row["file_path"] for row in conn.execute("SELECT file_path FROM movies")}
    found = find_video_files(root)
    seen: set[str] = set()
    added = 0

    for path in found:
        file_path = str(path.resolve())
        seen.add(file_path)
        parsed = parse_filename(path)
        if file_path not in known:
            added += 1
        conn.execute(
            """
            INSERT INTO movies (file_path, file_name, file_size, parsed_title, parsed_year)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                file_name    = excluded.file_name,
                file_size    = excluded.file_size,
                parsed_title = excluded.parsed_title,
                parsed_year  = excluded.parsed_year,
                missing      = 0,
                updated_at   = CURRENT_TIMESTAMP
            """,
            (file_path, path.name, path.stat().st_size, parsed["title"], parsed["year"]),
        )

    gone = known - seen
    conn.executemany(
        "UPDATE movies SET missing = 1, updated_at = CURRENT_TIMESTAMP WHERE file_path = ?",
        [(p,) for p in gone],
    )
    conn.commit()
    return {"found": len(found), "added": added, "missing": len(gone)}


if __name__ == "__main__":
    # Quick check without the database or server: python -m app.scanner
    from . import config

    if config.MOVIE_LIBRARY_PATH is None:
        raise SystemExit("Set MOVIE_LIBRARY_PATH in backend/.env first.")

    files = find_video_files(config.MOVIE_LIBRARY_PATH)
    print(f"Found {len(files)} film file(s) in {config.MOVIE_LIBRARY_PATH}\n")
    for f in files:
        info = parse_filename(f)
        print(f"  {info['title']!s:<35} {info['year']!s:<6} <- {f.name}")
