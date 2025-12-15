import numpy as np
import pickle
import operator
from collections import defaultdict

similarity_model_path = "item_similarity_model.pkl"
movie_id_mapping_path = "movie_id_mapping.pkl"

class ItemBasedRecommender:
    def __init__(self):
        self.item_similarity_matrix = None
        self.movie_ids = None
        self.movie_id_to_index = None
        self._load_model_assets()

    def _load_model_assets(self):
        """
        Load the precomputed item similarity matrix and movie ID mapping list.
        """
        print("Loading model assets...")

        #1 Load the Similarity Matrix
        try:
            with open(similarity_model_path, 'rb') as f:
                self.item_similarity_matrix = pickle.load(f)
                print(f"Similarity matrix loaded. Shape: {self.item_similarity_matrix.shape}")
        except FileNotFoundError:
            print(f"Error: Model file not found at {similarity_model_path}")
            return

        #2 Load the Movie ID List
        try:
            with open(movie_id_mapping_path, 'rb') as f:
                self.movie_ids = pickle.load(f)
                print(f"Movie ID mapping loaded. Total movies: {len(self.movie_ids)}")
                
                self.movie_id_to_index = {movie_id: index for index, movie_id in enumerate(self.movie_ids)}
        except FileNotFoundError:
            print(f"Error: ID mapping file not found at {movie_id_mapping_path}")
            return
        

    def get_recommendations(self, liked_movie_ids: list, top_k: int = 10) -> list:
        """
        Generate top-K movie recommendations based on a list of liked movies.

        Parameters:
                liked_movie_ids (list): A list of MovieLens IDs liked by the current session user.
                top_k (int): The number of top recommendations to return.

        Returns:
                list: List of recommended movie IDs.
        """
        if self.item_similarity_matrix is None or self.movie_ids is None:
            print("Model assets not loaded properly.")
            return []
        
        #1. Compute the Total Score for each candidate movie
        recommendation_scores = defaultdict(float)

        for liked_id in liked_movie_ids:
            liked_index = self.movie_id_to_index.get(liked_id)

            if liked_index is None:
                print(f"Movie ID {liked_id} not found in the mapping.")
                continue

            similar_items = self.item_similarity_matrix[liked_index]

            for idx, score in enumerate(similar_items):
                candidate_movie_id = self.movie_ids[idx]

                if candidate_movie_id not in liked_movie_ids:
                    recommendation_scores[candidate_movie_id] += score

        #2. Sort the candidate movies based on their scores
        sorted_recommendations = sorted(
            recommendation_scores.items(), 
            key=operator.itemgetter(1), 
            reverse=True
        )

        #3. Return the top-K recommended movie IDs
        recommended_movie_ids = [movie_id for movie_id, score in sorted_recommendations[:top_k]]

        return recommended_movie_ids
        

