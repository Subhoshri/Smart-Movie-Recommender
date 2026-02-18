"""
Recommendation endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from api.schemas import (
    RecommendRequest,
    RecommendResponse,
    RecommendationItem,
    ExplainRequest,
    ExplainResponse,
    MovieSearchRequest,
    MovieSearchResponse,
    MovieDetail
)
from api.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """
    Get personalized movie recommendations for a user
    
    - **user_id**: User ID to get recommendations for
    - **n**: Number of recommendations (1-50)
    - **exclude_rated**: Skip movies user has already rated
    - **diversify**: Apply diversity optimization
    - **explain**: Include score breakdown for each recommendation
    """
    try:
        recommendations = recommendation_service.get_recommendations(
            user_id=request.user_id,
            n=request.n,
            exclude_rated=request.exclude_rated,
            diversify=request.diversify,
            explain=request.explain
        )
        
        # Convert to response model
        items = [RecommendationItem(**rec) for rec in recommendations]
        
        return RecommendResponse(
            user_id=request.user_id,
            recommendations=items,
            total=len(items)
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/explain", response_model=ExplainResponse)
async def explain_recommendation(request: ExplainRequest):
    """
    Get detailed explanation for why a movie was recommended
    
    - **user_id**: User ID
    - **movie_id**: Movie ID to explain
    """
    try:
        explanation = recommendation_service.get_explanation(
            user_id=request.user_id,
            movie_id=request.movie_id
        )
        
        return ExplainResponse(**explanation)
        
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.post("/search", response_model=MovieSearchResponse)
async def search_movies(request: MovieSearchRequest):
    """
    Search for movies by title or genre
    
    - **query**: Search query (movie title or genre)
    - **limit**: Maximum number of results (1-100)
    """
    try:
        results = recommendation_service.search_movies(
            query=request.query,
            limit=request.limit
        )
        
        # Convert to response model
        movies = []
        for movie in results:
            movies.append(MovieDetail(
                movie_id=movie['movieId'],
                title=movie['title'],
                genres=movie['genres']
            ))
        
        return MovieSearchResponse(
            query=request.query,
            results=movies,
            total=len(movies)
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/movie/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: int):
    """
    Get information about a specific movie
    
    - **movie_id**: Movie ID
    """
    try:
        movie = recommendation_service.get_movie_info(movie_id)
        
        if movie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie {movie_id} not found"
            )
        
        return MovieDetail(
            movie_id=movie['movieId'],
            title=movie['title'],
            genres=movie['genres']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get movie error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get movie: {str(e)}"
        )
