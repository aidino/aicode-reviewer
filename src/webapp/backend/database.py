"""
Database configuration and session management.

This module sets up the database connection, session factory, and provides
utilities for database operations in the AI Code Reviewer system.
"""

import os
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pydantic_settings import BaseSettings
from functools import lru_cache

from .models.auth_models import Base


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # Database connection settings from environment variables
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "aicode"
    postgres_password: str = "aicode123"
    postgres_db: str = "aicode_reviewer"
    
    database_echo: bool = False  # Set to True for SQL query logging
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 3600  # 1 hour
    
    # Test database settings
    test_database_url: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Build database URL from components."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings."""
    return DatabaseSettings()


class DatabaseManager:
    """
    Database manager for handling connections and sessions.
    
    This class provides a centralized way to manage database connections,
    sessions, and provides utilities for database operations.
    """
    
    def __init__(self, settings: Optional[DatabaseSettings] = None):
        """
        Initialize database manager.
        
        Args:
            settings: Database settings. If None, will use default settings.
        """
        self.settings = settings or get_database_settings()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            # Determine which database URL to use
            database_url = self.settings.database_url
            
            # Override with test database URL if in test environment
            if (os.getenv("TESTING") == "1" or "pytest" in os.getenv("_", "")) and self.settings.test_database_url:
                database_url = self.settings.test_database_url
            
            # Create engine with connection pooling
            connect_args = {}
            
            # Special handling for SQLite (for testing)
            if database_url.startswith("sqlite"):
                connect_args = {
                    "check_same_thread": False,
                }
                self._engine = create_engine(
                    database_url,
                    echo=self.settings.database_echo,
                    poolclass=StaticPool,
                    connect_args=connect_args
                )
            else:
                # PostgreSQL configuration
                self._engine = create_engine(
                    database_url,
                    echo=self.settings.database_echo,
                    pool_size=self.settings.pool_size,
                    max_overflow=self.settings.max_overflow,
                    pool_pre_ping=self.settings.pool_pre_ping,
                    pool_recycle=self.settings.pool_recycle,
                )
        
        return self._engine
    
    @property 
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory
    
    def get_session(self) -> Session:
        """
        Create a new database session.
        
        Returns:
            SQLAlchemy Session instance.
        """
        return self.session_factory()
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        
        This context manager automatically handles commit/rollback and
        ensures the session is properly closed.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all database tables. USE WITH CAUTION!"""
        Base.metadata.drop_all(bind=self.engine)
    
    def close(self) -> None:
        """Close database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    This function is meant to be used with FastAPI's dependency injection.
    It provides a database session that is automatically closed after use.
    
    Yields:
        SQLAlchemy Session instance.
    """
    db_manager = get_database_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    """
    Initialize database tables.
    
    This function creates all tables defined in the models.
    Call this during application startup.
    """
    db_manager = get_database_manager()
    db_manager.create_tables()


def close_database() -> None:
    """
    Close database connections.
    
    This function should be called during application shutdown
    to properly close all database connections.
    """
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None 