from typing import List, Dict, Any
from app.models.schemas import BookSchema

class PopularityService:
    def __init__(self, popularity_artifact: Dict[str, Any], metadata_artifact: Dict[str, Any]):
        self.popularity_df = popularity_artifact.get("popularity_df", [])
        self.empirical_m = popularity_artifact.get("empirical_m", 5.0)
        self.global_C = popularity_artifact.get("global_C", 6.0)
        self.books_metadata = metadata_artifact.get("books_metadata", {})

        # Sort books by popularity_score descending
        self.sorted_books = sorted(
            self.popularity_df,
            key=lambda x: x.get("popularity_score", 0),
            reverse=True
        )

    def get_popular(self, limit: int = 10, exclude_isbns: set = None) -> List[BookSchema]:
        exclude_isbns = exclude_isbns or set()
        results = []

        for item in self.sorted_books:
            isbn = str(item["isbn"])
            if isbn in exclude_isbns:
                continue

            meta = self.books_metadata.get(isbn, item)

            book = BookSchema(
                isbn=isbn,
                title=meta.get("title", item.get("title", "Unknown Title")),
                author=meta.get("author", item.get("author", "Unknown Author")),
                year=int(meta.get("year", item.get("year", 2000))),
                publisher=meta.get("publisher", item.get("publisher", "Unknown Publisher")),
                rating_count=int(meta.get("rating_count", item.get("rating_count", 0))),
                avg_rating=float(meta.get("avg_rating", item.get("avg_rating", 0.0))),
                popularity_score=float(meta.get("popularity_score", item.get("popularity_score", 0.0))),
                image_url_m=meta.get("image_url_m", item.get("image_url_m", "")),
                image_url_l=meta.get("image_url_l", item.get("image_url_l", None)),
                recommendation_reason=f"Top Rated Popular Choice (Weighted Score: {float(item.get('popularity_score', 0)):.2f})"
            )
            results.append(book)

            if len(results) >= limit:
                break

        return results
