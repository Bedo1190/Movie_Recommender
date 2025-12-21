import numpy as np
import pickle
import operator
from collections import defaultdict
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.dirname(current_dir)

similarity_model_path = os.path.join(root_dir, "item_similarity_model.pkl")
movie_id_mapping_path = os.path.join(root_dir, "movie_id_mapping.pkl")

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
        print(f"Loading model assets from: {root_dir} ...")

        # 1. Similarity Matrix 
        try:
            with open(similarity_model_path, 'rb') as f:
                self.item_similarity_matrix = pickle.load(f)
                print(f"Similarity matrix loaded. Shape: {self.item_similarity_matrix.shape}")
        except FileNotFoundError:
            print(f"Error: Model file not found at {similarity_model_path}")
            return

        # 2. Movie ID List 
        try:
            with open(movie_id_mapping_path, 'rb') as f:
                self.movie_ids = pickle.load(f)
                print(f"Movie ID mapping loaded. Total movies: {len(self.movie_ids)}")
                
                self.movie_id_to_index = {movie_id: index for index, movie_id in enumerate(self.movie_ids)}
        except FileNotFoundError:
            print(f"Error: Mapping file not found at {movie_id_mapping_path}")

    def get_recommendations(self, liked_movie_ids, top_k=10):
        """
        Geriye [(movieId, score), (movieId, score)] formatında liste döner.
        """
        if self.item_similarity_matrix is None or self.movie_ids is None:
            print("Model assets not loaded properly.")
            return []
        
        recommendation_scores = defaultdict(float)

        for liked_id in liked_movie_ids:
            liked_index = self.movie_id_to_index.get(liked_id)

            if liked_index is None:
                # print(f"Movie ID {liked_id} not found in the mapping.")
                continue

            similar_items = self.item_similarity_matrix[liked_index]

            for idx, score in enumerate(similar_items):
                candidate_movie_id = self.movie_ids[idx]

                if candidate_movie_id not in liked_movie_ids:
                    recommendation_scores[candidate_movie_id] += score

        if not recommendation_scores:
            return []
            
        max_score = max(recommendation_scores.values()) if recommendation_scores else 1.0
        
        sorted_recommendations = sorted(
            recommendation_scores.items(), 
            key=operator.itemgetter(1), 
            reverse=True
        )


        final_recommendations = []
        for movie_id, raw_score in sorted_recommendations[:top_k]:
            normalized_score = raw_score / max_score if max_score > 0 else 0
            final_recommendations.append((movie_id, normalized_score))

        return final_recommendations