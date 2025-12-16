# Movie Recommender – Frontend

This is a simple session-based React UI for your FastAPI backend.

## Run (dev)

1) Start the backend (from `movie-recommender/`):

```bash
python -m pip install -r requirements.txt  # if you have one
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2) Start the frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Optional: create a `.env` file to point to a different backend:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## What it uses

- `GET /movies/popular`
- `GET /search?q=...`
- `POST /recommend` with `{ liked_movie_ids: number[], top_k: number }`
- `GET /movies/{movieId}` (details modal + liked page)
