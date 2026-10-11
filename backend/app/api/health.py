from fastapi import APIRouter
from app.database.mongodb import get_database
from app.services.recommendation_service import engine_manager
from app.models.schemas import HealthSchema

router = APIRouter()

@router.get("/health", response_model=HealthSchema, tags=["Health"])
async def health_check():
    db = get_database()
    mongo_ok = False
    total_books = 0
    total_users = 0
    total_ratings = 0

    if db is not None:
        try:
            mongo_ok = True
            total_books = await db["books"].count_documents({})
            total_users = await db["users"].count_documents({})
            total_ratings = await db["ratings"].count_documents({})
        except Exception:
            mongo_ok = False

    return HealthSchema(
        status="ok" if (mongo_ok and engine_manager.is_loaded) else "degraded",
        mongodb_connected=mongo_ok,
        models_loaded=engine_manager.is_loaded,
        selected_algorithm=engine_manager.model_config.get("selected_algorithm", "Item-Item Cosine Similarity"),
        total_books=total_books,
        total_users=total_users,
        total_ratings=total_ratings
    )
