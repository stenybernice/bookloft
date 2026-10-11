import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.services.recommendation_service import engine_manager
from app.api import health, books, recommendations, ratings, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("book_recommender_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Book Recommendation System Backend...")
    # 1. Connect to MongoDB
    await connect_to_mongo()

    # 2. Load ML Recommendation Models once into memory
    engine_manager.load_artifacts()

    logger.info("Backend Lifespan Startup Complete! API is ready.")
    yield

    logger.info("Shutting down backend services...")
    await close_mongo_connection()

app = FastAPI(
    title="Hybrid Book Recommendation Engine API",
    description="Production-style ML Book Recommendation Backend combining Popularity-based scoring and Item-based Collaborative Filtering.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(ratings.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "name": "Hybrid Book Recommendation System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "status": "online"
    }
