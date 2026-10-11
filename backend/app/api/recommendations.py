from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.recommendation_service import engine_manager
from app.models.schemas import RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/popular", response_model=RecommendationResponse)
async def get_popular_recommendations(limit: int = Query(10, ge=1, le=50)):
    if not engine_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded.")

    items = engine_manager.popularity_service.get_popular(limit=limit)
    return RecommendationResponse(
        strategy="popularity",
        cold_start=True,
        count=len(items),
        items=items
    )

@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def get_user_collaborative_recommendations(user_id: int, limit: int = Query(10, ge=1, le=50)):
    if not engine_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded.")

    user_ratings = engine_manager.get_user_ratings(user_id)
    items, is_cold_start = engine_manager.collaborative_service.get_recommendations(
        user_ratings=user_ratings,
        limit=limit
    )

    if is_cold_start:
        items = engine_manager.popularity_service.get_popular(limit=limit)
        for b in items:
            b.recommendation_reason = "Popular with readers"

    return RecommendationResponse(
        strategy="collaborative" if not is_cold_start else "popularity_cold_start",
        cold_start=is_cold_start,
        user_id=user_id,
        count=len(items),
        items=items
    )

@router.get("/hybrid/{user_id}", response_model=RecommendationResponse)
async def get_hybrid_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    cf_weight: Optional[float] = Query(None, ge=0.0, le=1.0),
    popularity_weight: Optional[float] = Query(None, ge=0.0, le=1.0)
):
    if not engine_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded.")

    user_ratings = engine_manager.get_user_ratings(user_id)
    items, is_cold_start, weights_used = engine_manager.hybrid_service.get_hybrid_recommendations(
        user_ratings=user_ratings,
        limit=limit,
        cf_weight_override=cf_weight,
        pop_weight_override=popularity_weight
    )

    return RecommendationResponse(
        strategy="hybrid" if not is_cold_start else "popularity_cold_start",
        cold_start=is_cold_start,
        user_id=user_id,
        count=len(items),
        weights_used=weights_used,
        items=items
    )
