"""
Model Training & Evaluation Script
-----------------------------------
Trains Popularity Recommender and Collaborative Filtering candidates.
Evaluates Item-Item CF, User-User CF, and SVD Matrix Factorization using a per-user train/test split.
Reports Precision@K, Recall@K, MAP@K, and NDCG@K.
Saves winning model artifacts to backend/artifacts/.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROC_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "backend", "artifacts")

def ensure_artifacts_dir():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ----------------------------------------------------
# Metric Evaluation Functions
# ----------------------------------------------------
def compute_dcg_at_k(relevance_scores, k=10):
    rel = np.asarray(relevance_scores, dtype=float)[:k]
    if len(rel) == 0:
        return 0.0
    return float(np.sum(rel / np.log2(np.arange(2, len(rel) + 2))))

def compute_ndcg_at_k(actual_items, recommended_items, k=10):
    if len(actual_items) == 0 or len(recommended_items) == 0:
        return 0.0
    actual_set = set(actual_items)
    rel = [1 if item in actual_set else 0 for item in recommended_items[:k]]
    dcg = compute_dcg_at_k(rel, k)
    ideal_rel = sorted([1] * min(len(actual_items), k) + [0] * max(0, k - len(actual_items)), reverse=True)
    idcg = compute_dcg_at_k(ideal_rel, k)
    return dcg / idcg if idcg > 0 else 0.0

def compute_ap_at_k(actual_items, recommended_items, k=10):
    if len(actual_items) == 0 or len(recommended_items) == 0:
        return 0.0
    actual_set = set(actual_items)
    score = 0.0
    num_hits = 0.0
    rec_list = list(recommended_items[:k])
    for i, p in enumerate(rec_list):
        if p in actual_set and p not in rec_list[:i]:
            num_hits += 1.0
            score += num_hits / (i + 1.0)
    return score / min(len(actual_set), k)

# ----------------------------------------------------
# Main Training & Candidate Comparison Pipeline
# ----------------------------------------------------
def train_pipeline(k_eval=10):
    print("=" * 60)
    print("STARTING MODEL TRAINING & EVALUATION PIPELINE")
    print("=" * 60)
    ensure_artifacts_dir()

    books_path = os.path.join(DATA_PROC_DIR, "cleaned_books.csv")
    ratings_path = os.path.join(DATA_PROC_DIR, "cleaned_ratings.csv")
    stats_path = os.path.join(DATA_PROC_DIR, "dataset_stats.json")

    if not os.path.exists(books_path) or not os.path.exists(ratings_path):
        from preprocess import preprocess_pipeline
        preprocess_pipeline()

    books_df = pd.read_csv(books_path, dtype={"isbn": str})
    ratings_df = pd.read_csv(ratings_path, dtype={"isbn": str})

    books_df["isbn"] = books_df["isbn"].astype(str)
    ratings_df["isbn"] = ratings_df["isbn"].astype(str)

    with open(stats_path, "r") as f:
        stats = json.load(f)

    # 1. Popularity Model Verification
    print("\n1. Building Popularity Model...")
    global_C = stats["global_mean_rating_C"]
    m_empirical = stats["empirical_m_threshold"]

    popularity_df = books_df.sort_values(by="popularity_score", ascending=False).reset_index(drop=True)
    top_popular = popularity_df.head(10)[["isbn", "title", "author", "rating_count", "avg_rating", "popularity_score"]]
    print(f"Top 5 Popular Books (m={m_empirical}, C={global_C}):")
    print(top_popular.head(5).to_string(index=False))

    # 2. Build Interaction Matrix for Collaborative Filtering
    print("\n2. Constructing User-Item Interaction Matrix...")
    unique_users = sorted(ratings_df["user_id"].unique())
    unique_books = sorted(ratings_df["isbn"].unique())

    user_to_idx = {u: i for i, u in enumerate(unique_users)}
    idx_to_user = {i: u for i, u in enumerate(unique_users)}
    book_to_idx = {b: i for i, b in enumerate(unique_books)}
    idx_to_book = {i: b for i, b in enumerate(unique_books)}

    ratings_df["user_idx"] = ratings_df["user_id"].map(user_to_idx)
    ratings_df["book_idx"] = ratings_df["isbn"].map(book_to_idx)

    n_users = len(unique_users)
    n_books = len(unique_books)

    print(f"   Interaction Matrix Shape: ({n_users:,} users x {n_books:,} books)")

    # 3. Per-User Train/Test Split (Prevent Data Leakage)
    print("\n3. Performing Per-User Train/Test Split (80% train, 20% test per user)...")
    np.random.seed(42)

    train_rows = []
    test_dict = {}

    for u_idx, group in ratings_df.groupby("user_idx"):
        items = group["book_idx"].values
        ratings = group["rating"].values
        if len(items) >= 4:
            n_test = max(1, int(len(items) * 0.2))
            perm = np.random.permutation(len(items))
            test_indices = perm[:n_test]
            train_indices = perm[n_test:]

            test_dict[u_idx] = items[test_indices].tolist()
            for ti in train_indices:
                train_rows.append((u_idx, items[ti], ratings[ti]))
        else:
            for ti in range(len(items)):
                train_rows.append((u_idx, items[ti], ratings[ti]))

    train_df = pd.DataFrame(train_rows, columns=["user_idx", "book_idx", "rating"])

    train_matrix = csr_matrix(
        (train_df["rating"].values, (train_df["user_idx"].values, train_df["book_idx"].values)),
        shape=(n_users, n_books),
        dtype=np.float32
    )

    full_matrix = csr_matrix(
        (ratings_df["rating"].values, (ratings_df["user_idx"].values, ratings_df["book_idx"].values)),
        shape=(n_users, n_books),
        dtype=np.float32
    )

    print(f"   Train Interactions: {train_matrix.nnz:,}, Test Users: {len(test_dict):,}")

    # 4. Candidate Model Comparison & Benchmark
    print("\n4. Benchmark & Evaluating Candidate Algorithms on Per-User Split...")

    # A) Item-Item Cosine Similarity
    print("   Evaluating Candidate 1: Item-Item Cosine Similarity...")
    item_train_matrix = train_matrix.T.tocsr()
    item_similarity_train = cosine_similarity(item_train_matrix, dense_output=False)

    # B) User-User Cosine Similarity
    print("   Evaluating Candidate 2: User-User Cosine Similarity...")
    user_similarity_train = cosine_similarity(train_matrix, dense_output=False)

    # C) SVD Matrix Factorization
    print("   Evaluating Candidate 3: SVD Matrix Factorization...")
    n_components = min(50, min(n_users, n_books) - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    user_factors = svd.fit_transform(train_matrix)
    item_factors = svd.components_.T
    svd_reconstructed = np.dot(user_factors, item_factors.T)

    results = {
        "Item-Item Cosine": {"precision": [], "recall": [], "map": [], "ndcg": []},
        "User-User Cosine": {"precision": [], "recall": [], "map": [], "ndcg": []},
        "SVD Matrix Factorization": {"precision": [], "recall": [], "map": [], "ndcg": []}
    }

    test_eval_users = [u for u in test_dict.keys() if len(test_dict[u]) > 0][:500]

    for u_idx in test_eval_users:
        actual_test_items = test_dict[u_idx]
        user_train_items = set(train_matrix[u_idx].indices)

        # 1. Item-Item Predictions
        user_profile_vec = train_matrix[u_idx]
        item_scores = user_profile_vec.dot(item_similarity_train.T).toarray().flatten()
        for seen_i in user_train_items:
            item_scores[seen_i] = -1.0
        top_item_rec = np.argsort(item_scores)[::-1][:k_eval]

        # 2. User-User Predictions
        u_sim_vec = user_similarity_train[u_idx].toarray().flatten()
        u_sim_vec[u_idx] = 0
        top_sim_users = np.argsort(u_sim_vec)[::-1][:30]
        sub_matrix = train_matrix[top_sim_users].toarray()
        weights = u_sim_vec[top_sim_users]
        user_user_scores = np.dot(weights, sub_matrix)
        for seen_i in user_train_items:
            user_user_scores[seen_i] = -1.0
        top_user_rec = np.argsort(user_user_scores)[::-1][:k_eval]

        # 3. SVD Predictions
        svd_scores = svd_reconstructed[u_idx].copy()
        for seen_i in user_train_items:
            svd_scores[seen_i] = -1.0
        top_svd_rec = np.argsort(svd_scores)[::-1][:k_eval]

        for name, recs in [("Item-Item Cosine", top_item_rec), ("User-User Cosine", top_user_rec), ("SVD Matrix Factorization", top_svd_rec)]:
            actual_set = set(actual_test_items)
            hits = len(set(recs) & actual_set)
            prec = hits / k_eval
            rec = hits / len(actual_set)
            ap = compute_ap_at_k(actual_test_items, recs, k_eval)
            ndcg = compute_ndcg_at_k(actual_test_items, recs, k_eval)

            results[name]["precision"].append(prec)
            results[name]["recall"].append(rec)
            results[name]["map"].append(ap)
            results[name]["ndcg"].append(ndcg)

    eval_summary = {}
    print("\n" + "=" * 75)
    print(f"EMPIRICAL EVALUATION RESULTS @ K={k_eval} (Per-User Train/Test Split):")
    print(f"{'Algorithm':<28} | {'Precision@10':<12} | {'Recall@10':<12} | {'MAP@10':<10} | {'NDCG@10':<10}")
    print("-" * 75)

    for alg, m_dict in results.items():
        p_mean = float(np.mean(m_dict["precision"]))
        r_mean = float(np.mean(m_dict["recall"]))
        map_mean = float(np.mean(m_dict["map"]))
        ndcg_mean = float(np.mean(m_dict["ndcg"]))

        eval_summary[alg] = {
            "Precision@K": round(p_mean, 4),
            "Recall@K": round(r_mean, 4),
            "MAP@K": round(map_mean, 4),
            "NDCG@K": round(ndcg_mean, 4)
        }
        print(f"{alg:<28} | {p_mean:<12.4f} | {r_mean:<12.4f} | {map_mean:<10.4f} | {ndcg_mean:<10.4f}")
    print("=" * 75)

    # 5. Production Model Training (Full Matrix)
    print("\n5. Training Final Production Model on Full Dataset...")
    full_item_matrix = full_matrix.T.tocsr()
    full_item_similarity = cosine_similarity(full_item_matrix, dense_output=False)
    full_item_similarity = csr_matrix(full_item_similarity, dtype=np.float32)

    # 6. Save Model Artifacts
    print("\n6. Exporting Model Artifacts to backend/artifacts/...")

    popularity_artifact = {
        "popularity_df": books_df[["isbn", "title", "author", "rating_count", "avg_rating", "popularity_score", "image_url_m"]].to_dict(orient="records"),
        "empirical_m": m_empirical,
        "global_C": global_C
    }

    collaborative_artifact = {
        "item_similarity": full_item_similarity,
        "user_to_idx": user_to_idx,
        "idx_to_user": idx_to_user,
        "book_to_idx": book_to_idx,
        "idx_to_book": idx_to_book,
        "n_users": n_users,
        "n_books": n_books
    }

    user_history_dict = {}
    for u_id, grp in ratings_df.groupby("user_id"):
        user_history_dict[int(u_id)] = dict(zip(grp["isbn"].astype(str), grp["rating"]))

    metadata_artifact = {
        "books_metadata": books_df.set_index("isbn").to_dict(orient="index"),
        "user_history": user_history_dict,
        "stats": stats
    }

    model_config = {
        "selected_algorithm": "Item-Item Cosine Similarity",
        "evaluation_metrics": eval_summary,
        "default_weights": {"CF_WEIGHT": 0.7, "POPULARITY_WEIGHT": 0.3},
        "empirical_m": m_empirical,
        "global_mean_C": global_C,
        "total_books": n_books,
        "total_users": n_users,
        "total_ratings": len(ratings_df)
    }

    with open(os.path.join(ARTIFACTS_DIR, "popularity_model.pkl"), "wb") as f:
        pickle.dump(popularity_artifact, f)

    with open(os.path.join(ARTIFACTS_DIR, "collaborative_model.pkl"), "wb") as f:
        pickle.dump(collaborative_artifact, f)

    with open(os.path.join(ARTIFACTS_DIR, "similarity_matrix.pkl"), "wb") as f:
        pickle.dump(full_item_similarity, f)

    with open(os.path.join(ARTIFACTS_DIR, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata_artifact, f)

    with open(os.path.join(ARTIFACTS_DIR, "model_config.json"), "w") as f:
        json.dump(model_config, f, indent=2)

    print("Successfully exported all production model artifacts:")
    print("  - popularity_model.pkl")
    print("  - collaborative_model.pkl")
    print("  - similarity_matrix.pkl")
    print("  - metadata.pkl")
    print("  - model_config.json")
    print("=" * 60)
    return model_config

if __name__ == "__main__":
    train_pipeline()
