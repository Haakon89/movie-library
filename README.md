# movie-library
A way to display your local movie files in an organized and visual way.

Python (FastAPI) backend + SQLite, React frontend (stage 2), metadata from TMDB (stage 3).

## Project layout

```
movie-library/
├── backend/
│   ├── app/
│   │   ├── config.py      # settings from backend/.env
│   │   ├── database.py    # SQLite connection + table layout
│   │   ├── scanner.py     # finds film files, reads title/year from names
│   │   └── main.py        # the web API (FastAPI)
│   ├── scripts/
│   │   └── make_sample_films.py   # creates test files with messy names
│   ├── tests/
│   │   └── test_scanner.py
│   ├── requirements.txt
│   └── .env.example       # copy to .env and fill in
└── frontend/              # React app (stage 2)
```

## Setup (Windows, PowerShell)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python scripts/make_sample_films.py
```

If PowerShell refuses to run `Activate.ps1`, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Everyday commands (from `backend/`, with the venv active)

| What | Command |
|---|---|
| Run the tests | `pytest -v` |
| Try the scanner on your folder | `python -m app.scanner` |
| Start the API | `uvicorn app.main:app --reload` |
| Try the API in your browser | http://127.0.0.1:8000/docs |

## Roadmap

1. **Scanner + backend skeleton** ← we are here
2. React frontend: poster grid and search
3. TMDB matching: posters, descriptions, trailers
4. Detail page and play button
5. Editing tool and "needs review" match picker
6. Netflix-style polish
