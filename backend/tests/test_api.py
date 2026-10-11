"""
Backend API Unit & Integration Tests
------------------------------------
Tests health endpoint, popular recommendations, collaborative recommendations,
cold start fallback, hybrid recommendations, book search, and rating submission.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.main import app
from app.services.recommendation_service import engine_manager

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] is True
    assert "selected_algorithm" in data

def test_popular_recommendations(client):
    response = client.get("/api/recommendations/popular?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "popularity"
    assert len(data["items"]) == 5
    first_item = data["items"][0]
    assert "isbn" in first_item
    assert "popularity_score" in first_item
    assert first_item["popularity_score"] > 0

def test_cold_start_user_recommendations(client):
    response = client.get("/api/recommendations/user/99999?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["cold_start"] is True
    assert len(data["items"]) == 5
    assert "Popular with readers" in data["items"][0]["recommendation_reason"]
    assert "cold-start" not in data["items"][0]["recommendation_reason"].lower()

def test_existing_user_hybrid_recommendations(client):
    demo_resp = client.get("/api/users/demo")
    assert demo_resp.status_code == 200
    demo_users = demo_resp.json()
    active_user = next((u for u in demo_users if u["rating_count"] > 0), None)

    if active_user:
        u_id = active_user["user_id"]
        response = client.get(f"/api/recommendations/hybrid/{u_id}?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["cold_start"] is False
        assert "weights_used" in data

def test_book_search(client):
    response = client.get("/api/books/search?q=the&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_rating_submission_incremental(client):
    valid_isbn = str(list(engine_manager.collaborative_service.book_to_idx.keys())[0])
    payload = {
        "user_id": 99999,
        "isbn": valid_isbn,
        "rating": 9
    }
    response = client.post("/api/ratings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user_total_ratings"] >= 1

    rec_resp = client.get("/api/recommendations/hybrid/99999?limit=5")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["cold_start"] is False
    assert len(rec_data["items"]) == 5
