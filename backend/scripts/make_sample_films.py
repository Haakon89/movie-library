"""Create empty "film files" with realistic, messy names to test the scanner on.

Run from the backend folder:  python scripts/make_sample_films.py
They go in movie-library/sample_films/ (ignored by Git). The files are empty (0 bytes),
so they won't play, but the scanner only looks at names.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "sample_films"

NAMES = [
    # Typical release-style names
    "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
    "Inception.2010.720p.BRRip.x264.AAC-ETRG.mp4",
    "Parasite.2019.KOREAN.1080p.WEBRip.x265.mkv",
    # Tidy names, films in their own folder
    "Spirited Away (2001)/Spirited Away (2001).mp4",
    "Heat (1995)/Heat (1995).mkv",
    "Heat (1995)/Heat (1995).srt",          # subtitle: should be ignored
    "Heat (1995)/Heat.1995.sample.mkv",     # sample clip: should be ignored
    # Tricky ones: numbers in the title
    "Blade.Runner.2049.2017.2160p.UHD.mkv",
    "2001.A.Space.Odyssey.1968.REMASTERED.1080p.mkv",
    "1917.2019.1080p.mkv",
    # No year, odd case, spaces, underscores
    "amelie.mkv",
    "THE_GODFATHER_1972.AVI",
    "Pans Labyrinth 2006 DVDRip.avi",
    # Not films
    "notes.txt",
    "Inception.2010.nfo",
]


def main() -> None:
    for name in NAMES:
        path = TARGET / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    print(f"Created {len(NAMES)} files in {TARGET}")


if __name__ == "__main__":
    main()
