import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

from data_loader import load_data, create_user_item_matrix

similarity_model_path = "item_similarity_model.pkl"
movie_id_mapping_path = "movie_id_mapping.pkl"
rating_file_path = "ratings_clean.csv" 

def compute_item_similarity(item_user_sparse_matrix):
    """
    Compute the item-item cosine similarity matrix.
    The input matrix must have items as rows: shape (num_movies, num_users).
    """
    print("Computing item-item cosine similarity matrix...")

    # Since the input matrix has items as rows, cosine_similarity computes similarity between items
    item_similarity_matrix = cosine_similarity(item_user_sparse_matrix)

    print("Item-item similarity matrix computed successfully.")
    print(f"Item similarity matrix shape: {item_similarity_matrix.shape}")
    return item_similarity_matrix

def save_model_assets(item_similarity_matrix, movie_ids):
    """
    Save the computed similarity matrix and the corresponding movie IDs list.
    """

    try:
        # 1. Save the Similarity Matrix (The Model)
        with open(similarity_model_path, 'wb') as f:
            pickle.dump(item_similarity_matrix, f)
            print(f"Item similarity model saved to {similarity_model_path}")

        # 2. Save the Movie ID Mapping List
        with open(movie_id_mapping_path, 'wb') as f:
            pickle.dump(movie_ids, f)
            print(f"Movie ID list saved to {movie_id_mapping_path}")
    except Exception as e:
        print(f"Error saving model assets: {e}")

def build_and_save_model():
    """
    Build the item-based collaborative filtering model and save the assets.
    """
    # Load data
    ratings_df = load_data(rating_file_path)
    if ratings_df is None:
        print("Failed to load ratings data. Exiting.")
        return

    # Create item-user interaction matrix (Items are rows)
    item_user_matrix, movie_ids = create_user_item_matrix(ratings_df)
    if item_user_matrix is None:
        print("Failed to create item-user matrix. Exiting.")
        return

    # Compute item similarity matrix
    item_similarity_matrix = compute_item_similarity(item_user_matrix)

    # Save model assets
    save_model_assets(item_similarity_matrix, movie_ids)