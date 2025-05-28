"""
Unit tests for authentication models.

This module tests the User, UserProfile, and UserSession models
including their relationships, validation, and business logic.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.webapp.backend.models.auth_models import Base, User, UserProfile, UserSession, UserRole


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
        password_hash="hashed_password_123",
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_profile(db_session, sample_user):
    """Create a sample user profile for testing."""
    profile = UserProfile(
        user_id=sample_user.id,
        full_name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        timezone="Asia/Ho_Chi_Minh",
        preferences={"theme": "dark", "notifications": True}
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def sample_user_session(db_session, sample_user):
    """Create a sample user session for testing."""
    now = datetime.now(timezone.utc)
    session = UserSession(
        user_id=sample_user.id,
        jti="test-jwt-id-123",
        token_type="access",
        user_agent="Mozilla/5.0 Test Browser",
        ip_address="192.168.1.1",
        issued_at=now,
        expires_at=now + timedelta(hours=1)
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


class TestUser:
    """Test cases for User model."""
    
    def test_user_creation(self, db_session):
        """Test creating a new user."""
        user = User(
            username="newuser",
            email="newuser@example.com",
            password_hash="hashed_password",
            role=UserRole.ADMIN
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.ADMIN
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_default_values(self, db_session):
        """Test user default values."""
        user = User(
            username="defaultuser",
            email="default@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is True
        assert user.role == UserRole.USER
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_unique_constraints(self, db_session, sample_user):
        """Test unique constraints on username and email."""
        # Test duplicate username
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            duplicate_username = User(
                username=sample_user.username,
                email="different@example.com",
                password_hash="hashed_password"
            )
            db_session.add(duplicate_username)
            db_session.commit()
        
        db_session.rollback()
        
        # Test duplicate email
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            duplicate_email = User(
                username="differentuser",
                email=sample_user.email,
                password_hash="hashed_password"
            )
            db_session.add(duplicate_email)
            db_session.commit()
    
    def test_user_repr(self, sample_user):
        """Test user string representation."""
        expected = f"<User(id={sample_user.id}, username='testuser', email='test@example.com')>"
        assert repr(sample_user) == expected


class TestUserProfile:
    """Test cases for UserProfile model."""
    
    def test_profile_creation(self, db_session, sample_user):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id=sample_user.id,
            full_name="John Doe",
            avatar_url="https://example.com/john.jpg",
            timezone="America/New_York",
            preferences={"language": "en", "theme": "light"}
        )
        
        db_session.add(profile)
        db_session.commit()
        
        assert profile.id is not None
        assert profile.user_id == sample_user.id
        assert profile.full_name == "John Doe"
        assert profile.avatar_url == "https://example.com/john.jpg"
        assert profile.timezone == "America/New_York"
        assert profile.preferences == {"language": "en", "theme": "light"}
        assert profile.created_at is not None
        assert profile.updated_at is not None
    
    def test_profile_default_timezone(self, db_session, sample_user):
        """Test default timezone value."""
        profile = UserProfile(user_id=sample_user.id)
        
        db_session.add(profile)
        db_session.commit()
        
        assert profile.timezone == "UTC"
    
    def test_profile_user_relationship(self, db_session, sample_user_profile):
        """Test relationship between profile and user."""
        assert sample_user_profile.user is not None
        assert sample_user_profile.user.username == "testuser"
        assert sample_user_profile.user.profile == sample_user_profile
    
    def test_profile_unique_user_constraint(self, db_session, sample_user, sample_user_profile):
        """Test unique constraint on user_id."""
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            duplicate_profile = UserProfile(
                user_id=sample_user.id,
                full_name="Duplicate Profile"
            )
            db_session.add(duplicate_profile)
            db_session.commit()
    
    def test_profile_cascade_delete(self, db_session, sample_user, sample_user_profile):
        """Test cascade delete when user is deleted."""
        profile_id = sample_user_profile.id
        
        # Delete user
        db_session.delete(sample_user)
        db_session.commit()
        
        # Profile should be deleted too
        deleted_profile = db_session.get(UserProfile, profile_id)
        assert deleted_profile is None
    
    def test_profile_repr(self, sample_user_profile):
        """Test profile string representation."""
        expected = f"<UserProfile(id={sample_user_profile.id}, user_id={sample_user_profile.user_id}, full_name='Test User')>"
        assert repr(sample_user_profile) == expected


class TestUserSession:
    """Test cases for UserSession model."""
    
    def test_session_creation(self, db_session, sample_user):
        """Test creating a user session."""
        now = datetime.now(timezone.utc)
        session = UserSession(
            user_id=sample_user.id,
            jti="unique-jwt-id",
            token_type="refresh",
            user_agent="Chrome/91.0",
            ip_address="10.0.0.1",
            issued_at=now,
            expires_at=now + timedelta(days=7)
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.jti == "unique-jwt-id"
        assert session.token_type == "refresh"
        assert session.user_agent == "Chrome/91.0"
        assert session.ip_address == "10.0.0.1"
        assert session.is_active is True
        assert session.is_blacklisted is False
        # Compare timestamps without timezone info since SQLite doesn't preserve timezone
        assert session.issued_at.replace(tzinfo=None) == now.replace(tzinfo=None)
        assert session.expires_at.replace(tzinfo=None) == (now + timedelta(days=7)).replace(tzinfo=None)
        assert session.created_at is not None
    
    def test_session_default_values(self, db_session, sample_user):
        """Test session default values."""
        now = datetime.now(timezone.utc)
        session = UserSession(
            user_id=sample_user.id,
            jti="default-test-jti",
            issued_at=now,
            expires_at=now + timedelta(hours=1)
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.token_type == "access"
        assert session.is_active is True
        assert session.is_blacklisted is False
    
    def test_session_user_relationship(self, db_session, sample_user_session):
        """Test relationship between session and user."""
        assert sample_user_session.user is not None
        assert sample_user_session.user.username == "testuser"
        assert sample_user_session in sample_user_session.user.sessions
    
    def test_session_unique_jti_constraint(self, db_session, sample_user, sample_user_session):
        """Test unique constraint on jti."""
        now = datetime.now(timezone.utc)
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            duplicate_jti = UserSession(
                user_id=sample_user.id,
                jti=sample_user_session.jti,  # Same JTI
                issued_at=now,
                expires_at=now + timedelta(hours=1)
            )
            db_session.add(duplicate_jti)
            db_session.commit()
    
    def test_session_cascade_delete(self, db_session, sample_user, sample_user_session):
        """Test cascade delete when user is deleted."""
        session_id = sample_user_session.id
        
        # Delete user
        db_session.delete(sample_user)
        db_session.commit()
        
        # Session should be deleted too
        deleted_session = db_session.get(UserSession, session_id)
        assert deleted_session is None
    
    def test_session_is_expired(self, db_session, sample_user):
        """Test is_expired method."""
        now = datetime.now(timezone.utc)
        
        # Expired session
        expired_session = UserSession(
            user_id=sample_user.id,
            jti="expired-jti",
            issued_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1)
        )
        
        # Valid session
        valid_session = UserSession(
            user_id=sample_user.id,
            jti="valid-jti",
            issued_at=now,
            expires_at=now + timedelta(hours=1)
        )
        
        assert expired_session.is_expired() is True
        assert valid_session.is_expired() is False
    
    def test_session_is_valid(self, db_session, sample_user):
        """Test is_valid method."""
        now = datetime.now(timezone.utc)
        
        # Valid session
        valid_session = UserSession(
            user_id=sample_user.id,
            jti="valid-session-jti",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            is_active=True,
            is_blacklisted=False
        )
        
        # Blacklisted session
        blacklisted_session = UserSession(
            user_id=sample_user.id,
            jti="blacklisted-jti",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            is_active=True,
            is_blacklisted=True
        )
        
        # Inactive session
        inactive_session = UserSession(
            user_id=sample_user.id,
            jti="inactive-jti",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            is_active=False,
            is_blacklisted=False
        )
        
        # Expired session
        expired_session = UserSession(
            user_id=sample_user.id,
            jti="expired-valid-jti",
            issued_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            is_active=True,
            is_blacklisted=False
        )
        
        assert valid_session.is_valid() is True
        assert blacklisted_session.is_valid() is False
        assert inactive_session.is_valid() is False
        assert expired_session.is_valid() is False
    
    def test_session_blacklist(self, db_session, sample_user_session):
        """Test blacklist method."""
        assert sample_user_session.is_blacklisted is False
        assert sample_user_session.is_active is True
        assert sample_user_session.blacklisted_at is None
        
        sample_user_session.blacklist()
        
        assert sample_user_session.is_blacklisted is True
        assert sample_user_session.is_active is False
        assert sample_user_session.blacklisted_at is not None
        assert sample_user_session.is_valid() is False
    
    def test_session_update_last_used(self, db_session, sample_user_session):
        """Test update_last_used method."""
        assert sample_user_session.last_used_at is None
        
        sample_user_session.update_last_used()
        
        assert sample_user_session.last_used_at is not None
        assert isinstance(sample_user_session.last_used_at, datetime)
    
    def test_session_repr(self, sample_user_session):
        """Test session string representation."""
        jti_short = sample_user_session.jti[:8]
        expected = f"<UserSession(id={sample_user_session.id}, user_id={sample_user_session.user_id}, jti='{jti_short}...', active={sample_user_session.is_active})>"
        assert repr(sample_user_session) == expected


class TestUserRole:
    """Test cases for UserRole enum."""
    
    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.GUEST == "guest"
    
    def test_user_role_assignment(self, db_session):
        """Test assigning different roles to users."""
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash="hashed_password",
            role=UserRole.ADMIN
        )
        
        guest_user = User(
            username="guest",
            email="guest@example.com",
            password_hash="hashed_password",
            role=UserRole.GUEST
        )
        
        db_session.add_all([admin_user, guest_user])
        db_session.commit()
        
        assert admin_user.role == UserRole.ADMIN
        assert guest_user.role == UserRole.GUEST 