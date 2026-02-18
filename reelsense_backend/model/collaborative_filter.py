"""
Collaborative Filtering component using user-based cosine similarity
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pickle


class CollaborativeFilter:
    """User-based collaborative filtering"""
    
    def __init__(self, k_neighbors: int = 30):
        self.k_neighbors = k_neighbors
        self.user_similarity = None
        self.user_item_matrix = None
        self.user_ids = None
        self.movie_ids = None
        
    def fit(self, ratings_df: pd.DataFrame):
        """
        Train the collaborative filter
        
        Args:
            ratings_df: DataFrame with columns [userId, movieId, rating]
        """
        # Create user-item matrix
        self.user_item_matrix = ratings_df.pivot_table(
            index='userId',
            columns='movieId', 
            values='rating'
        ).fillna(0)
        
        self.user_ids = self.user_item_matrix.index.tolist()
        self.movie_ids = self.user_item_matrix.columns.tolist()
        
        # Calculate user-user similarity
        print("Computing user similarity matrix...")
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        
        print(f"CF model fitted on {len(self.user_ids)} users, {len(self.movie_ids)} movies")
        
        return self
    
    def predict(self, user_id: int, movie_id: int) -> float:
        """
        Predict rating for a user-movie pair
        
        Returns:
            Predicted CF score (0-5 scale)
        """
        if user_id not in self.user_ids or movie_id not in self.movie_ids:
            return 0.0
        
        user_idx = self.user_ids.index(user_id)
        movie_idx = self.movie_ids.index(movie_id)
        
        # Get top-k similar users
        similar_users = np.argsort(self.user_similarity[user_idx])[::-1][1:self.k_neighbors+1]
        
        # Weighted average of similar users' ratings
        numerator = 0
        denominator = 0
        
        for sim_user_idx in similar_users:
            sim_score = self.user_similarity[user_idx][sim_user_idx]
            rating = self.user_item_matrix.iloc[sim_user_idx, movie_idx]
            
            if rating > 0:  # Only consider users who rated this movie
                numerator += sim_score * rating
                denominator += sim_score
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def predict_batch(self, user_id: int, movie_ids: list) -> dict:
        """
        Predict scores for multiple movies for a user
        
        Returns:
            Dict mapping movie_id -> CF score
        """
        scores = {}
        for movie_id in movie_ids:
            scores[movie_id] = self.predict(user_id, movie_id)
        return scores
    
    def get_user_rated_movies(self, user_id: int) -> list:
        """Get list of movies already rated by user"""
        if user_id not in self.user_ids:
            return []
        
        user_idx = self.user_ids.index(user_id)
        rated_movies = self.user_item_matrix.iloc[user_idx]
        return rated_movies[rated_movies > 0].index.tolist()
    
    def save(self, path: str = "model/cf_model.pkl"):
        """Save the trained model"""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"CF model saved to {path}")
    
    @staticmethod
    def load(path: str = "model/cf_model.pkl"):
        """Load a trained model"""
        with open(path, "rb") as f:
            return pickle.load(f)
