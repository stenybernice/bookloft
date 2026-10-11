from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.database.mongodb import get_database
from app.services.recommendation_service import engine_manager
from app.models.schemas import RatingSubmission, RatingResponse

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("", response_model=RatingResponse)
async def submit_rating(payload: RatingSubmission):
    user_id = payload.user_id
    clean_isbn = payload.isbn.strip().upper()
    rating_val = payload.rating

    db = get_database()
    doc_id = f"{user_id}_{clean_isbn}"

    # 1. Save / Upsert in MongoDB
    if db is not None:
        try:
            await db["ratings"].update_one(
                {"_id": doc_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "isbn": clean_isbn,
                        "rating": rating_val,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"MongoDB rating save error: {e}")

    # 2. Update user's in-memory interaction history instantly
    total_user_ratings = engine_manager.add_user_rating(user_id, clean_isbn, rating_val)

    return RatingResponse(
        status="success",
        message=f"Rating of {rating_val}/10 successfully saved for book ISBN '{clean_isbn}'.",
        user_id=user_id,
        isbn=clean_isbn,
        rating=rating_val,
        user_total_ratings=total_user_ratings
    )
