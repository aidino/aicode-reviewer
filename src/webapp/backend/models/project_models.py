from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .auth_models import Base, User

class Project(Base):
    """
    ORM model cho repository/project, lưu metadata và liên kết với User (owner).
    Enhanced with smart caching and token management.
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    default_branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stars: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    forks: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 🆕 Smart Cache Management Fields
    cached_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Local cache directory path")
    last_commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, comment="Last known git commit hash")
    cache_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cache expiration time")
    cache_size_mb: Mapped[Optional[int]] = mapped_column(Integer, default=0, comment="Cache size in MB")
    auto_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Enable automatic git sync")
    
    # 🔐 Secure Token Management Fields  
    encrypted_access_token: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, comment="Encrypted PAT token")
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Token expiration time")
    token_last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Last time token was used")

    owner: Mapped["User"] = relationship("User", backref="projects")

    def __repr__(self) -> str:
        cache_status = "cached" if self.cached_path else "no-cache"
        token_status = "token" if self.encrypted_access_token else "no-token"
        return f"<Project(id={self.id}, name='{self.name}', {cache_status}, {token_status})>"
    
    @property
    def is_cache_valid(self) -> bool:
        """Check if current cache is still valid"""
        import os
        return (
            self.cached_path is not None and
            os.path.exists(self.cached_path) and
            self.cache_expires_at is not None and
            self.cache_expires_at > datetime.now(timezone.utc)
        )
    
    @property
    def is_token_valid(self) -> bool:
        """Check if stored token is still valid"""
        return (
            self.encrypted_access_token is not None and
            (self.token_expires_at is None or self.token_expires_at > datetime.now(timezone.utc))
        ) 