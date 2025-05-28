"""
Authentication utilities for password hashing and JWT token management.

This module provides core authentication functions including password hashing,
JWT token creation/verification, and user extraction from tokens.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic_settings import BaseSettings
from functools import lru_cache

from ..database import get_db_session
from ..models.auth_models import User, UserSession


class AuthSettings(BaseSettings):
    """Authentication configuration settings."""
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Password settings
    pwd_schemes: list[str] = ["bcrypt"]
    pwd_deprecated: str = "auto"
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "AUTH_",
        "extra": "ignore"  # Ignore extra fields from .env file
    }


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """Get cached authentication settings."""
    return AuthSettings()


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to verify against.
        
    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token.
        expires_delta: Optional custom expiration time.
        
    Returns:
        Encoded JWT token string.
    """
    settings = get_auth_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Data to encode in the token.
        expires_delta: Optional custom expiration time.
        
    Returns:
        Encoded JWT token string.
    """
    settings = get_auth_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode.
        
    Returns:
        Decoded token payload.
        
    Raises:
        HTTPException: If token is invalid or expired.
    """
    settings = get_auth_settings()
    
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def generate_jti() -> str:
    """
    Generate a unique JWT ID (JTI).
    
    Returns:
        Unique string identifier.
    """
    return str(uuid.uuid4())


def create_user_tokens(
    user: User,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, str]:
    """
    Create access and refresh tokens for a user.
    
    Args:
        user: User to create tokens for.
        user_agent: Client user agent string.
        ip_address: Client IP address.
        db: Database session.
        
    Returns:
        Dictionary containing access and refresh tokens.
    """
    # Generate JTIs for token tracking
    access_jti = generate_jti()
    refresh_jti = generate_jti()
    
    # Create token data
    access_token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "jti": access_jti
    }
    
    refresh_token_data = {
        "sub": str(user.id),
        "jti": refresh_jti
    }
    
    # Create tokens
    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(refresh_token_data)
    
    # Store session information in database if provided
    if db:
        settings = get_auth_settings()
        now = datetime.now(timezone.utc)
        
        # Access token session
        access_session = UserSession(
            user_id=user.id,
            jti=access_jti,
            token_type="access",
            user_agent=user_agent,
            ip_address=ip_address,
            issued_at=now,
            expires_at=now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        )
        
        # Refresh token session
        refresh_session = UserSession(
            user_id=user.id,
            jti=refresh_jti,
            token_type="refresh",
            user_agent=user_agent,
            ip_address=ip_address,
            issued_at=now,
            expires_at=now + timedelta(days=settings.jwt_refresh_token_expire_days)
        )
        
        db.add_all([access_session, refresh_session])
        db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """
    Get the current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials.
        db: Database session.
        
    Returns:
        Current authenticated user.
        
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    # Decode token
    payload = decode_token(credentials.credentials)
    
    # Extract user ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get JTI for session validation
    jti: str = payload.get("jti")
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing JTI",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token type
    token_type: str = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if session exists and is valid
    session = db.query(UserSession).filter(
        UserSession.jti == jti,
        UserSession.token_type == "access"
    ).first()
    
    if not session or not session.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update session last used time
    session.update_last_used()
    db.commit()
    
    return user


def blacklist_token(jti: str, db: Session) -> bool:
    """
    Blacklist a token by its JTI.
    
    Args:
        jti: JWT ID to blacklist.
        db: Database session.
        
    Returns:
        True if token was blacklisted, False if not found.
    """
    session = db.query(UserSession).filter(UserSession.jti == jti).first()
    if session:
        session.blacklist()
        db.commit()
        return True
    return False 