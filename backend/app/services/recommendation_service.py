import os
import json
import pickle
import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.popularity_service import PopularityService
from app.services.collaborative_service import CollaborativeService
from app.services.hybrid_service import HybridService
from app.models.schemas import BookSchema

logger = logging.getLogger(__name__)

class RecommendationEngineManager:
    def __init__(self):
        self.is_loaded = False
        self.popularity_service = None
        self.collaborative_service = None
        self.hybrid_service = None
        self.user_history_cache: Dict[int, Dict[str, int]] = {}
        self.books_metadata: Dict[str, Dict[str, Any]] = {}
        self.model_config: Dict[str, Any] = {}

    def load_artifacts(self):
        artifacts_dir = settings.MODEL_ARTIFACTS_DIR
        logger.info(f"Loading ML model artifacts from {artifacts_dir}...")

        pop_path = os.path.join(artifacts_dir, "popularity_model.pkl")
        collab_path = os.path.join(artifacts_dir, "collaborative_model.pkl")
        meta_path = os.path.join(artifacts_dir, "metadata.pkl")
        config_path = os.path.join(artifacts_dir, "model_config.json")

        if not (os.path.exists(pop_path) and os.path.exists(collab_path) and os.path.exists(meta_path)):
            logger.warning("Artifact files missing. Attempting automated training run...")
            from scripts.train import train_pipeline
            train_pipeline()

        with open(pop_path, "rb") as f:
            pop_artifact = pickle.load(f)

        with open(collab_path, "rb") as f:
            collab_artifact = pickle.load(f)

        with open(meta_path, "rb") as f:
            meta_artifact = pickle.load(f)

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.model_config = json.load(f)

        self.user_history_cache = meta_artifact.get("user_history", {})
        self.books_metadata = meta_artifact.get("books_metadata", {})

        self.popularity_service = PopularityService(pop_artifact, meta_artifact)
        self.collaborative_service = CollaborativeService(collab_artifact, meta_artifact)
        self.hybrid_service = HybridService(self.popularity_service, self.collaborative_service)

        self.is_loaded = True
        logger.info(f"Successfully loaded ML models! Configured algorithm: {self.model_config.get('selected_algorithm', 'Item-Item Cosine Similarity')}")

    def get_user_ratings(self, user_id: int) -> Dict[str, int]:
        return self.user_history_cache.get(user_id, {})

    def add_user_rating(self, user_id: int, isbn: str, rating: int) -> int:
        """
        Updates in-memory interaction history instantly without triggering full model retraining.
        """
        if user_id not in self.user_history_cache:
            self.user_history_cache[user_id] = {}

        self.user_history_cache[user_id][isbn] = rating

        # Update book metadata stats in memory if present
        if isbn in self.books_metadata:
            b_meta = self.books_metadata[isbn]
            cnt = b_meta.get("rating_count", 0) + 1
            old_avg = b_meta.get("avg_rating", 0.0)
            new_avg = ((old_avg * (cnt - 1)) + rating) / cnt
            b_meta["rating_count"] = cnt
            b_meta["avg_rating"] = round(new_avg, 2)

        return len(self.user_history_cache[user_id])

engine_manager = RecommendationEngineManager()
