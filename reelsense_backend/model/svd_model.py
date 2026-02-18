"""
Matrix Factorization using SVD (Singular Value Decomposition)
"""
import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import pickle


class SVDModel:
    """SVD-based matrix factorization"""
    
    def __init__(self, n_factors: int = 100, n_epochs: int = 20, lr_all: float = 0.005, reg_all: float = 0.02):
        self.model = SVD(
            n_factors=n_factors,
            n_epochs=n_epochs,
            lr_all=lr_all,
            reg_all=reg_all,
            random_state=42
        )
        self.reader = Reader(rating_scale=(0.5, 5.0))
        self.is_fitted = False
        
    def fit(self, ratings_df: pd.DataFrame):
        """
        Train SVD model
        
        Args:
            ratings_df: DataFrame with columns [userId, movieId, rating]
        """
        # Convert to Surprise format
        data = Dataset.load_from_df(
            ratings_df[['userId', 'movieId', 'rating']], 
            self.reader
        )
        
        # Train on full dataset
        trainset = data.build_full_trainset()
        
        print("Training SVD model...")
        self.model.fit(trainset)
        self.is_fitted = True
        
        print(f"SVD model fitted on {trainset.n_users} users, {trainset.n_items} items")
        
        return self
    
    def predict(self, user_id: int, movie_id: int) -> float:
        """
        Predict rating for a user-movie pair
        
        Returns:
            Predicted rating (0.5-5.0 scale)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        prediction = self.model.predict(user_id, movie_id)
        return prediction.est
    
    def predict_batch(self, user_id: int, movie_ids: list) -> dict:
        """
        Predict ratings for multiple movies
        
        Returns:
            Dict mapping movie_id -> predicted rating
        """
        scores = {}
        for movie_id in movie_ids:
            scores[movie_id] = self.predict(user_id, movie_id)
        return scores
    
    def get_top_n_recommendations(self, user_id: int, n: int = 10, 
                                   candidate_movies: list = None) -> list:
        """
        Get top-N recommendations for a user
        
        Args:
            user_id: User ID
            n: Number of recommendations
            candidate_movies: List of movie IDs to consider (if None, consider all)
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if candidate_movies is None:
            # Get all movies (expensive, should be cached)
            candidate_movies = list(range(1, 10000))  # Placeholder
        
        predictions = []
        for movie_id in candidate_movies:
            pred_rating = self.predict(user_id, movie_id)
            predictions.append((movie_id, pred_rating))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n]
    
    def save(self, path: str = "model/svd_model.pkl"):
        """Save the trained model"""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"SVD model saved to {path}")
    
    @staticmethod
    def load(path: str = "model/svd_model.pkl"):
        """Load a trained model"""
        with open(path, "rb") as f:
            return pickle.load(f)


class SVDEvaluator:
    """Evaluation metrics for SVD model"""
    
    @staticmethod
    def evaluate(model: SVDModel, test_df: pd.DataFrame) -> dict:
        """
        Evaluate model on test set
        
        Returns:
            Dict with RMSE, MAE metrics
        """
        predictions = []
        actuals = []
        
        for _, row in test_df.iterrows():
            pred = model.predict(row['userId'], row['movieId'])
            predictions.append(pred)
            actuals.append(row['rating'])
        
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mae = np.mean(np.abs(predictions - actuals))
        
        return {
            'rmse': rmse,
            'mae': mae
        }
