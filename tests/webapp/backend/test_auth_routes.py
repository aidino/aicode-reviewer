"""
Unit tests for authentication API routes.

This module tests the FastAPI authentication endpoints including
registration, login, logout, profile management, and token operations.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.webapp.backend.models.auth_models import Base, User, UserProfile, UserSession, UserRole
from src.webapp.backend.auth.routes import router as auth_router
from src.webapp.backend.auth.utils import hash_password, create_user_tokens
from src.webapp.backend.database import get_db_session


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    app = FastAPI()
    app.include_router(auth_router)
    return app


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(app, db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    return TestClient(app)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_with_profile(db_session):
    """Create a sample user with profile for testing."""
    user = User(
        username="profileuser",
        email="profile@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    profile = UserProfile(
        user_id=user.id,
        full_name="Profile User",
        timezone="Asia/Ho_Chi_Minh",
        preferences={"theme": "dark"}
    )
    db_session.add(profile)
    db_session.commit()
    
    return user


@pytest.fixture
def auth_headers(sample_user, db_session):
    """Create authorization headers for testing."""
    # Patch authentication settings for consistent testing
    with patch('src.webapp.backend.auth.utils.get_auth_settings') as mock_utils_settings, \
         patch('src.webapp.backend.auth.routes.get_auth_settings') as mock_routes_settings, \
         patch('src.webapp.backend.auth.service.get_auth_settings') as mock_service_settings:
        
        from src.webapp.backend.auth.utils import AuthSettings
        settings = AuthSettings(
            jwt_secret_key="test-secret-key",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=30,
            jwt_refresh_token_expire_days=7
        )
        
        # Configure all mocks
        mock_utils_settings.return_value = settings
        mock_routes_settings.return_value = settings
        mock_service_settings.return_value = settings
        
        # Create tokens with patched settings
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="TestAgent",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        yield {"Authorization": f"Bearer {tokens['access_token']}"}


class TestUserRegistration:
    """Test cases for user registration endpoint."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "full_name": "New User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_register_user_duplicate_username(self, client, sample_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": sample_user.username,
            "email": "different@example.com",
            "password": "NewPassword123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]
    
    def test_register_user_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email."""
        user_data = {
            "username": "differentuser",
            "email": sample_user.email,
            "password": "NewPassword123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        # Pydantic validation occurs first (422), then auth service validation (400)
        assert response.status_code in [400, 422]
        if response.status_code == 400:
            assert "Password does not meet strength requirements" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "username": "invaliduser",
            "email": "invalid-email",
            "password": "ValidPassword123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test cases for user login endpoint."""
    
    @patch('src.webapp.backend.auth.routes.get_auth_settings')
    @patch('src.webapp.backend.auth.utils.get_auth_settings')  
    @patch('src.webapp.backend.auth.service.get_auth_settings')
    def test_login_user_success_username(self, mock_settings_service, mock_settings_utils, mock_settings_routes, client, sample_user):
        """Test successful login with username."""
        from src.webapp.backend.auth.utils import AuthSettings
        settings = AuthSettings(
            jwt_secret_key="test-secret-key",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=30,
            jwt_refresh_token_expire_days=7
        )
        mock_settings_service.return_value = settings
        mock_settings_utils.return_value = settings
        mock_settings_routes.return_value = settings
        
        login_data = {
            "username_or_email": sample_user.username,
            "password": "TestPassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes in seconds
        assert data["user"]["username"] == sample_user.username
        assert data["user"]["email"] == sample_user.email
    
    @patch('src.webapp.backend.auth.routes.get_auth_settings')
    @patch('src.webapp.backend.auth.utils.get_auth_settings')  
    @patch('src.webapp.backend.auth.service.get_auth_settings')
    def test_login_user_success_email(self, mock_settings_service, mock_settings_utils, mock_settings_routes, client, sample_user):
        """Test successful login with email."""
        from src.webapp.backend.auth.utils import AuthSettings
        settings = AuthSettings(
            jwt_secret_key="test-secret-key",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=30,
            jwt_refresh_token_expire_days=7
        )
        mock_settings_service.return_value = settings
        mock_settings_utils.return_value = settings
        mock_settings_routes.return_value = settings
        
        login_data = {
            "username_or_email": sample_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == sample_user.username
    
    def test_login_user_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        login_data = {
            "username_or_email": sample_user.username,
            "password": "WrongPassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_user_nonexistent(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username_or_email": "nonexistent",
            "password": "TestPassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestUserLogout:
    """Test cases for user logout endpoint."""
    
    def test_logout_user_success(self, client, auth_headers):
        """Test successful user logout."""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Logged out successfully" in data["message"]
    
    def test_logout_user_invalid_token(self, client):
        """Test logout with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.string"}
        
        response = client.post("/auth/logout", headers=headers)
        
        # Logout is idempotent - returns 200 even for invalid tokens
        assert response.status_code == 200
        data = response.json()
        assert "already invalid" in data["message"]
    
    def test_logout_user_no_token(self, client):
        """Test logout without token."""
        response = client.post("/auth/logout")
        
        assert response.status_code == 403  # Missing token


class TestGetCurrentUser:
    """Test cases for getting current user endpoint."""
    
    def test_get_current_user_success(self, client, auth_headers, sample_user):
        """Test getting current user information."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
        assert data["role"] == sample_user.role
        assert data["profile"] is None  # No profile created
    
    def test_get_current_user_with_profile(self, client, sample_user_with_profile, db_session):
        """Test getting current user with profile."""
        with patch('src.webapp.backend.auth.utils.get_auth_settings') as mock_settings:
            from src.webapp.backend.auth.utils import AuthSettings
            mock_settings.return_value = AuthSettings(
                jwt_secret_key="test-secret-key",
                jwt_algorithm="HS256",
                jwt_access_token_expire_minutes=30,
                jwt_refresh_token_expire_days=7
            )
            
            tokens = create_user_tokens(
                user=sample_user_with_profile,
                user_agent="TestAgent",
                ip_address="127.0.0.1",
                db=db_session
            )
            
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            response = client.get("/auth/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == sample_user_with_profile.id
            assert data["profile"] is not None
            assert data["profile"]["full_name"] == "Profile User"
            assert data["profile"]["timezone"] == "Asia/Ho_Chi_Minh"
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.string"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 403


class TestUpdateProfile:
    """Test cases for updating user profile."""
    
    def test_update_profile_success(self, client, auth_headers):
        """Test successful profile update."""
        profile_data = {
            "full_name": "Updated Name",
            "timezone": "America/New_York",
            "preferences": {
                "theme": "light",
                "notifications": {"email": True}
            }
        }
        
        response = client.put("/auth/me", json=profile_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["timezone"] == "America/New_York"
        assert data["preferences"]["theme"] == "light"
    
    def test_update_profile_partial(self, client, auth_headers):
        """Test partial profile update."""
        profile_data = {
            "full_name": "Only Name Updated"
        }
        
        response = client.put("/auth/me", json=profile_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Only Name Updated"
        assert data["timezone"] == "UTC"  # Default value
    
    def test_update_profile_no_token(self, client):
        """Test profile update without token."""
        profile_data = {"full_name": "Test"}
        
        response = client.put("/auth/me", json=profile_data)
        
        assert response.status_code == 403


class TestChangePassword:
    """Test cases for changing password."""
    
    def test_change_password_success(self, client, auth_headers):
        """Test successful password change."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword456!"
        }
        
        response = client.post("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Password changed successfully" in data["message"]
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword456!"
        }
        
        response = client.post("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_change_password_weak_new(self, client, auth_headers):
        """Test password change with weak new password."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "weak"
        }
        
        response = client.post("/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "does not meet strength requirements" in response.json()["detail"]
    
    def test_change_password_no_token(self, client):
        """Test password change without token."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword456!"
        }
        
        response = client.post("/auth/change-password", json=password_data)
        
        assert response.status_code == 403


class TestTokenRefresh:
    """Test cases for token refresh."""
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_refresh_token_success(self, mock_settings, client, sample_user, db_session):
        """Test successful token refresh."""
        from src.webapp.backend.auth.utils import AuthSettings
        mock_settings.return_value = AuthSettings(
            jwt_secret_key="test-secret-key",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=30,
            jwt_refresh_token_expire_days=7
        )
        
        # Create tokens
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="TestAgent",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        
        # New tokens should be different from original
        assert data["access_token"] != tokens["access_token"]
        assert data["refresh_token"] != tokens["refresh_token"]
    
    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid.refresh.token"
        }
        
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401


class TestUserSessions:
    """Test cases for user session management."""
    
    def test_get_user_sessions(self, client, auth_headers):
        """Test getting user sessions."""
        response = client.get("/auth/sessions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2  # At least access and refresh tokens
        
        # Check session structure
        if data:
            session = data[0]
            assert "id" in session
            assert "user_id" in session
            assert "jti" in session
            assert "token_type" in session
            assert "is_active" in session
    
    def test_get_user_sessions_no_token(self, client):
        """Test getting user sessions without token."""
        response = client.get("/auth/sessions")
        
        assert response.status_code == 403
    
    def test_revoke_all_sessions(self, client, auth_headers):
        """Test revoking all user sessions except current."""
        response = client.delete("/auth/sessions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Revoked" in data["message"]
        assert "sessions successfully" in data["message"] 