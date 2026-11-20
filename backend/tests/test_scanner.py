"""Tests for app/scanner.py. Run from the backend folder with:  pytest -v

They all fail until you implement find_video_files() and parse_filename().
Make them pass one by one!
"""

from pathlib import Path

import pytest

from app import scanner
from app.database import connect, init_db
from app.scanner import find_video_files, parse_filename, scan_library


def make_files(root: Path, names: list[str]) -> None:
    """Create empty files (and any subfolders) under root."""
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


# ---------- find_video_files ----------

def test_finds_video_files(tmp_path):
    make_files(tmp_path, ["Heat.1995.mkv", "Alien.1979.mp4"])
    assert [p.name for p in find_video_files(tmp_path)] == ["Alien.1979.mp4", "Heat.1995.mkv"]


def test_ignores_non_video_files(tmp_path):
    make_files(tmp_path, ["Heat.1995.mkv", "Heat.1995.srt", "Heat.1995.nfo", "notes.txt", "poster.jpg"])
    assert [p.name for p in find_video_files(tmp_path)] == ["Heat.1995.mkv"]


def test_extension_is_case_insensitive(tmp_path):
    make_files(tmp_path, ["HEAT.1995.MKV"])
    assert [p.name for p in find_video_files(tmp_path)] == ["HEAT.1995.MKV"]


def test_searches_subfolders(tmp_path):
    make_files(tmp_path, ["Heat (1995)/Heat.1995.mkv", "a/b/c/Alien.1979.mp4"])
    assert sorted(p.name for p in find_video_files(tmp_path)) == ["Alien.1979.mp4", "Heat.1995.mkv"]


def test_skips_sample_clips(tmp_path):
    make_files(tmp_path, ["Heat.1995.mkv", "Heat.1995.sample.mkv", "SAMPLE-heat.mkv"])
    assert [p.name for p in find_video_files(tmp_path)] == ["Heat.1995.mkv"]


def test_ignores_folders_that_look_like_videos(tmp_path):
    (tmp_path / "weird.folder.mkv").mkdir()
    assert find_video_files(tmp_path) == []


# ---------- parse_filename ----------

@pytest.mark.parametrize(
    "file_name, title, year",
    [
        ("The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv", "The Matrix", 1999),
        ("Spirited Away (2001).mp4", "Spirited Away", 2001),
        ("Heat.mkv", "Heat", None),
    ],
)
def test_parse_filename(file_name, title, year):
    assert parse_filename(Path(file_name)) == {"title": title, "year": year}


def test_parse_filename_falls_back_to_file_name(monkeypatch):
    # Pretend guessit couldn't find a title at all.
    monkeypatch.setattr(scanner, "guessit", lambda name: {})
    assert parse_filename(Path("mystery_file.mkv")) == {"title": "mystery_file", "year": None}


# ---------- scan_library (already written, but it needs your functions) ----------

def test_scan_library_adds_and_marks_missing(tmp_path):
    make_files(tmp_path, ["The.Matrix.1999.mkv", "Heat.1995.mkv"])
    conn = connect(":memory:")
    init_db(conn)

    assert scan_library(conn, tmp_path) == {"found": 2, "added": 2, "missing": 0}
    # Scanning again changes nothing
    assert scan_library(conn, tmp_path) == {"found": 2, "added": 0, "missing": 0}

    (tmp_path / "Heat.1995.mkv").unlink()
    assert scan_library(conn, tmp_path) == {"found": 1, "added": 0, "missing": 1}

    row = conn.execute("SELECT * FROM movies WHERE file_name = 'The.Matrix.1999.mkv'").fetchone()
    assert (row["parsed_title"], row["parsed_year"]) == ("The Matrix", 1999)
