"""
Rating endpoints
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging

from api.schemas import RatingCreate, RatingResponse
from api.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["ratings"])


@router.post("/rate", response_model=RatingResponse)
async def submit_rating(rating: RatingCreate):
    """
    Submit a movie rating
    
    - **user_id**: User ID submitting the rating
    - **movie_id**: Movie being rated
    - **rating**: Rating value (0.5 to 5.0 in 0.5 increments)
    """
    try:
        # Validate movie exists
        movie = recommendation_service.get_movie_info(rating.movie_id)
        if movie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie {rating.movie_id} not found"
            )
        
        # Add rating
        result = recommendation_service.add_rating(
            user_id=rating.user_id,
            movie_id=rating.movie_id,
            rating=rating.rating
        )
        
        return RatingResponse(
            user_id=rating.user_id,
            movie_id=rating.movie_id,
            rating=rating.rating,
            timestamp=datetime.utcnow(),
            message=result.get('message', 'Rating saved successfully')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rating submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit rating: {str(e)}"
        )


@router.get("/user/{user_id}/ratings")
async def get_user_ratings(user_id: int, limit: int = 50):
    """
    Get a user's rating history
    
    - **user_id**: User ID
    - **limit**: Maximum number of ratings to return
    """
    try:
        # Get ratings from service
        ratings_df = recommendation_service.ratings_df
        user_ratings = ratings_df[ratings_df['userId'] == user_id]
        
        if user_ratings.empty:
            return {
                "user_id": user_id,
                "ratings": [],
                "total": 0
            }
        
        # Sort by timestamp (most recent first)
        user_ratings = user_ratings.sort_values('timestamp', ascending=False)
        user_ratings = user_ratings.head(limit)
        
        # Add movie titles
        ratings_list = []
        for _, row in user_ratings.iterrows():
            movie = recommendation_service.get_movie_info(int(row['movieId']))
            ratings_list.append({
                "movie_id": int(row['movieId']),
                "title": movie['title'] if movie else "Unknown",
                "genres": movie['genres'] if movie else "",
                "rating": float(row['rating']),
                "timestamp": datetime.fromtimestamp(row['timestamp'])
            })
        
        return {
            "user_id": user_id,
            "ratings": ratings_list,
            "total": len(ratings_list)
        }
        
    except Exception as e:
        logger.error(f"Get ratings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ratings: {str(e)}"
        )
