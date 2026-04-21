import sys
import os

# добавляем текущую папку
current_dir = os.path.dirname(os.path.abspath(__file__))  # папка tests
parent_dir = os.path.dirname(current_dir)  # папка user_service

print(f"Parent dir: {parent_dir}")  # Посмотрим, какой путь
print(f"Files in parent dir: {os.listdir(parent_dir)}")  # Проверим, есть ли main.py

sys.path.insert(0, parent_dir)

from fastapi.testclient import TestClient

# Пробуем импортировать
try:
    from main import app

    print("Import successful!")
except ImportError as e:
    print(f"Import error: {e}")
    # Покажем, что есть в sys.path
    print("sys.path:", sys.path[:5])


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
        "favorite_categories": ["travel", "food"],
    }

    response = client.post("/api/v1/profile/register", json=user_data)

    if response.status_code == 201:
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
