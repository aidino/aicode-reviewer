"""
Authentication models for the AI Code Reviewer system.

This module defines the database models for user authentication, profiles,
and session management using SQLAlchemy ORM with PostgreSQL support.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, 
    ForeignKey, Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class UserRole(str, Enum):
    """Enumeration for user roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """
    User model for authentication and authorization.
    
    This model stores core user information including credentials,
    status, and role-based access control.
    """
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False,
        doc="Unique username for login"
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False,
        doc="User email address"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Bcrypt hashed password"
    )
    
    # User status and role
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        doc="Whether the user account is active"
    )
    role: Mapped[UserRole] = mapped_column(
        String(20), default=UserRole.USER, nullable=False,
        doc="User role for authorization"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        nullable=False, doc="When the user was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False, doc="When the user was last updated"
    )
    
    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False,
        cascade="all, delete-orphan"
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Constraints and indexes
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_username_active", "username", "is_active"),
        Index("idx_users_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserProfile(Base):
    """
    User profile model for extended user information.
    
    This model stores additional user information like display name,
    avatar, timezone, and user preferences.
    """
    __tablename__ = "user_profiles"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False,
        doc="Reference to the user"
    )
    
    # Profile information
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        doc="User's full display name"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        doc="URL to user's avatar image"
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC", nullable=False,
        doc="User's timezone (e.g., 'Asia/Ho_Chi_Minh')"
    )
    
    # User preferences stored as JSON
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="User preferences as JSON (theme, notifications, etc.)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        nullable=False, doc="When the profile was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False, doc="When the profile was last updated"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    # Constraints and indexes
    __table_args__ = (
        Index("idx_user_profiles_user_id", "user_id"),
        Index("idx_user_profiles_full_name", "full_name"),
    )
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, full_name='{self.full_name}')>"


class UserSession(Base):
    """
    User session model for token blacklisting and session management.
    
    This model tracks active user sessions and provides mechanism
    for token blacklisting and session invalidation.
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
        doc="Reference to the user"
    )
    
    # Session identification
    jti: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True,
        doc="JWT ID (unique identifier for the token)"
    )
    token_type: Mapped[str] = mapped_column(
        String(20), default="access", nullable=False,
        doc="Type of token (access, refresh)"
    )
    
    # Session metadata
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="User agent string from the client"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True,
        doc="IP address of the client (supports IPv6)"
    )
    
    # Session status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        doc="Whether the session is active"
    )
    is_blacklisted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Whether the token is blacklisted"
    )
    
    # Timestamps
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        doc="When the token was issued"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        doc="When the token expires"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="When the token was last used"
    )
    blacklisted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="When the token was blacklisted"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        nullable=False, doc="When the session record was created"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    
    # Constraints and indexes
    __table_args__ = (
        Index("idx_user_sessions_user_id_active", "user_id", "is_active"),
        Index("idx_user_sessions_jti_active", "jti", "is_active"),
        Index("idx_user_sessions_expires_at", "expires_at"),
        Index("idx_user_sessions_blacklisted", "is_blacklisted", "blacklisted_at"),
        Index("idx_user_sessions_token_type", "token_type"),
        UniqueConstraint("jti", name="uq_user_sessions_jti"),
    )
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, jti='{self.jti[:8]}...', active={self.is_active})>"

    def is_expired(self) -> bool:
        """Check if the session/token is expired."""
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at
        
        # Handle timezone-naive datetime (SQLite compatibility)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return now > expires_at

    def is_valid(self) -> bool:
        """Check if the session is valid (active, not blacklisted, not expired)."""
        return (
            self.is_active and 
            not self.is_blacklisted and 
            not self.is_expired()
        )

    def blacklist(self) -> None:
        """Blacklist this session/token."""
        self.is_blacklisted = True
        self.is_active = False
        self.blacklisted_at = datetime.now(timezone.utc)

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used_at = datetime.now(timezone.utc) 