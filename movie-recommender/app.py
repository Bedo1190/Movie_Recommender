import sys
import os
from pathlib import Path
import json
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

ai_rec_path = os.path.join(root_dir, 'ai_recommender')
if ai_rec_path not in sys.path:
    sys.path.append(ai_rec_path)

try:
    try:
        from ai_recommender.recommender import ItemBasedRecommender
    except ImportError:
        from recommender import ItemBasedRecommender
    print("Recommender sınıfı başarıyla import edildi.")
except ImportError as e:
    print(f"Recommender modülü bulunamadı! Hata: {e}")
    ItemBasedRecommender = None

# --- VERİ YÜKLEME ---
DATA_DIR = Path("data/processed")
ASSETS_DIR = DATA_DIR / "api_assets"

POPULAR_PATH = ASSETS_DIR / "popular_100.json"
GENRES_PATH = ASSETS_DIR / "genres.json"
SEARCH_PATH = ASSETS_DIR / "search_index.csv"
MASTER_CSV = DATA_DIR / "movies_master.csv"
BASE_CSV = DATA_DIR / "movies_base.csv"

app = FastAPI(title="Movie API (Session-based)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_movies_df() -> pd.DataFrame:
    if MASTER_CSV.exists():
        df = pd.read_csv(MASTER_CSV)
    elif BASE_CSV.exists():
        df = pd.read_csv(BASE_CSV)
    else:
        print("UYARI: CSV dosyası bulunamadı, boş DataFrame dönülüyor.")
        return pd.DataFrame(columns=["movieId", "title"])

    df["movieId"] = df["movieId"].astype(int)
    for col in ["poster_url", "overview", "title_clean", "year", "genres", "rating_mean"]:
        if col in df.columns:
            df[col] = df[col].fillna("")
            
    return df.set_index("movieId", drop=False)

MOVIES = load_movies_df()

try:
    with open(POPULAR_PATH, "r", encoding="utf-8") as f:
        POPULAR_100 = json.load(f)
except:
    POPULAR_100 = []

try:
    with open(GENRES_PATH, "r", encoding="utf-8") as f:
        GENRES_LIST = json.load(f)
except:
    GENRES_LIST = []

try:
    SEARCH = pd.read_csv(SEARCH_PATH)
    SEARCH["q"] = SEARCH["q"].astype(str).str.lower()
except:
    SEARCH = pd.DataFrame()

print("Model Başlatılıyor...")
if ItemBasedRecommender:
    try:
        rec_model = ItemBasedRecommender()
    except Exception as e:
        print(f"Model başlatma hatası: {e}")
        rec_model = None
else:
    rec_model = None


class RecommendationRequest(BaseModel):
    liked_movie_ids: List[int]
    top_k: int = 10

@app.get("/")
def home():
    return {"status": "running", "model": "active" if rec_model else "inactive"}

@app.get("/movies/popular")
def get_popular():
    return POPULAR_100

@app.get("/movies/genres")
def get_genres():
    return GENRES_LIST

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    if movie_id not in MOVIES.index:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MOVIES.loc[movie_id].to_dict()

@app.get("/movies/search")
def search_movies(q: str = Query(..., min_length=1), limit: int = 20):
    if SEARCH.empty: return []
    q_norm = q.strip().lower()
    hits = SEARCH[SEARCH["q"].str.contains(q_norm, na=False)].head(limit)
    
    results = []
    for mid in hits["movieId"].tolist():
        if mid in MOVIES.index:
            results.append(MOVIES.loc[mid].to_dict())
    return results

@app.post("/recommend")
def recommend(payload: RecommendationRequest):
    if not rec_model:
        raise HTTPException(status_code=503, detail="Model yüklenemedi.")

    recommendations = rec_model.get_recommendations(payload.liked_movie_ids, payload.top_k)
    
    results = []
    for mid, score in recommendations:
        if mid in MOVIES.index:
            movie_data = MOVIES.loc[mid].to_dict()
            
            response_item = {
                "movieId": int(movie_data["movieId"]),
                "title": str(movie_data.get("title", "")),
                "poster_url": str(movie_data.get("poster_url", "")),
                "year": int(movie_data["year"]) if movie_data.get("year") else None,
                "rating_mean": float(movie_data.get("rating_mean", 0)),
                "genres": str(movie_data.get("genres", "")),
                
                "match_score": int(score * 100)
            }
            results.append(response_item)
            
    return results