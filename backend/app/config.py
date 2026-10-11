import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "book_recommender"
    FRONTEND_URL: str = "http://localhost:5173"
    CF_WEIGHT: float = 0.7
    POPULARITY_WEIGHT: float = 0.3
    MODEL_ARTIFACTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
