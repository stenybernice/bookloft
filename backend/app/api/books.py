import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.database.mongodb import get_database
from app.services.recommendation_service import engine_manager
from app.models.schemas import BookSchema

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/search", response_model=List[BookSchema])
async def search_books(q: str = Query(..., min_length=1, description="Query string for title, author, or ISBN"), limit: int = Query(20, ge=1, le=50)):
    db = get_database()
    clean_q = q.strip()
    regex_pattern = re.compile(re.escape(clean_q), re.IGNORECASE)

    results = []

    if db is not None:
        cursor = db["books"].find({
            "$or": [
                {"title": {"$regex": regex_pattern}},
                {"author": {"$regex": regex_pattern}},
                {"isbn": {"$regex": regex_pattern}},
                {"publisher": {"$regex": regex_pattern}}
            ]
        }).limit(limit)

        async for doc in cursor:
            results.append(BookSchema(
                isbn=str(doc["isbn"]),
                title=doc.get("title", "Unknown Title"),
                author=doc.get("author", "Unknown Author"),
                year=int(doc.get("year", 2000)),
                publisher=doc.get("publisher", "Unknown Publisher"),
                rating_count=int(doc.get("rating_count", 0)),
                avg_rating=float(doc.get("avg_rating", 0.0)),
                popularity_score=float(doc.get("popularity_score", 0.0)),
                image_url_m=doc.get("image_url_m", ""),
                image_url_l=doc.get("image_url_l", None)
            ))

    # Fallback to in-memory metadata if db query empty
    if not results and engine_manager.is_loaded:
        q_lower = clean_q.lower()
        for isbn, meta in engine_manager.books_metadata.items():
            if (q_lower in meta.get("title", "").lower() or
                q_lower in meta.get("author", "").lower() or
                q_lower in isbn.lower()):
                results.append(BookSchema(
                    isbn=isbn,
                    title=meta.get("title", "Unknown Title"),
                    author=meta.get("author", "Unknown Author"),
                    year=int(meta.get("year", 2000)),
                    publisher=meta.get("publisher", "Unknown Publisher"),
                    rating_count=int(meta.get("rating_count", 0)),
                    avg_rating=float(meta.get("avg_rating", 0.0)),
                    popularity_score=float(meta.get("popularity_score", 0.0)),
                    image_url_m=meta.get("image_url_m", ""),
                    image_url_l=meta.get("image_url_l", None)
                ))
                if len(results) >= limit:
                    break

    return results

@router.get("/{isbn}", response_model=BookSchema)
async def get_book_details(isbn: str):
    db = get_database()
    clean_isbn = isbn.strip().upper()

    doc = None
    if db is not None:
        doc = await db["books"].find_one({"isbn": clean_isbn})

    if not doc and engine_manager.is_loaded:
        meta = engine_manager.books_metadata.get(clean_isbn)
        if meta:
            doc = meta
            doc["isbn"] = clean_isbn

    if not doc:
        raise HTTPException(status_code=404, detail=f"Book with ISBN '{clean_isbn}' not found.")

    return BookSchema(
        isbn=str(doc["isbn"]),
        title=doc.get("title", "Unknown Title"),
        author=doc.get("author", "Unknown Author"),
        year=int(doc.get("year", 2000)),
        publisher=doc.get("publisher", "Unknown Publisher"),
        rating_count=int(doc.get("rating_count", 0)),
        avg_rating=float(doc.get("avg_rating", 0.0)),
        popularity_score=float(doc.get("popularity_score", 0.0)),
        image_url_m=doc.get("image_url_m", ""),
        image_url_l=doc.get("image_url_l", None)
    )

@router.get("/{isbn}/similar", response_model=List[BookSchema])
async def get_similar_books(isbn: str, limit: int = Query(6, ge=1, le=20)):
    clean_isbn = isbn.strip().upper()
    if not engine_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Recommendation engine not loaded.")

    similar_books = engine_manager.collaborative_service.get_similar_books(clean_isbn, limit=limit)
    return similar_books
