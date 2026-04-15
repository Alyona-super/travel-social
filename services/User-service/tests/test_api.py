import pytest

from fastapi.testclient import TestClient
# from main import app
# from database import Base, engine, get_db
from ..main import app
from ..database import Base, engine, get_db

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "profile-service"}


def test_register_user():
    user_data = {
        "email": "test@example.com",
        "password": "test123",
        "full_name": "Test User",
        "favorite_categories": ["travel", "food"]
    }

    response = client.post("/api/v1/profile/register", json=user_data)

    if response.status_code == 201:
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data