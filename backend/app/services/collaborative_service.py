import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schemas import BookSchema

class CollaborativeService:
    def __init__(self, cf_artifact: Dict[str, Any], metadata_artifact: Dict[str, Any]):
        self.item_similarity = cf_artifact["item_similarity"]  # CSR matrix (n_books x n_books)
        self.book_to_idx = cf_artifact["book_to_idx"]
        self.idx_to_book = cf_artifact["idx_to_book"]
        self.n_books = cf_artifact["n_books"]
        self.books_metadata = metadata_artifact.get("books_metadata", {})

    def get_recommendations(
        self,
        user_ratings: Dict[str, int],
        limit: int = 10,
        exclude_isbns: set = None
    ) -> Tuple[List[BookSchema], bool]:
        """
        Generates item-based collaborative filtering recommendations.
        Returns: (list of BookSchema, is_cold_start boolean)
        """
        exclude_isbns = exclude_isbns or set()
        rated_items = {str(k): v for k, v in user_ratings.items() if v > 0}

        # Cold Start check: if user has 0 explicit ratings
        if not rated_items:
            return [], True

        # Map user's rated ISBNs to matrix column indices
        rated_indices = []
        rated_ratings = []
        rated_titles = {}

        for isbn, r in rated_items.items():
            if isbn in self.book_to_idx:
                idx = self.book_to_idx[isbn]
                rated_indices.append(idx)
                rated_ratings.append(r)
                meta = self.books_metadata.get(isbn, {})
                rated_titles[idx] = (meta.get("title", f"Book {isbn}"), r)

        if not rated_indices:
            return [], True

        rated_indices = np.array(rated_indices)
        rated_ratings = np.array(rated_ratings, dtype=np.float32)

        # Slice sub-matrix of item similarity for rated items: (len(rated_indices) x n_books)
        sim_sub = self.item_similarity[rated_indices].toarray()  # (k x n_books)

        # Calculate weighted score: sum(sim * rating) / sum(sim)
        weighted_sim = sim_sub * rated_ratings[:, np.newaxis]  # (k x n_books)
        raw_scores = np.sum(weighted_sim, axis=0)
        sim_sums = np.sum(np.abs(sim_sub), axis=0)

        # Avoid divide by zero
        scores = np.zeros(self.n_books, dtype=np.float32)
        valid_mask = sim_sums > 0
        scores[valid_mask] = raw_scores[valid_mask] / sim_sums[valid_mask]

        # Zero out already rated items and excluded ISBNs
        for idx in rated_indices:
            scores[idx] = -1.0

        for isbn in exclude_isbns:
            if isbn in self.book_to_idx:
                scores[self.book_to_idx[isbn]] = -1.0

        top_indices = np.argsort(scores)[::-1]
        results = []

        for idx in top_indices:
            score_val = float(scores[idx])
            if score_val <= 0:
                break

            target_isbn = self.idx_to_book[idx]
            if target_isbn in exclude_isbns:
                continue

            # Find which rated book contributed most to this recommendation
            item_sim_vec = sim_sub[:, idx]  # sim of all rated books with target
            best_contributor_k = np.argmax(item_sim_vec * rated_ratings)
            contrib_idx = rated_indices[best_contributor_k]
            contrib_title, contrib_rating = rated_titles[contrib_idx]

            meta = self.books_metadata.get(target_isbn, {})

            reason = f"Recommended because you rated '{contrib_title}' {contrib_rating}/10"

            book = BookSchema(
                isbn=target_isbn,
                title=meta.get("title", f"Book {target_isbn}"),
                author=meta.get("author", "Unknown Author"),
                year=int(meta.get("year", 2000)),
                publisher=meta.get("publisher", "Unknown Publisher"),
                rating_count=int(meta.get("rating_count", 0)),
                avg_rating=float(meta.get("avg_rating", 0.0)),
                popularity_score=float(meta.get("popularity_score", 0.0)),
                image_url_m=meta.get("image_url_m", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"),
                image_url_l=meta.get("image_url_l", None),
                similarity_score=round(score_val, 4),
                recommendation_reason=reason
            )
            results.append(book)

            if len(results) >= limit:
                break

        if not results:
            return [], True

        return results, False

    def get_similar_books(self, isbn: str, limit: int = 6) -> List[BookSchema]:
        """Gets items most similar to a given book (for 'You May Also Like')."""
        if isbn not in self.book_to_idx:
            return []

        target_idx = self.book_to_idx[isbn]
        sim_vec = self.item_similarity[target_idx].toarray().flatten()
        sim_vec[target_idx] = -1.0  # exclude self

        top_indices = np.argsort(sim_vec)[::-1][:limit]
        target_meta = self.books_metadata.get(isbn, {})
        target_title = target_meta.get("title", f"ISBN {isbn}")

        results = []
        for idx in top_indices:
            sim_score = float(sim_vec[idx])
            if sim_score <= 0:
                break
            b_isbn = self.idx_to_book[idx]
            meta = self.books_metadata.get(b_isbn, {})

            book = BookSchema(
                isbn=b_isbn,
                title=meta.get("title", f"Book {b_isbn}"),
                author=meta.get("author", "Unknown Author"),
                year=int(meta.get("year", 2000)),
                publisher=meta.get("publisher", "Unknown Publisher"),
                rating_count=int(meta.get("rating_count", 0)),
                avg_rating=float(meta.get("avg_rating", 0.0)),
                popularity_score=float(meta.get("popularity_score", 0.0)),
                image_url_m=meta.get("image_url_m", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"),
                image_url_l=meta.get("image_url_l", None),
                similarity_score=round(sim_score, 4),
                recommendation_reason=f"Similar story and audience to '{target_title}' ({sim_score:.0%} similarity match)"
            )
            results.append(book)

        return results
