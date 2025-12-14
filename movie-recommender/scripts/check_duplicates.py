import pandas as pd

m = pd.read_csv("data/processed/movies_base.csv")
print("Duplicate movieId rows:", m["movieId"].duplicated().sum())
