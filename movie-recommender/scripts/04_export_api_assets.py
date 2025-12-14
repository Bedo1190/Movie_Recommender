import pandas as pd
import json
import os

IN_MASTER = "data/processed/movies_master.csv"   # if you have TMDB posters
IN_BASE   = "data/processed/movies_base.csv"     # fallback if master doesn't exist
OUT_DIR   = "data/processed/api_assets"

os.makedirs(OUT_DIR, exist_ok=True)

# Load master if available, else base
try:
    df = pd.read_csv(IN_MASTER)
    source = "movies_master.csv"
except FileNotFoundError:
    df = pd.read_csv(IN_BASE)
    source = "movies_base.csv"

# ---- Minimal fields for API/UI ----
# keep only what backend/frontend needs
keep_cols = [c for c in [
    "movieId", "title", "title_clean", "year", "genres",
    "rating_count", "rating_mean", "tmdbId", "poster_url", "overview"
] if c in df.columns]

df = df[keep_cols].copy()
df["movieId"] = df["movieId"].astype(int)

# Fill missing optional cols
for col in ["poster_url", "overview", "title_clean", "genres"]:
    if col in df.columns:
        df[col] = df[col].fillna("")

# ---- 1) Popular movies (top 100) ----
# Sort by rating_count then rating_mean
if "rating_count" in df.columns:
    popular = df.sort_values(["rating_count", "rating_mean"], ascending=[False, False]).head(100)
else:
    popular = df.head(100)

popular_path = f"{OUT_DIR}/popular_100.json"
popular[["movieId","title","year","genres"] + ([ "poster_url" ] if "poster_url" in popular.columns else [])] \
    .to_json(popular_path, orient="records", force_ascii=False)

# ---- 2) Genres list ----
genres = set()
if "genres" in df.columns:
    for g in df["genres"].astype(str).tolist():
        for part in g.split("|"):
            part = part.strip()
            if part and part != "(no genres listed)":
                genres.add(part)

genres_path = f"{OUT_DIR}/genres.json"
with open(genres_path, "w", encoding="utf-8") as f:
    json.dump(sorted(genres), f, ensure_ascii=False, indent=2)

# ---- 3) Search index (small CSV) ----
# Backend can do simple "contains" filtering on title_clean
search_cols = ["movieId"]
if "title_clean" in df.columns:
    search_cols.append("title_clean")
else:
    search_cols.append("title")
if "title" in df.columns and "title" not in search_cols:
    search_cols.append("title")

search_df = df[search_cols].copy()
search_df["q"] = search_df[search_cols[1]].astype(str).str.lower()

search_path = f"{OUT_DIR}/search_index.csv"
search_df.to_csv(search_path, index=False)

print("Export source:", source)
print("Saved:", popular_path)
print("Saved:", genres_path)
print("Saved:", search_path)
