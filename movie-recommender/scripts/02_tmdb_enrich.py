import os, json, time
import pandas as pd
import requests
from tqdm import tqdm

BASE = "data/processed/movies_base.csv"
CACHE_DIR = "data/cache/tmdb"
OUT = "data/processed/movies_master.csv"

os.makedirs(CACHE_DIR, exist_ok=True)


TMDB_TOKEN = os.getenv("TMDB_TOKEN")
if not TMDB_TOKEN:
    raise RuntimeError("Missing TMDB_TOKEN env var")

HEADERS = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}

# Get configuration to build poster URL (recommended)
conf = requests.get("https://api.themoviedb.org/3/configuration", headers=HEADERS).json()
base_url = conf["images"]["secure_base_url"]
poster_size = "w500"  # choose a size from config

def cached_get_movie(tmdb_id: int):
    cache_path = f"{CACHE_DIR}/{tmdb_id}.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None

    data = r.json()
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    time.sleep(0.05)  # be polite
    return data

df = pd.read_csv(BASE)

# Keep only rows with tmdbId
df = df[df["tmdbId"].notna()].copy()
df["tmdbId"] = df["tmdbId"].astype(int)

# Fetch only top N popular to start (change N as you like)
N = 500
df = df.sort_values("rating_count", ascending=False).head(N).copy()

overviews, posters, tmdb_genres = [], [], []

for tmdb_id in tqdm(df["tmdbId"].tolist()):
    data = cached_get_movie(tmdb_id)
    if not data:
        overviews.append("")
        posters.append("")
        tmdb_genres.append("")
        continue

    overviews.append(data.get("overview","") or "")
    poster_path = data.get("poster_path")
    posters.append(f"{base_url}{poster_size}{poster_path}" if poster_path else "")
    # genres is list of dicts: [{"id":..,"name":..}, ...]
    g = data.get("genres", [])
    tmdb_genres.append("|".join([x["name"] for x in g if "name" in x]))

df["overview"] = overviews
df["poster_url"] = posters
df["tmdb_genres"] = tmdb_genres

df.to_csv(OUT, index=False)
print("Saved:", OUT)
