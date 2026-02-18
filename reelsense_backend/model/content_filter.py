"""
Content-Based Filtering using TF-IDF on movie genres and tags
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


class ContentBasedFilter:
    """Content-based filtering using movie metadata"""
    
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.movie_ids = None
        self.content_similarity = None
        
    def fit(self, movie_data: pd.DataFrame):
        """
        Train content-based filter
        
        Args:
            movie_data: DataFrame with columns [movieId, genres, tag, content_features]
        """
        self.movie_ids = movie_data['movieId'].tolist()
        
        # Create TF-IDF matrix from content features
        print("Computing TF-IDF features...")
        self.tfidf_matrix = self.tfidf.fit_transform(
            movie_data['content_features']
        )
        
        # Compute item-item similarity
        print("Computing content similarity matrix...")
        self.content_similarity = cosine_similarity(self.tfidf_matrix)
        
        print(f"Content model fitted on {len(self.movie_ids)} movies")
        
        return self
    
    def get_similar_movies(self, movie_id: int, top_k: int = 10) -> list:
        """
        Get most similar movies based on content
        
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        if movie_id not in self.movie_ids:
            return []
        
        movie_idx = self.movie_ids.index(movie_id)
        similarities = self.content_similarity[movie_idx]
        
        # Get top-k similar (excluding itself)
        similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
        
        return [
            (self.movie_ids[idx], similarities[idx]) 
            for idx in similar_indices
        ]
    
    def predict(self, user_id: int, movie_id: int, user_ratings: pd.DataFrame) -> float:
        """
        Predict content-based score for a user-movie pair
        
        Args:
            user_id: User ID
            movie_id: Movie ID to predict
            user_ratings: DataFrame with user's rating history
            
        Returns:
            Content-based score (0-1 scale, normalized)
        """
        if movie_id not in self.movie_ids:
            return 0.0
        
        # Get movies user has rated highly (4+ stars)
        user_liked = user_ratings[
            (user_ratings['userId'] == user_id) & 
            (user_ratings['rating'] >= 4.0)
        ]['movieId'].tolist()
        
        if not user_liked:
            return 0.0
        
        movie_idx = self.movie_ids.index(movie_id)
        
        # Average similarity to user's liked movies
        similarities = []
        for liked_movie in user_liked:
            if liked_movie in self.movie_ids:
                liked_idx = self.movie_ids.index(liked_movie)
                sim = self.content_similarity[movie_idx][liked_idx]
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    def predict_batch(self, user_id: int, movie_ids: list, user_ratings: pd.DataFrame) -> dict:
        """
        Predict content scores for multiple movies
        
        Returns:
            Dict mapping movie_id -> content score
        """
        scores = {}
        for movie_id in movie_ids:
            scores[movie_id] = self.predict(user_id, movie_id, user_ratings)
        return scores
    
    def save(self, path: str = "model/content_model.pkl"):
        """Save the trained model"""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"Content model saved to {path}")
    
    @staticmethod
    def load(path: str = "model/content_model.pkl"):
        """Load a trained model"""
        with open(path, "rb") as f:
            return pickle.load(f)
