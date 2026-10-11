"""
Data Preprocessing & Cleaning Pipeline
---------------------------------------
Handles missing values, duplicate records, ISBN validation, explicit vs implicit ratings,
interaction sparsity thresholding, and empirical statistics generation.
Saves preprocessed CSVs and metadata to data/processed/.
"""

import os
import json
import re
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROC_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

def ensure_directories():
    os.makedirs(DATA_PROC_DIR, exist_ok=True)

def clean_isbn(isbn):
    """Standardize and validate ISBN format."""
    if pd.isna(isbn) or isbn is None:
        return None
    val_str = str(isbn).strip()
    clean = re.sub(r'[\s\-@#\$"]', '', val_str).upper()
    if len(clean) >= 5:
        return clean
    return None

def preprocess_pipeline(min_book_ratings=2, min_user_ratings=2):
    print("=" * 60)
    print("STARTING DATA PREPROCESSING PIPELINE")
    print("=" * 60)
    ensure_directories()

    books_path = os.path.join(DATA_RAW_DIR, "Books.csv")
    users_path = os.path.join(DATA_RAW_DIR, "Users.csv")
    ratings_path = os.path.join(DATA_RAW_DIR, "Ratings.csv")

    if not (os.path.exists(books_path) and os.path.exists(users_path) and os.path.exists(ratings_path)):
        raise FileNotFoundError("Raw files missing in data/raw/. Run scripts/download_data.py first.")

    # 1. Load Raw Datasets
    print("\n1. Loading raw CSV files...")
    books_df = pd.read_csv(books_path, low_memory=False, dtype=str)
    users_df = pd.read_csv(users_path, low_memory=False)
    ratings_df = pd.read_csv(ratings_path, low_memory=False, dtype={"User-ID": str, "ISBN": str, "Book-Rating": str})

    initial_stats = {
        "raw_books_count": len(books_df),
        "raw_users_count": len(users_df),
        "raw_ratings_count": len(ratings_df)
    }
    print(f"   Raw Books: {initial_stats['raw_books_count']:,}")
    print(f"   Raw Users: {initial_stats['raw_users_count']:,}")
    print(f"   Raw Ratings: {initial_stats['raw_ratings_count']:,}")

    # 2. Clean Books Metadata
    print("\n2. Cleaning Books metadata...")
    books_df["isbn"] = books_df["ISBN"].apply(clean_isbn)
    books_df = books_df.dropna(subset=["isbn"])

    col_map = {
        "Book-Title": "title",
        "Book-Author": "author",
        "Year-Of-Publication": "year",
        "Publisher": "publisher",
        "Image-URL-S": "image_url_s",
        "Image-URL-M": "image_url_m",
        "Image-URL-L": "image_url_l"
    }
    books_df = books_df.rename(columns=col_map)

    books_df["title"] = books_df["title"].fillna("Unknown Title").astype(str).str.strip()
    books_df["author"] = books_df["author"].fillna("Unknown Author").astype(str).str.strip()
    books_df["publisher"] = books_df["publisher"].fillna("Unknown Publisher").astype(str).str.strip()

    def parse_year(val):
        try:
            y = int(float(str(val).strip()))
            if 1300 <= y <= 2026:
                return y
            return 2000
        except (ValueError, TypeError):
            return 2000

    books_df["year"] = books_df["year"].apply(parse_year)

    fallback_img = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"
    if "image_url_m" in books_df.columns:
        books_df["image_url_m"] = books_df["image_url_m"].fillna(fallback_img)
    else:
        books_df["image_url_m"] = fallback_img

    if "image_url_l" in books_df.columns:
        books_df["image_url_l"] = books_df["image_url_l"].fillna(fallback_img)
    else:
        books_df["image_url_l"] = fallback_img

    books_df = books_df.drop_duplicates(subset=["isbn"]).copy()

    # 3. Clean Users Metadata
    print("\n3. Cleaning Users metadata...")
    users_df = users_df.rename(columns={"User-ID": "user_id", "Location": "location", "Age": "age"})
    users_df["user_id"] = pd.to_numeric(users_df["user_id"], errors="coerce").fillna(-1).astype(int)
    users_df = users_df[users_df["user_id"] > 0].copy()

    median_age = float(users_df["age"].median()) if "age" in users_df.columns and not users_df["age"].isnull().all() else 30.0
    users_df["age"] = pd.to_numeric(users_df["age"], errors="coerce")
    users_df.loc[(users_df["age"] < 5) | (users_df["age"] > 100), "age"] = np.nan
    users_df["age"] = users_df["age"].fillna(median_age).astype(int)
    users_df["location"] = users_df["location"].fillna("Unknown").astype(str).str.strip()

    # 4. Clean Ratings Dataset
    print("\n4. Cleaning Ratings & separating explicit vs implicit ratings...")
    ratings_df = ratings_df.rename(columns={"User-ID": "user_id", "ISBN": "isbn", "Book-Rating": "rating"})
    ratings_df["user_id"] = pd.to_numeric(ratings_df["user_id"], errors="coerce").fillna(-1).astype(int)
    ratings_df = ratings_df[ratings_df["user_id"] > 0]

    ratings_df["isbn"] = ratings_df["isbn"].apply(clean_isbn)
    ratings_df = ratings_df.dropna(subset=["isbn"])
    ratings_df["rating"] = pd.to_numeric(ratings_df["rating"], errors="coerce").fillna(0).astype(int)

    valid_isbns = set(books_df["isbn"].unique())
    valid_users = set(users_df["user_id"].unique())

    ratings_df = ratings_df[ratings_df["isbn"].isin(valid_isbns) & ratings_df["user_id"].isin(valid_users)]

    # Deduplicate (user_id, isbn) keeping max rating
    ratings_df = ratings_df.groupby(["user_id", "isbn"], as_index=False)["rating"].max()

    explicit_ratings = ratings_df[ratings_df["rating"] > 0].copy()
    implicit_ratings = ratings_df[ratings_df["rating"] == 0].copy()

    total_valid = max(1, len(ratings_df))
    print(f"   Total valid ratings: {len(ratings_df):,}")
    print(f"   Explicit ratings (1-10): {len(explicit_ratings):,} ({len(explicit_ratings)/total_valid:.1%})")
    print(f"   Implicit interactions (0): {len(implicit_ratings):,} ({len(implicit_ratings)/total_valid:.1%})")

    # 5. Interaction Filtering for Collaborative Filtering
    print(f"\n5. Filtering low-interaction users (<{min_user_ratings} ratings) and books (<{min_book_ratings} ratings) for CF matrix...")

    cf_ratings = explicit_ratings.copy() if len(explicit_ratings) > 0 else ratings_df.copy()

    for iteration in range(3):
        user_counts = cf_ratings["user_id"].value_counts()
        book_counts = cf_ratings["isbn"].value_counts()

        valid_u = user_counts[user_counts >= min_user_ratings].index
        valid_b = book_counts[book_counts >= min_book_ratings].index

        cf_ratings = cf_ratings[cf_ratings["user_id"].isin(valid_u) & cf_ratings["isbn"].isin(valid_b)]

    if len(cf_ratings) == 0:
        print("   Warning: Iterative threshold filtering yielded empty set. Falling back to explicit ratings.")
        cf_ratings = explicit_ratings.copy()

    global_mean_C = float(explicit_ratings["rating"].mean()) if len(explicit_ratings) > 0 else 6.0

    book_stats = explicit_ratings.groupby("isbn").agg(
        rating_count=("rating", "count"),
        avg_rating=("rating", "mean")
    ).reset_index()

    if len(book_stats) > 0:
        m_empirical = float(np.percentile(book_stats["rating_count"], 75))
        m_empirical = max(2.0, m_empirical)
    else:
        m_empirical = 5.0

    print(f"   Calculated Empirical Minimum Threshold m = {m_empirical:.2f}")
    print(f"   Global Mean Rating C = {global_mean_C:.2f}")

    # Popularity Weighted Score W = (v / (v + m)) * R + (m / (v + m)) * C
    book_stats["popularity_score"] = (
        (book_stats["rating_count"] / (book_stats["rating_count"] + m_empirical)) * book_stats["avg_rating"] +
        (m_empirical / (book_stats["rating_count"] + m_empirical)) * global_mean_C
    )

    books_processed = books_df[["isbn", "title", "author", "year", "publisher", "image_url_m", "image_url_l"]].merge(
        book_stats, on="isbn", how="left"
    )
    books_processed["rating_count"] = books_processed["rating_count"].fillna(0).astype(int)
    books_processed["avg_rating"] = books_processed["avg_rating"].fillna(0.0).round(2)
    books_processed["popularity_score"] = books_processed["popularity_score"].fillna(
        (m_empirical / (0 + m_empirical)) * global_mean_C
    ).round(4)

    n_users = len(cf_ratings["user_id"].unique())
    n_books = len(cf_ratings["isbn"].unique())
    n_ratings = len(cf_ratings)
    sparsity = (1.0 - (n_ratings / (n_users * n_books))) * 100 if (n_users * n_books) > 0 else 100.0

    stats_summary = {
        "total_books_in_catalog": len(books_processed),
        "total_users_in_catalog": len(users_df),
        "total_explicit_ratings": len(explicit_ratings),
        "total_implicit_interactions": len(implicit_ratings),
        "cf_filtered_users": n_users,
        "cf_filtered_books": n_books,
        "cf_filtered_ratings": n_ratings,
        "interaction_sparsity_percent": round(sparsity, 4),
        "global_mean_rating_C": round(global_mean_C, 4),
        "empirical_m_threshold": round(m_empirical, 2),
        "min_user_ratings_threshold": min_user_ratings,
        "min_book_ratings_threshold": min_book_ratings
    }

    print("\n6. Saving cleaned data and stats summary...")
    books_processed.to_csv(os.path.join(DATA_PROC_DIR, "cleaned_books.csv"), index=False)
    users_df.to_csv(os.path.join(DATA_PROC_DIR, "cleaned_users.csv"), index=False)
    cf_ratings.to_csv(os.path.join(DATA_PROC_DIR, "cleaned_ratings.csv"), index=False)
    explicit_ratings.to_csv(os.path.join(DATA_PROC_DIR, "all_explicit_ratings.csv"), index=False)

    with open(os.path.join(DATA_PROC_DIR, "dataset_stats.json"), "w") as f:
        json.dump(stats_summary, f, indent=2)

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE!")
    print(f"Summary Stats:\n{json.dumps(stats_summary, indent=2)}")
    print("=" * 60)
    return stats_summary

if __name__ == "__main__":
    preprocess_pipeline()
