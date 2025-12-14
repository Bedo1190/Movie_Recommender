from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path("data/processed")
ASSETS_DIR = DATA_DIR / "api_assets"

POPULAR_PATH = ASSETS_DIR / "popular_100.json"
GENRES_PATH = ASSETS_DIR / "genres.json"
SEARCH_PATH = ASSETS_DIR / "search_index.csv"

MASTER_CSV = DATA_DIR / "movies_master.csv"
BASE_CSV = DATA_DIR / "movies_base.csv"

app = FastAPI(title="Movie API (Session-based)")

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # set to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load once at startup ----
def load_movies_df() -> pd.DataFrame:
    if MASTER_CSV.exists():
        df = pd.read_csv(MASTER_CSV)
    elif BASE_CSV.exists():
        df = pd.read_csv(BASE_CSV)
    else:
        raise RuntimeError("No movies_master.csv or movies_base.csv found in data/processed")

    df["movieId"] = df["movieId"].astype(int)

    # Ensure optional fields exist
    for col in ["poster_url", "overview", "title_clean", "year", "genres", "rating_count", "rating_mean"]:
        if col not in df.columns:
            df[col] = ""

    # Index for fast lookup
    return df.set_index("movieId", drop=False)

MOVIES = load_movies_df()

with open(POPULAR_PATH, "r", encoding="utf-8") as f:
    POPULAR_100 = json.load(f)

with open(GENRES_PATH, "r", encoding="utf-8") as f:
    GENRES = json.load(f)

SEARCH = pd.read_csv(SEARCH_PATH)
# expected columns: movieId, title/title_clean, q
SEARCH["movieId"] = SEARCH["movieId"].astype(int)
SEARCH["q"] = SEARCH["q"].astype(str).str.lower()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/movies/popular")
def movies_popular():
    # returns the pre-exported popular list (fast)
    return POPULAR_100


@app.get("/genres")
def genres():
    return GENRES


@app.get("/movies/{movie_id}")
def movie_detail(movie_id: int):
    if movie_id not in MOVIES.index:
        raise HTTPException(status_code=404, detail="movieId not found")
    row = MOVIES.loc[movie_id]
    # Return a clean JSON dict
    return {
        "movieId": int(row["movieId"]),
        "title": row.get("title", ""),
        "year": None if pd.isna(row.get("year")) else int(row.get("year")),
        "genres": row.get("genres", ""),
        "poster_url": row.get("poster_url", ""),
        "overview": row.get("overview", ""),
        "rating_count": int(row.get("rating_count", 0)) if str(row.get("rating_count", "")).strip() != "" else 0,
        "rating_mean": float(row.get("rating_mean", 0)) if str(row.get("rating_mean", "")).strip() != "" else 0.0,
    }


@app.get("/movies/search")
def movie_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50)
):
    q_norm = q.strip().lower()

    # simple contains filter on precomputed 'q' column
    hits = SEARCH[SEARCH["q"].str.contains(q_norm, na=False)].head(limit)

    results = []
    for mid in hits["movieId"].tolist():
        if mid in MOVIES.index:
            row = MOVIES.loc[mid]
            results.append({
                "movieId": int(row["movieId"]),
                "title": row.get("title", ""),
                "year": None if pd.isna(row.get("year")) else int(row.get("year")),
                "genres": row.get("genres", ""),
                "poster_url": row.get("poster_url", ""),
            })

    return results
