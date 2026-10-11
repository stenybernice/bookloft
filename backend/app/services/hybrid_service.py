import numpy as np
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.models.schemas import BookSchema
from app.services.popularity_service import PopularityService
from app.services.collaborative_service import CollaborativeService

class HybridService:
    def __init__(
        self,
        popularity_service: PopularityService,
        collaborative_service: CollaborativeService,
        cf_weight: float = None,
        popularity_weight: float = None
    ):
        self.popularity_service = popularity_service
        self.collaborative_service = collaborative_service
        self.cf_weight = cf_weight if cf_weight is not None else settings.CF_WEIGHT
        self.popularity_weight = popularity_weight if popularity_weight is not None else settings.POPULARITY_WEIGHT

    def get_hybrid_recommendations(
        self,
        user_ratings: Dict[str, int],
        limit: int = 10,
        cf_weight_override: float = None,
        pop_weight_override: float = None
    ) -> Tuple[List[BookSchema], bool, Dict[str, float]]:

        w_cf = cf_weight_override if cf_weight_override is not None else self.cf_weight
        w_pop = pop_weight_override if pop_weight_override is not None else self.popularity_weight

        # Normalize weights so they sum to 1.0
        total_w = w_cf + w_pop
        if total_w > 0:
            w_cf /= total_w
            w_pop /= total_w

        weights_used = {"CF_WEIGHT": round(w_cf, 2), "POPULARITY_WEIGHT": round(w_pop, 2)}

        # Check Cold Start (user has 0 ratings)
        if not user_ratings:
            pop_recs = self.popularity_service.get_popular(limit=limit)
            for b in pop_recs:
                b.recommendation_reason = f"Popular with readers (weighted score {b.popularity_score:.2f})"
            return pop_recs, True, weights_used

        # Fetch top candidate items from Collaborative Filtering (fetch candidate pool of 100)
        cf_candidates, is_cold_start = self.collaborative_service.get_recommendations(
            user_ratings=user_ratings,
            limit=100
        )

        if is_cold_start or not cf_candidates:
            pop_recs = self.popularity_service.get_popular(
                limit=limit,
                exclude_isbns=set(user_ratings.keys())
            )
            for b in pop_recs:
                b.recommendation_reason = "Popular with readers"
            return pop_recs, True, weights_used

        # Extract CF scores and Popularity scores for candidate items
        cf_scores = np.array([c.similarity_score for c in cf_candidates], dtype=np.float32)
        pop_scores = np.array([c.popularity_score for c in cf_candidates], dtype=np.float32)

        # Min-Max Normalization to [0, 1]
        def min_max_scale(arr):
            min_val = np.min(arr)
            max_val = np.max(arr)
            if max_val > min_val:
                return (arr - min_val) / (max_val - min_val)
            return np.ones_like(arr)

        norm_cf = min_max_scale(cf_scores)
        norm_pop = min_max_scale(pop_scores)

        hybrid_scores = (w_cf * norm_cf) + (w_pop * norm_pop)

        # Rank candidates by hybrid score
        ranked_indices = np.argsort(hybrid_scores)[::-1]
        results = []

        for idx in ranked_indices[:limit]:
            book = cf_candidates[idx]
            h_score = float(hybrid_scores[idx])
            book.hybrid_score = round(h_score, 4)

            # Detailed hybrid explanation
            book.recommendation_reason = (
                f"Hybrid Pick ({w_cf:.0%} CF Match + {w_pop:.0%} Popularity) — "
                f"Matches your shelf history & high community rating"
            )
            results.append(book)

        return results, False, weights_used
