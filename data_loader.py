import pandas as pd
from scipy.sparse import csr_matrix
import os

def load_data(file_path):
    """"
    Load the MovieLens ratings data from a CSV file.
    """
    try:
        # Load the ratings data from the provided path
        # Read the CSV file into a pandas DataFrame
        ratings_df = pd.read_csv(file_path, usecols=['userId', 'movieId', 'rating'])
        print(f"Data loaded successfully from {os.path.abspath(file_path)}. Total ratings: {len(ratings_df)}")
        return ratings_df
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    
def create_user_item_matrix(ratings_df):
    """
    Create an Item-User interaction matrix (Items as rows) from the ratings DataFrame.
    
    Returns:
        item_user_sparse_matrix (csr_matrix): Sparse matrix with shape (num_movies, num_users).
        movie_ids (list): List of Movie IDs corresponding to the matrix rows.
    """
    if ratings_df is None:
        print("Error: ratings_df is None. Cannot create user-item matrix.")
        return None

    # Create a pivot table: Rows=Users, Columns=Items
    user_item_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    print(f"User-item interaction matrix created with shape: {user_item_matrix.shape}")
    
    # Transpose to get Item-User matrix: Rows=Items, Columns=Users
    item_user_matrix = user_item_matrix.T
    
    # Get the list of movie IDs corresponding to the rows of the Item-User matrix
    movie_ids = item_user_matrix.index.tolist()

    # Convert the Item-User DataFrame to a sparse matrix for efficiency
    item_user_sparse_matrix = csr_matrix(item_user_matrix.values)
    
    print(f"Item-User interaction matrix created with shape: {item_user_sparse_matrix.shape}")
    print(f"Number of movies: {item_user_sparse_matrix.shape[0]}, Number of users: {item_user_sparse_matrix.shape[1]}")
    print("Item-User interaction matrix created successfully.")
    
    # Return the matrix where items are rows, and the list of movie IDs
    return item_user_sparse_matrix, movie_ids