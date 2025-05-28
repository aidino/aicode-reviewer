"""
Unit tests for authentication utilities.

This module tests password hashing, JWT token creation/verification,
and user authentication utilities.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.webapp.backend.models.auth_models import Base, User, UserSession, UserRole
from src.webapp.backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
    create_user_tokens,
    get_current_user,
    blacklist_token,
    get_auth_settings,
    AuthSettings
)


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
def auth_settings():
    """Create test auth settings."""
    return AuthSettings(
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=30,
        jwt_refresh_token_expire_days=7
    )


class TestPasswordUtils:
    """Test cases for password utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are typically 60 characters
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_different_results(self):
        """Test that hashing the same password twice gives different results."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # bcrypt includes random salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTUtils:
    """Test cases for JWT utilities."""
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_create_access_token(self, mock_get_settings, auth_settings):
        """Test access token creation."""
        mock_get_settings.return_value = auth_settings
        
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token content
        payload = jwt.decode(
            token, 
            auth_settings.jwt_secret_key, 
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_create_refresh_token(self, mock_get_settings, auth_settings):
        """Test refresh token creation."""
        mock_get_settings.return_value = auth_settings
        
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token content
        payload = jwt.decode(
            token, 
            auth_settings.jwt_secret_key, 
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_create_token_with_custom_expiry(self, mock_get_settings, auth_settings):
        """Test token creation with custom expiry time."""
        mock_get_settings.return_value = auth_settings
        
        data = {"sub": "123"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)
        
        payload = jwt.decode(
            token, 
            auth_settings.jwt_secret_key, 
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        # Check that expiry is approximately 60 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_time = datetime.now(timezone.utc) + custom_delta
        
        # Allow 10 second tolerance
        assert abs((exp_time - expected_time).total_seconds()) < 10
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_decode_token_valid(self, mock_get_settings, auth_settings):
        """Test decoding a valid token."""
        mock_get_settings.return_value = auth_settings
        
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_decode_token_invalid(self, mock_get_settings, auth_settings):
        """Test decoding an invalid token."""
        mock_get_settings.return_value = auth_settings
        
        invalid_token = "invalid.token.string"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_decode_token_expired(self, mock_get_settings, auth_settings):
        """Test decoding an expired token."""
        mock_get_settings.return_value = auth_settings
        
        # Create token that expires immediately
        data = {"sub": "123"}
        past_time = datetime.now(timezone.utc) - timedelta(seconds=1)
        expired_delta = past_time - datetime.now(timezone.utc)
        
        token = create_access_token(data, expires_delta=expired_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_generate_jti(self):
        """Test JWT ID generation."""
        jti1 = generate_jti()
        jti2 = generate_jti()
        
        assert isinstance(jti1, str)
        assert isinstance(jti2, str)
        assert len(jti1) == 36  # UUID4 format
        assert len(jti2) == 36
        assert jti1 != jti2  # Should be unique


class TestUserTokens:
    """Test cases for user token management."""
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_create_user_tokens_without_db(self, mock_get_settings, sample_user, auth_settings):
        """Test creating user tokens without database storage."""
        mock_get_settings.return_value = auth_settings
        
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="Test Browser",
            ip_address="127.0.0.1"
        )
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Verify token contents
        access_payload = jwt.decode(
            tokens["access_token"],
            auth_settings.jwt_secret_key,
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        refresh_payload = jwt.decode(
            tokens["refresh_token"],
            auth_settings.jwt_secret_key,
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        assert access_payload["sub"] == str(sample_user.id)
        assert access_payload["username"] == sample_user.username
        assert access_payload["email"] == sample_user.email
        assert access_payload["role"] == sample_user.role
        assert access_payload["type"] == "access"
        
        assert refresh_payload["sub"] == str(sample_user.id)
        assert refresh_payload["type"] == "refresh"
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_create_user_tokens_with_db(self, mock_get_settings, sample_user, db_session, auth_settings):
        """Test creating user tokens with database storage."""
        mock_get_settings.return_value = auth_settings
        
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="Test Browser",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        # Check that sessions were created in database
        sessions = db_session.query(UserSession).filter(
            UserSession.user_id == sample_user.id
        ).all()
        
        assert len(sessions) == 2  # access and refresh tokens
        
        # Check session details
        access_session = next(s for s in sessions if s.token_type == "access")
        refresh_session = next(s for s in sessions if s.token_type == "refresh")
        
        assert access_session.user_agent == "Test Browser"
        assert access_session.ip_address == "127.0.0.1"
        assert access_session.is_active is True
        assert access_session.is_blacklisted is False
        
        assert refresh_session.user_agent == "Test Browser"
        assert refresh_session.ip_address == "127.0.0.1"
        assert refresh_session.is_active is True
        assert refresh_session.is_blacklisted is False


class TestGetCurrentUser:
    """Test cases for getting current user from token."""
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_get_current_user_valid_token(self, mock_get_settings, sample_user, db_session, auth_settings):
        """Test getting current user with valid token."""
        mock_get_settings.return_value = auth_settings
        
        # Create tokens and sessions
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="Test Browser",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        # Mock HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=tokens["access_token"]
        )
        
        # Get current user
        current_user = get_current_user(credentials=credentials, db=db_session)
        
        assert current_user.id == sample_user.id
        assert current_user.username == sample_user.username
        assert current_user.email == sample_user.email
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_get_current_user_invalid_token(self, mock_get_settings, db_session, auth_settings):
        """Test getting current user with invalid token."""
        mock_get_settings.return_value = auth_settings
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.string"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=credentials, db=db_session)
        
        assert exc_info.value.status_code == 401
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_get_current_user_blacklisted_token(self, mock_get_settings, sample_user, db_session, auth_settings):
        """Test getting current user with blacklisted token."""
        mock_get_settings.return_value = auth_settings
        
        # Create tokens and sessions
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="Test Browser",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        # Blacklist the access token
        access_payload = jwt.decode(
            tokens["access_token"],
            auth_settings.jwt_secret_key,
            algorithms=[auth_settings.jwt_algorithm]
        )
        
        session = db_session.query(UserSession).filter(
            UserSession.jti == access_payload["jti"]
        ).first()
        session.blacklist()
        db_session.commit()
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=tokens["access_token"]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=credentials, db=db_session)
        
        assert exc_info.value.status_code == 401
        assert "invalid or expired" in exc_info.value.detail.lower()
    
    @patch('src.webapp.backend.auth.utils.get_auth_settings')
    def test_get_current_user_refresh_token_type(self, mock_get_settings, sample_user, db_session, auth_settings):
        """Test getting current user with refresh token (should fail)."""
        mock_get_settings.return_value = auth_settings
        
        # Create tokens and sessions
        tokens = create_user_tokens(
            user=sample_user,
            user_agent="Test Browser",
            ip_address="127.0.0.1",
            db=db_session
        )
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=tokens["refresh_token"]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=credentials, db=db_session)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail


class TestBlacklistToken:
    """Test cases for token blacklisting."""
    
    def test_blacklist_token_exists(self, sample_user, db_session):
        """Test blacklisting an existing token."""
        # Create a session
        now = datetime.now(timezone.utc)
        session = UserSession(
            user_id=sample_user.id,
            jti="test-jti-123",
            token_type="access",
            issued_at=now,
            expires_at=now + timedelta(hours=1)
        )
        db_session.add(session)
        db_session.commit()
        
        # Blacklist the token
        result = blacklist_token("test-jti-123", db_session)
        
        assert result is True
        
        # Check that session is blacklisted
        db_session.refresh(session)
        assert session.is_blacklisted is True
        assert session.is_active is False
        assert session.blacklisted_at is not None
    
    def test_blacklist_token_not_exists(self, db_session):
        """Test blacklisting a non-existent token."""
        result = blacklist_token("non-existent-jti", db_session)
        
        assert result is False


class TestAuthSettings:
    """Test cases for auth settings."""
    
    def test_auth_settings_defaults(self):
        """Test default auth settings values."""
        settings = AuthSettings()
        
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_access_token_expire_minutes == 30
        assert settings.jwt_refresh_token_expire_days == 7
        assert "bcrypt" in settings.pwd_schemes
        assert settings.pwd_deprecated == "auto"
    
    def test_auth_settings_custom_values(self):
        """Test auth settings with custom values."""
        settings = AuthSettings(
            jwt_secret_key="custom-secret",
            jwt_access_token_expire_minutes=60,
            jwt_refresh_token_expire_days=14
        )
        
        assert settings.jwt_secret_key == "custom-secret"
        assert settings.jwt_access_token_expire_minutes == 60
        assert settings.jwt_refresh_token_expire_days == 14 