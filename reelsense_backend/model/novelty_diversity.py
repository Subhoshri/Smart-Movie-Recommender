"""
Novelty and Diversity components for promoting long-tail discovery
"""
import pandas as pd
import numpy as np
from collections import Counter
import pickle


class NoveltyBooster:
    """Promotes lesser-known movies to increase discovery"""
    
    def __init__(self, alpha: float = 0.3):
        """
        Args:
            alpha: Novelty weight (higher = more emphasis on unpopular items)
        """
        self.alpha = alpha
        self.movie_popularity = None
        self.max_popularity = None
        
    def fit(self, ratings_df: pd.DataFrame):
        """
        Calculate movie popularity scores
        
        Args:
            ratings_df: DataFrame with columns [userId, movieId, rating]
        """
        # Count ratings per movie
        popularity = ratings_df['movieId'].value_counts().to_dict()
        
        self.movie_popularity = popularity
        self.max_popularity = max(popularity.values())
        
        print(f"Novelty booster fitted on {len(popularity)} movies")
        print(f"Most popular movie has {self.max_popularity} ratings")
        
        return self
    
    def get_novelty_score(self, movie_id: int) -> float:
        """
        Calculate novelty score for a movie (inverse popularity)
        
        Returns:
            Novelty score (0-1, higher = more novel/less popular)
        """
        if movie_id not in self.movie_popularity:
            return 1.0  # Unknown movies get max novelty
        
        popularity = self.movie_popularity[movie_id]
        
        # Inverse popularity, normalized
        novelty = 1.0 - (popularity / self.max_popularity)
        
        return novelty ** self.alpha  # Apply alpha weighting
    
    def get_novelty_scores(self, movie_ids: list) -> dict:
        """
        Get novelty scores for multiple movies
        
        Returns:
            Dict mapping movie_id -> novelty score
        """
        return {
            movie_id: self.get_novelty_score(movie_id) 
            for movie_id in movie_ids
        }
    
    def save(self, path: str = "model/novelty_booster.pkl"):
        """Save the model"""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"Novelty booster saved to {path}")
    
    @staticmethod
    def load(path: str = "model/novelty_booster.pkl"):
        """Load the model"""
        with open(path, "rb") as f:
            return pickle.load(f)


class DiversityOptimizer:
    """Ensures recommended list has diverse genres/content"""
    
    def __init__(self, movie_data: pd.DataFrame):
        """
        Args:
            movie_data: DataFrame with [movieId, genres] columns
        """
        self.movie_genres = {}
        
        for _, row in movie_data.iterrows():
            genres = row['genres'].split('|') if '|' in row['genres'] else [row['genres']]
            self.movie_genres[row['movieId']] = set(genres)
    
    def calculate_diversity(self, movie_list: list) -> float:
        """
        Calculate intra-list diversity (how different movies are from each other)
        
        Args:
            movie_list: List of movie IDs
            
        Returns:
            Diversity score (0-1, higher = more diverse)
        """
        if len(movie_list) < 2:
            return 0.0
        
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(movie_list)):
            for j in range(i + 1, len(movie_list)):
                movie1 = movie_list[i]
                movie2 = movie_list[j]
                
                if movie1 in self.movie_genres and movie2 in self.movie_genres:
                    genres1 = self.movie_genres[movie1]
                    genres2 = self.movie_genres[movie2]
                    
                    # Jaccard similarity
                    intersection = len(genres1 & genres2)
                    union = len(genres1 | genres2)
                    
                    similarity = intersection / union if union > 0 else 0
                    total_similarity += similarity
                    comparisons += 1
        
        if comparisons == 0:
            return 0.0
        
        avg_similarity = total_similarity / comparisons
        diversity = 1.0 - avg_similarity
        
        return diversity
    
    def rerank_by_diversity(self, scored_movies: list, top_k: int = 10) -> list:
        """
        Re-rank recommendations to maximize diversity
        
        Args:
            scored_movies: List of (movie_id, score) tuples
            top_k: Number of final recommendations
            
        Returns:
            Re-ranked list of (movie_id, score) tuples
        """
        if len(scored_movies) <= top_k:
            return scored_movies
        
        # Start with highest-scored movie
        selected = [scored_movies[0]]
        remaining = scored_movies[1:]
        
        while len(selected) < top_k and remaining:
            best_candidate = None
            best_diversity = -1
            
            for candidate in remaining:
                # Calculate diversity if we add this candidate
                test_list = [m[0] for m in selected] + [candidate[0]]
                diversity = self.calculate_diversity(test_list)
                
                # Balance diversity with original score
                combined_score = 0.7 * candidate[1] + 0.3 * diversity
                
                if combined_score > best_diversity:
                    best_diversity = combined_score
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
        
        return selected
