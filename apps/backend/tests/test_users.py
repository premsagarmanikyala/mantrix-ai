"""
Tests for user API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import get_db, Base
from models.database import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "bio": "Test bio"
    }


def test_create_user(sample_user):
    """Test creating a new user."""
    response = client.post("/api/v1/users", json=sample_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user["email"]
    assert data["username"] == sample_user["username"]
    assert "id" in data


def test_get_users():
    """Test getting all users."""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_by_id():
    """Test getting a user by ID."""
    # First create a user
    user_data = {
        "email": "gettest@example.com",
        "username": "getuser",
        "full_name": "Get User",
        "bio": "Get test bio"
    }
    create_response = client.post("/api/v1/users", json=user_data)
    user_id = create_response.json()["id"]
    
    # Now get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_update_user():
    """Test updating a user."""
    # First create a user
    user_data = {
        "email": "update@example.com",
        "username": "updateuser",
        "full_name": "Update User",
        "bio": "Update test bio"
    }
    create_response = client.post("/api/v1/users", json=user_data)
    user_id = create_response.json()["id"]
    
    # Update the user
    update_data = {"full_name": "Updated Name"}
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_delete_user():
    """Test deleting a user."""
    # First create a user
    user_data = {
        "email": "delete@example.com",
        "username": "deleteuser", 
        "full_name": "Delete User",
        "bio": "Delete test bio"
    }
    create_response = client.post("/api/v1/users", json=user_data)
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404