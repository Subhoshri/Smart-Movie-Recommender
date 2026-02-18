"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime


# ==================== Movie Schemas ====================

class MovieBase(BaseModel):
    """Base movie information"""
    movie_id: int
    title: str
    genres: str


class MovieDetail(MovieBase):
    """Detailed movie information"""
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None


# ==================== Recommendation Schemas ====================

class ScoreBreakdown(BaseModel):
    """Explanation of recommendation score components"""
    cf_score: float = Field(..., description="Collaborative filtering score")
    cf_weight: float
    content_score: float = Field(..., description="Content similarity score")
    content_weight: float
    svd_score: float = Field(..., description="SVD prediction score")
    svd_weight: float
    novelty_score: float = Field(..., description="Novelty/diversity score")
    novelty_weight: float
    final_score: float


class RecommendationItem(BaseModel):
    """Single recommendation with optional explanation"""
    movie_id: int
    title: str
    genres: str
    score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation score")
    explanation: Optional[ScoreBreakdown] = None


class RecommendRequest(BaseModel):
    """Request for movie recommendations"""
    user_id: int = Field(..., gt=0, description="User ID")
    n: int = Field(10, ge=1, le=50, description="Number of recommendations")
    exclude_rated: bool = Field(True, description="Exclude movies user has already rated")
    diversify: bool = Field(True, description="Apply diversity optimization")
    explain: bool = Field(False, description="Include explanation for each recommendation")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 1,
            "n": 10,
            "exclude_rated": True,
            "diversify": True,
            "explain": False
        }
    })


class RecommendResponse(BaseModel):
    """Response with recommendations"""
    user_id: int
    recommendations: List[RecommendationItem]
    total: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Explanation Schemas ====================

class ExplainRequest(BaseModel):
    """Request for recommendation explanation"""
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)


class ExplainResponse(BaseModel):
    """Detailed explanation of why a movie was recommended"""
    movie: str
    genres: str
    overall_score: float
    primary_reason: str
    score_breakdown: Dict[str, str]
    human_explanation: str


# ==================== Rating Schemas ====================

class RatingCreate(BaseModel):
    """Submit a new rating"""
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating from 0.5 to 5.0")
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 1,
            "movie_id": 260,
            "rating": 4.5
        }
    })


class RatingResponse(BaseModel):
    """Response after submitting rating"""
    user_id: int
    movie_id: int
    rating: float
    timestamp: datetime
    message: str = "Rating saved successfully"


# ==================== User Schemas ====================

class UserCreate(BaseModel):
    """Register new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """User login credentials"""
    username: str
    password: str


class UserResponse(BaseModel):
    """User information response"""
    user_id: int
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


# ==================== Search Schemas ====================

class MovieSearchRequest(BaseModel):
    """Search for movies"""
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)


class MovieSearchResponse(BaseModel):
    """Search results"""
    query: str
    results: List[MovieDetail]
    total: int


# ==================== Health Check ====================

class HealthResponse(BaseModel):
    """API health status"""
    status: str
    model_loaded: bool
    total_movies: int
    total_users: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
