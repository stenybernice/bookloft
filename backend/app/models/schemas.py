from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BookSchema(BaseModel):
    isbn: str
    title: str
    author: str
    year: int = 2000
    publisher: str = "Unknown Publisher"
    rating_count: int = 0
    avg_rating: float = 0.0
    popularity_score: float = 0.0
    image_url_m: str
    image_url_l: Optional[str] = None
    recommendation_reason: Optional[str] = None
    similarity_score: Optional[float] = None
    hybrid_score: Optional[float] = None

class RatingSubmission(BaseModel):
    user_id: int = Field(..., description="ID of the user rating the book")
    isbn: str = Field(..., description="ISBN of the book being rated")
    rating: int = Field(..., ge=1, le=10, description="Rating value from 1 to 10")

class RatingResponse(BaseModel):
    status: str
    message: str
    user_id: int
    isbn: str
    rating: int
    user_total_ratings: int

class RecommendationResponse(BaseModel):
    strategy: str  # "popularity", "collaborative", "hybrid"
    cold_start: bool
    user_id: Optional[int] = None
    count: int
    weights_used: Optional[Dict[str, float]] = None
    items: List[BookSchema]

class UserProfileSchema(BaseModel):
    user_id: int
    location: str
    age: int
    rating_count: int
    recent_ratings: List[Dict[str, Any]] = []

class DemoUserSchema(BaseModel):
    user_id: int
    name: str
    persona: str
    location: str
    age: int
    rating_count: int

class HealthSchema(BaseModel):
    status: str
    mongodb_connected: bool
    models_loaded: bool
    selected_algorithm: str
    total_books: int
    total_users: int
    total_ratings: int
