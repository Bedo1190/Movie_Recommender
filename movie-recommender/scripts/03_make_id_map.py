import pandas as pd

ratings = pd.read_csv("data/processed/ratings_clean.csv")
movie_ids = sorted(ratings["movieId"].unique())

id_map = pd.DataFrame({"movieId": movie_ids, "item_index": range(len(movie_ids))})
id_map.to_csv("data/processed/movieId_to_index.csv", index=False)

print("Saved data/processed/movieId_to_index.csv")
