"""
Health check and system status endpoints
"""
from fastapi import APIRouter
from datetime import datetime

from api.schemas import HealthResponse
from api.services.recommendation_service import recommendation_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns system status and model readiness
    """
    stats = recommendation_service.get_stats()
    
    return HealthResponse(
        status="healthy" if stats.get('model_loaded') else "not_ready",
        model_loaded=stats.get('model_loaded', False),
        total_movies=stats.get('total_movies', 0),
        total_users=stats.get('total_users', 0),
        timestamp=datetime.utcnow()
    )


@router.get("/")
async def root():
    """
    API root endpoint
    
    Welcome message and basic info
    """
    return {
        "name": "ReelSense API",
        "version": "1.0.0",
        "description": "Explainable Hybrid Movie Recommendation System",
        "docs": "/docs",
        "health": "/health"
    }


@router.get("/stats")
async def get_stats():
    """
    Get detailed system statistics
    
    Returns model configuration and data stats
    """
    return recommendation_service.get_stats()
