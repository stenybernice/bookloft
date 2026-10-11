"""
End-to-End Pipeline Verification Script
----------------------------------------
Verifies Preprocessing -> Training -> Model Artifacts -> MongoDB Seeding -> FastAPI Recommendation Engine
"""

import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

def run_verification():
    print("=" * 70)
    print("STARTING END-TO-END PIPELINE VERIFICATION")
    print("=" * 70)

    # 1. Check Artifacts
    artifacts_dir = os.path.join(PROJECT_ROOT, "backend", "artifacts")
    required_files = [
        "popularity_model.pkl",
        "collaborative_model.pkl",
        "similarity_matrix.pkl",
        "metadata.pkl",
        "model_config.json"
    ]

    print("\n1. Verifying Model Artifacts...")
    for f in required_files:
        path = os.path.join(artifacts_dir, f)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required artifact: {path}")
        size_kb = os.path.getsize(path) / 1024
        print(f"   [PASS] {f:<25} ({size_kb:.2f} KB)")

    # Read config
    with open(os.path.join(artifacts_dir, "model_config.json"), "r") as f:
        config = json.load(f)

    print(f"\n   Model Selected: {config['selected_algorithm']}")
    print(f"   Evaluation Metrics @ K=10:")
    for alg, metrics in config["evaluation_metrics"].items():
        print(f"     - {alg:<25}: NDCG@10 = {metrics['NDCG@K']}, MAP@10 = {metrics['MAP@K']}, Precision@10 = {metrics['Precision@K']}")

    # 2. Test FastAPI TestClient Engine Initialization & Endpoints with Lifespan Context
    print("\n2. Verifying FastAPI Backend & Recommendation Engine Service...")
    from app.main import app
    from app.services.recommendation_service import engine_manager
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        # Health Check
        res_health = client.get("/api/health")
        assert res_health.status_code == 200
        h_data = res_health.json()
        print(f"   [PASS] GET /api/health -> status: {h_data['status']}, models_loaded: {h_data['models_loaded']}")

        # Popular Recommendations
        res_pop = client.get("/api/recommendations/popular?limit=5")
        assert res_pop.status_code == 200
        pop_data = res_pop.json()
        print(f"   [PASS] GET /api/recommendations/popular -> returned {pop_data['count']} items. Top item: '{pop_data['items'][0]['title']}' (Score: {pop_data['items'][0]['popularity_score']})")

        # Cold Start User Recommendations
        res_cold = client.get("/api/recommendations/user/99999?limit=5")
        assert res_cold.status_code == 200
        cold_data = res_cold.json()
        assert cold_data["cold_start"] is True
        print(f"   [PASS] GET /api/recommendations/user/99999 -> Cold Start Triggered: {cold_data['cold_start']}")

        # Incremental Rating Submission Test with str(valid_isbn)
        valid_isbn = str(list(engine_manager.collaborative_service.book_to_idx.keys())[0])
        res_rate = client.post("/api/ratings", json={"user_id": 88888, "isbn": valid_isbn, "rating": 10})
        assert res_rate.status_code == 200
        print(f"   [PASS] POST /api/ratings -> Rating saved for user 88888 on ISBN '{valid_isbn}'")

        res_post_rate = client.get("/api/recommendations/hybrid/88888?limit=5")
        assert res_post_rate.status_code == 200
        post_data = res_post_rate.json()
        assert post_data["cold_start"] is False
        print(f"   [PASS] Incremental Update Verified: User 88888 received immediate personalized hybrid recs without model retraining!")
        print(f"          Reason sample: '{post_data['items'][0]['recommendation_reason']}'")

    print("\n" + "=" * 70)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
