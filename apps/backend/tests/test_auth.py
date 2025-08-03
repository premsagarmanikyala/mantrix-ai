"""
Tests for authentication functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import get_db
from services.auth_service import AuthService

# Test database URL - using SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test_auth.db"


@pytest.fixture
def test_db():
    """Create test database and session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    
    def override_get_db():
        try:
            db = TestSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestSessionLocal()
    
    # Clean up
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.commit()
    
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_signup_success(client: TestClient, test_db):
    """Test successful user signup."""
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/signup", json=signup_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == signup_data["email"]
    assert "user_id" in data
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_signup_duplicate_email(client: TestClient, test_db):
    """Test signup with duplicate email."""
    signup_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123"
    }
    
    # First signup should succeed
    response1 = client.post("/api/auth/signup", json=signup_data)
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post("/api/auth/signup", json=signup_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


def test_signup_invalid_password(client: TestClient, test_db):
    """Test signup with invalid password."""
    signup_data = {
        "email": "test@example.com",
        "password": "short"  # Less than 6 characters
    }
    
    response = client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 422  # Validation error


def test_login_success(client: TestClient, test_db):
    """Test successful user login."""
    # First create a user
    signup_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    client.post("/api/auth/signup", json=signup_data)
    
    # Then try to login
    login_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == login_data["email"]
    assert "user_id" in data
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_invalid_email(client: TestClient, test_db):
    """Test login with non-existent email."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password(client: TestClient, test_db):
    """Test login with wrong password."""
    # First create a user
    signup_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword"
    }
    client.post("/api/auth/signup", json=signup_data)
    
    # Try to login with wrong password
    login_data = {
        "email": "wrongpass@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_success(client: TestClient, test_db):
    """Test getting current user info with valid token."""
    # Signup and get token
    signup_data = {
        "email": "currentuser@example.com",
        "password": "testpassword123"
    }
    signup_response = client.post("/api/auth/signup", json=signup_data)
    token = signup_response.json()["access_token"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == signup_data["email"]
    assert "user_id" in data


def test_get_current_user_no_token(client: TestClient, test_db):
    """Test getting current user info without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # Forbidden (no token)


def test_get_current_user_invalid_token(client: TestClient, test_db):
    """Test getting current user info with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401  # Unauthorized


def test_auth_health_check(client: TestClient):
    """Test authentication health check endpoint."""
    response = client.get("/api/auth/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "authentication"
    assert data["jwt_enabled"] == True


def test_password_hashing():
    """Test password hashing functionality."""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    
    # Hash should be different from original password
    assert hashed != password
    assert len(hashed) > 0
    
    # Should be able to verify the password
    assert AuthService.verify_password(password, hashed) == True
    
    # Wrong password should not verify
    assert AuthService.verify_password("wrongpassword", hashed) == False


def test_jwt_token_creation_and_validation():
    """Test JWT token creation and validation."""
    user_id = "test_user_123"
    email = "test@example.com"
    
    # Create token
    token = AuthService.create_access_token(user_id, email)
    assert len(token) > 0
    
    # Decode and validate token
    payload = AuthService.decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert "exp" in payload
    assert "iat" in payload
    
    # Invalid token should return None
    invalid_payload = AuthService.decode_access_token("invalid_token")
    assert invalid_payload is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])