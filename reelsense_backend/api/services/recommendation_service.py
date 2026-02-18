"""
Recommendation service - Handles model loading and inference
"""
import pickle
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging

from model.hybrid_recommender import HybridRecommender

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating recommendations using trained models"""
    
    def __init__(self, model_dir: str = "model/trained"):
        self.model_dir = Path(model_dir)
        self.recommender: Optional[HybridRecommender] = None
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self._is_loaded = False
        
    def load_models(self):
        """Load trained models and data"""
        try:
            logger.info("Loading hybrid recommender model...")
            self.recommender = HybridRecommender.load(
                str(self.model_dir / "hybrid_recommender.pkl")
            )
            
            logger.info("Loading ratings and movies data...")
            self.ratings_df = pd.read_csv(self.model_dir / "ratings.csv")
            self.movies_df = pd.read_csv(self.model_dir / "movies.csv")
            
            self._is_loaded = True
            logger.info(f"✅ Models loaded successfully!")
            logger.info(f"   - {len(self.movies_df)} movies")
            logger.info(f"   - {len(self.ratings_df)} ratings")
            logger.info(f"   - {self.ratings_df['userId'].nunique()} users")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._is_loaded and self.recommender is not None
    
    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        exclude_rated: bool = True,
        diversify: bool = True,
        explain: bool = False
    ) -> List[Dict]:
        """
        Generate recommendations for a user
        
        Returns:
            List of recommendation dicts
        """
        if not self.is_ready():
            raise RuntimeError("Service not ready. Call load_models() first.")
        
        # Check if user exists
        if user_id not in self.ratings_df['userId'].values:
            logger.warning(f"User {user_id} not found in training data. Using cold-start strategy.")
            # For new users, return popular + diverse movies
            return self._cold_start_recommendations(n, explain)
        
        try:
            recommendations = self.recommender.recommend(
                user_id=user_id,
                n=n,
                exclude_rated=exclude_rated,
                diversify=diversify,
                explain=explain
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise
    
    def get_explanation(self, user_id: int, movie_id: int) -> Dict:
        """
        Get detailed explanation for a recommendation
        
        Returns:
            Explanation dict
        """
        if not self.is_ready():
            raise RuntimeError("Service not ready. Call load_models() first.")
        
        try:
            explanation = self.recommender.get_explanation(user_id, movie_id)
            return explanation
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            raise
    
    def add_rating(self, user_id: int, movie_id: int, rating: float) -> Dict:
        """
        Add a new rating (in-memory only for now)
        
        TODO: Persist to database and retrain periodically
        
        Returns:
            Confirmation dict
        """
        if not self.is_ready():
            raise RuntimeError("Service not ready. Call load_models() first.")
        
        # For now, just add to in-memory DataFrame
        # In production, this should go to database
        new_rating = pd.DataFrame([{
            'userId': user_id,
            'movieId': movie_id,
            'rating': rating,
            'timestamp': pd.Timestamp.now().timestamp()
        }])
        
        self.ratings_df = pd.concat([self.ratings_df, new_rating], ignore_index=True)
        
        logger.info(f"Rating added: User {user_id} rated Movie {movie_id} with {rating}")
        
        return {
            'status': 'success',
            'message': 'Rating saved (in-memory). Model will be updated in next training cycle.',
            'user_id': user_id,
            'movie_id': movie_id,
            'rating': rating
        }
    
    def search_movies(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for movies by title or genre
        
        Returns:
            List of matching movies
        """
        if not self.is_ready():
            raise RuntimeError("Service not ready. Call load_models() first.")
        
        query_lower = query.lower()
        
        # Search in title and genres
        matches = self.movies_df[
            self.movies_df['title'].str.lower().str.contains(query_lower, na=False) |
            self.movies_df['genres'].str.lower().str.contains(query_lower, na=False)
        ]
        
        results = matches.head(limit).to_dict('records')
        
        logger.info(f"Search '{query}' found {len(results)} results")
        return results
    
    def get_movie_info(self, movie_id: int) -> Optional[Dict]:
        """Get information about a specific movie"""
        if not self.is_ready():
            raise RuntimeError("Service not ready. Call load_models() first.")
        
        movie = self.movies_df[self.movies_df['movieId'] == movie_id]
        
        if movie.empty:
            return None
        
        return movie.iloc[0].to_dict()
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        if not self.is_ready():
            return {
                'status': 'not_ready',
                'model_loaded': False
            }
        
        return {
            'status': 'ready',
            'model_loaded': True,
            'total_movies': len(self.movies_df),
            'total_ratings': len(self.ratings_df),
            'total_users': self.ratings_df['userId'].nunique(),
            'model_weights': {
                'alpha': self.recommender.alpha,
                'beta': self.recommender.beta,
                'gamma': self.recommender.gamma,
                'delta': self.recommender.delta
            }
        }
    
    def _cold_start_recommendations(self, n: int, explain: bool) -> List[Dict]:
        """
        Recommendations for new users (cold start)
        Uses popularity + diversity
        """
        # Get most rated movies
        popular_movies = self.ratings_df.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).reset_index()
        
        popular_movies.columns = ['movieId', 'count', 'avg_rating']
        
        # Filter: at least 50 ratings and avg >= 4.0
        popular = popular_movies[
            (popular_movies['count'] >= 50) & 
            (popular_movies['avg_rating'] >= 4.0)
        ].sort_values('count', ascending=False)
        
        # Get diverse genres
        recommendations = []
        seen_genres = set()
        
        for _, row in popular.iterrows():
            if len(recommendations) >= n:
                break
            
            movie_info = self.get_movie_info(row['movieId'])
            if movie_info is None:
                continue
            
            genres = set(movie_info['genres'].split('|'))
            
            # Add if introduces new genre
            if not genres.issubset(seen_genres) or len(recommendations) < 3:
                rec = {
                    'movie_id': int(row['movieId']),
                    'title': movie_info['title'],
                    'genres': movie_info['genres'],
                    'score': 0.8  # Fixed score for cold start
                }
                
                if explain:
                    rec['explanation'] = {
                        'cf_score': 0.0,
                        'cf_weight': 0.0,
                        'content_score': 0.0,
                        'content_weight': 0.0,
                        'svd_score': 0.0,
                        'svd_weight': 0.0,
                        'novelty_score': 1.0,
                        'novelty_weight': 1.0,
                        'final_score': 0.8
                    }
                
                recommendations.append(rec)
                seen_genres.update(genres)
        
        logger.info(f"Cold start: generated {len(recommendations)} popular/diverse recommendations")
        return recommendations


# Global service instance (singleton)
recommendation_service = RecommendationService()
