from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.database.mongodb import get_database
from app.services.recommendation_service import engine_manager
from app.models.schemas import DemoUserSchema, UserProfileSchema

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/demo", response_model=List[DemoUserSchema])
async def get_demo_users():
    """Returns curated demo users for front-end persona switching."""
    # Find existing users from engine cache with rating histories
    user_counts = [(u_id, len(ratings)) for u_id, ratings in engine_manager.user_history_cache.items() if len(ratings) >= 2]
    user_counts.sort(key=lambda x: x[1], reverse=True)

    demo_list = [
        DemoUserSchema(
            user_id=99999,
            name="Aria Vance (New Reader)",
            persona="New Reader",
            location="New York, NY, USA",
            age=24,
            rating_count=0
        )
    ]

    personas = [
        ("Maya Lin", "Fiction & Mystery Lover", 28, "Toronto, Canada"),
        ("Liam O'Connor", "Classic Literature Enthusiast", 34, "London, UK"),
        ("Elena Rostova", "Fantasy & Sci-Fi Avid Reader", 26, "Berlin, Germany"),
        ("Marcus Vance", "Thrillers & Non-Fiction Reader", 42, "Austin, TX, USA")
    ]

    for i, (name, persona, age, location) in enumerate(personas):
        if i < len(user_counts):
            uid, count = user_counts[i]
            demo_list.append(DemoUserSchema(
                user_id=int(uid),
                name=f"{name} (User #{uid})",
                persona=persona,
                location=location,
                age=age,
                rating_count=count
            ))

    return demo_list

@router.get("/{user_id}", response_model=UserProfileSchema)
async def get_user_profile(user_id: int):
    db = get_database()
    user_ratings_dict = engine_manager.get_user_ratings(user_id)

    user_doc = None
    if db is not None:
        user_doc = await db["users"].find_one({"user_id": user_id})

    location = user_doc.get("location", "Unknown Location") if user_doc else "Demo Location"
    age = int(user_doc.get("age", 25)) if user_doc else 25

    recent_list = []
    for isbn, rating in list(user_ratings_dict.items())[:20]:
        meta = engine_manager.books_metadata.get(isbn, {})
        recent_list.append({
            "isbn": isbn,
            "title": meta.get("title", f"Book {isbn}"),
            "author": meta.get("author", "Unknown Author"),
            "image_url_m": meta.get("image_url_m", ""),
            "user_rating": rating
        })

    return UserProfileSchema(
        user_id=user_id,
        location=location,
        age=age,
        rating_count=len(user_ratings_dict),
        recent_ratings=recent_list
    )
