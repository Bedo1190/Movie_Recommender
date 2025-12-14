import pandas as pd
import numpy as np
import re

RAW = "data/raw/ml-latest-small"
OUT = "data/processed"

movies  = pd.read_csv(f"{RAW}/movies.csv")      # movieId,title,genres
ratings = pd.read_csv(f"{RAW}/ratings.csv")     # userId,movieId,rating,timestamp
links   = pd.read_csv(f"{RAW}/links.csv")       # movieId,imdbId,tmdbId

# ---- Clean movies ----
def extract_year(title):
    m = re.search(r"\((\d{4})\)\s*$", str(title))
    return int(m.group(1)) if m else np.nan

movies["year"] = movies["title"].apply(extract_year)
movies["title_clean"] = movies["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)

# ---- Clean ratings ----
ratings = ratings.dropna(subset=["userId","movieId","rating"])
ratings["userId"] = ratings["userId"].astype(int)
ratings["movieId"] = ratings["movieId"].astype(int)
ratings["rating"] = ratings["rating"].astype(float)

# Optional: remove impossible ratings (MovieLens is typically 0.5–5.0)
ratings = ratings[(ratings["rating"] >= 0.5) & (ratings["rating"] <= 5.0)]

# ---- Popularity stats for UI ----
stats = (ratings.groupby("movieId")
         .agg(rating_count=("rating","size"),
              rating_mean=("rating","mean"))
         .reset_index())

# ---- Merge movies + stats + links ----
base = (movies.merge(stats, on="movieId", how="left")
              .merge(links, on="movieId", how="left"))

base["rating_count"] = base["rating_count"].fillna(0).astype(int)
base["rating_mean"]  = base["rating_mean"].fillna(0).round(3)

# Save outputs
base.to_csv(f"{OUT}/movies_base.csv", index=False)
ratings.to_csv(f"{OUT}/ratings_clean.csv", index=False)

print("Saved:", f"{OUT}/movies_base.csv", "and", f"{OUT}/ratings_clean.csv")
