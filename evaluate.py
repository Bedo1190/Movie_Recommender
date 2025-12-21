import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
import os

DATA_PATH = "movie-recommender/data/processed/ratings_clean.csv" 
TOP_K = 10

def dcg_at_k(r, k):
    """Discounted Cumulative Gain """
    r = np.asarray(r, dtype=float)[:k]
    if r.size:
        return np.sum(r / np.log2(np.arange(2, r.size + 2)))
    return 0.

def ndcg_at_k(r, k):
    """Normalized DCG """
    dcg_max = dcg_at_k(sorted(r, reverse=True), k)
    if not dcg_max:
        return 0.
    return dcg_at_k(r, k) / dcg_max

def evaluate():
    print(f"Veri yükleniyor: {DATA_PATH}...")
    
    if not os.path.exists(DATA_PATH):
        alt_path = "movie-recommender/data/processed/ratings_clean.csv"
        if os.path.exists(alt_path):
            print(f"Couldn't find main path trying: {alt_path}")
            path_to_use = alt_path
        else:
            print(f"Error; Couldn't find file ({DATA_PATH})")
            return
    else:
        path_to_use = DATA_PATH

    ratings = pd.read_csv(path_to_use)
    
    user_counts = ratings['userId'].value_counts()
    active_users = user_counts[user_counts >= 10].index
    ratings = ratings[ratings['userId'].isin(active_users)]

    print("Splitting data to Train (%80) and Test (%20)")
    train_data, test_data = train_test_split(ratings, test_size=0.2, stratify=ratings['userId'], random_state=42)

    test_ground_truth = test_data[test_data['rating'] >= 4.0].groupby('userId')['movieId'].apply(set).to_dict()
    test_users = list(test_ground_truth.keys())

    print("Training model...")
    user_item_matrix = train_data.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    item_user_matrix = user_item_matrix.T
    sparse_matrix = csr_matrix(item_user_matrix.values)
    
    item_similarity = cosine_similarity(sparse_matrix)
    item_similarity_df = pd.DataFrame(item_similarity, index=item_user_matrix.index, columns=item_user_matrix.index)
    
    print(f" Testing on {len(test_users)} users")
    
    precision_scores = []
    ndcg_scores = []
    recall_scores = []   
    hit_scores = []
    
    valid_items = set(item_similarity_df.index)

    for user in test_users:
        if user not in user_item_matrix.index: continue
        
        user_history = train_data[train_data['userId'] == user]
        liked_history = user_history[user_history['rating'] >= 3.0]['movieId'].tolist()
        
        true_test_items = test_ground_truth[user]
        
        if not liked_history or not true_test_items: continue

        valid_history = [m for m in liked_history if m in valid_items]
        if not valid_history: continue
            
        sim_scores = item_similarity_df.loc[valid_history].sum(axis=0)
        sim_scores = sim_scores.drop(valid_history, errors='ignore')
        
        recommendations = sim_scores.sort_values(ascending=False).head(TOP_K).index.tolist()
        
        hits = [1 if item in true_test_items else 0 for item in recommendations]
        
        hit_count = sum(hits)
        
        precision_scores.append(hit_count / TOP_K)
        
        recall_scores.append(hit_count / len(true_test_items))  
        
        ndcg_scores.append(ndcg_at_k(hits, TOP_K))
        hit_scores.append(1 if hit_count > 0 else 0)

    print("\n" + "="*40)
    print(f"📢 Results for (Top-{TOP_K} recommendations)")
    print("="*40)
    print(f"Average Precision : {np.mean(precision_scores):.4f}")
    print(f"Average Recall    : {np.mean(recall_scores):.4f}") 
    print(f"Average NDCG      : {np.mean(ndcg_scores):.4f}")
    print(f"Hit Rate          : {np.mean(hit_scores):.4f}")
    print("="*40)
if __name__ == "__main__":
    evaluate()