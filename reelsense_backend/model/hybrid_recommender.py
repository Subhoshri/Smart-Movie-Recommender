"""
Hybrid Recommender System combining CF, Content, SVD, and Novelty
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import pickle

from model.collaborative_filter import CollaborativeFilter
from model.content_filter import ContentBasedFilter
from model.svd_model import SVDModel
from model.novelty_diversity import NoveltyBooster, DiversityOptimizer


class HybridRecommender:
    """
    Hybrid recommendation system with explainability
    
    Final score = ɑ·CF + β·Content + γ·SVD + δ·Novelty
    """
    
    def __init__(
        self,
        alpha: float = 0.25,  # CF weight
        beta: float = 0.25,   # Content weight
        gamma: float = 0.35,  # SVD weight
        delta: float = 0.15   # Novelty weight
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        
        # Component models
        self.cf_model = None
        self.content_model = None
        self.svd_model = None
        self.novelty_booster = None
        self.diversity_optimizer = None
        
        # Data references
        self.ratings_df = None
        self.movies_df = None
        
    def fit(
        self,
        cf_model: CollaborativeFilter,
        content_model: ContentBasedFilter,
        svd_model: SVDModel,
        novelty_booster: NoveltyBooster,
        diversity_optimizer: DiversityOptimizer,
        ratings_df: pd.DataFrame,
        movies_df: pd.DataFrame
    ):
        """Load all pre-trained component models"""
        self.cf_model = cf_model
        self.content_model = content_model
        self.svd_model = svd_model
        self.novelty_booster = novelty_booster
        self.diversity_optimizer = diversity_optimizer
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        
        print("Hybrid recommender initialized with all components")
        return self
    
    def predict(self, user_id: int, movie_id: int, explain: bool = False) -> dict:
        """
        Predict hybrid score for a user-movie pair
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            explain: If True, return score breakdown
            
        Returns:
            Dict with 'score' and optional 'explanation'
        """
        # Get component scores
        cf_score = self.cf_model.predict(user_id, movie_id)
        content_score = self.content_model.predict(user_id, movie_id, self.ratings_df)
        svd_score = self.svd_model.predict(user_id, movie_id)
        novelty_score = self.novelty_booster.get_novelty_score(movie_id)
        
        # Normalize scores to 0-1 range
        cf_norm = cf_score / 5.0 if cf_score > 0 else 0.0
        content_norm = content_score  # Already 0-1
        svd_norm = svd_score / 5.0
        novelty_norm = novelty_score  # Already 0-1
        
        # Weighted combination
        hybrid_score = (
            self.alpha * cf_norm +
            self.beta * content_norm +
            self.gamma * svd_norm +
            self.delta * novelty_norm
        )
        
        result = {'score': hybrid_score}
        
        if explain:
            result['explanation'] = {
                'cf_score': cf_norm,
                'cf_weight': self.alpha,
                'content_score': content_norm,
                'content_weight': self.beta,
                'svd_score': svd_norm,
                'svd_weight': self.gamma,
                'novelty_score': novelty_norm,
                'novelty_weight': self.delta,
                'final_score': hybrid_score
            }
        
        return result
    
    def recommend(
        self,
        user_id: int,
        n: int = 10,
        exclude_rated: bool = True,
        diversify: bool = True,
        explain: bool = False
    ) -> List[Dict]:
        """
        Generate top-N recommendations for a user
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude_rated: Whether to exclude already-rated movies
            diversify: Whether to apply diversity optimization
            explain: Whether to include explanation for each recommendation
            
        Returns:
            List of recommendation dicts with movie info and scores
        """
        # Get candidate movies
        all_movies = self.movies_df['movieId'].tolist()
        
        if exclude_rated:
            rated_movies = self.cf_model.get_user_rated_movies(user_id)
            candidate_movies = [m for m in all_movies if m not in rated_movies]
        else:
            candidate_movies = all_movies
        
        # Score all candidates
        scored_movies = []
        for movie_id in candidate_movies:
            pred = self.predict(user_id, movie_id, explain=explain)
            scored_movies.append((movie_id, pred['score'], pred.get('explanation')))
        
        # Sort by score
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        
        # Apply diversity optimization if requested
        if diversify:
            scored_pairs = [(m[0], m[1]) for m in scored_movies[:n*2]]  # Consider 2x candidates
            diverse_pairs = self.diversity_optimizer.rerank_by_diversity(scored_pairs, n)
            
            # Reconstruct with explanations
            diverse_movie_ids = [m[0] for m in diverse_pairs]
            scored_movies = [m for m in scored_movies if m[0] in diverse_movie_ids]
        
        # Take top-N
        top_movies = scored_movies[:n]
        
        # Format results
        recommendations = []
        for movie_id, score, explanation in top_movies:
            movie_info = self.movies_df[self.movies_df['movieId'] == movie_id].iloc[0]
            
            rec = {
                'movie_id': movie_id,
                'title': movie_info['title'],
                'genres': movie_info['genres'],
                'score': round(score, 4)
            }
            
            if explain:
                rec['explanation'] = explanation
            
            recommendations.append(rec)
        
        return recommendations
    
    def get_explanation(self, user_id: int, movie_id: int) -> dict:
        """
        Get detailed explanation for why a movie was recommended
        
        Returns:
            Dict with human-readable explanation
        """
        pred = self.predict(user_id, movie_id, explain=True)
        exp = pred['explanation']
        
        # Find dominant factor
        components = [
            ('collaborative filtering', exp['cf_score'] * exp['cf_weight']),
            ('content similarity', exp['content_score'] * exp['content_weight']),
            ('rating prediction', exp['svd_score'] * exp['svd_weight']),
            ('novelty/discovery', exp['novelty_score'] * exp['novelty_weight'])
        ]
        components.sort(key=lambda x: x[1], reverse=True)
        
        movie_info = self.movies_df[self.movies_df['movieId'] == movie_id].iloc[0]
        
        explanation = {
            'movie': movie_info['title'],
            'genres': movie_info['genres'],
            'overall_score': round(pred['score'], 4),
            'primary_reason': components[0][0],
            'score_breakdown': {
                'CF': f"{exp['cf_score']:.3f} (weight: {exp['cf_weight']})",
                'Content': f"{exp['content_score']:.3f} (weight: {exp['content_weight']})",
                'SVD': f"{exp['svd_score']:.3f} (weight: {exp['svd_weight']})",
                'Novelty': f"{exp['novelty_score']:.3f} (weight: {exp['novelty_weight']})"
            },
            'human_explanation': self._generate_human_explanation(user_id, movie_id, components)
        }
        
        return explanation
    
    def _generate_human_explanation(self, user_id: int, movie_id: int, components: list) -> str:
        """Generate human-readable explanation text"""
        primary = components[0][0]
        
        explanations = {
            'collaborative filtering': "Users with similar taste to yours loved this movie",
            'content similarity': "This movie matches the genres and themes you enjoy",
            'rating prediction': "Our algorithm predicts you'll rate this highly",
            'novelty/discovery': "This is a hidden gem you might not have discovered otherwise"
        }
        
        return explanations.get(primary, "We think you'll enjoy this movie")
    
    def save(self, path: str = "model/hybrid_recommender.pkl"):
        """Save the hybrid model"""
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"Hybrid recommender saved to {path}")
    
    @staticmethod
    def load(path: str = "model/hybrid_recommender.pkl"):
        """Load the hybrid model"""
        with open(path, "rb") as f:
            return pickle.load(f)
