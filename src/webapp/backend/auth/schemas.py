"""
Pydantic schemas for authentication API requests and responses.

This module defines the data models for authentication endpoints
including registration, login, profile management, and token operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from ..models.auth_models import UserRole


# Request schemas
class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password (development mode: relaxed validation)")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "test",
                "full_name": "John Doe"
            }
        }
    )


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username_or_email": "john_doe",
                "password": "SecurePassword123!"
            }
        }
    )


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Valid refresh token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=1, description="New password (development mode: relaxed validation)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "test",
                "new_password": "newtest"
            }
        }
    )


class UpdateProfileRequest(BaseModel):
    """Schema for user profile update request."""
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar image URL")
    timezone: Optional[str] = Field(None, max_length=50, description="User timezone")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "timezone": "Asia/Ho_Chi_Minh",
                "preferences": {
                    "theme": "light",
                    "notifications": {
                        "email": True,
                        "push": False
                    }
                }
            }
        }
    )


# Response schemas
class UserResponse(BaseModel):
    """Schema for user information response."""
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    user_id: int
    full_name: Optional[str]
    avatar_url: Optional[str]
    timezone: str
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithProfileResponse(BaseModel):
    """Schema for user with profile response."""
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse]
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expires in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expires in seconds")
    user: UserResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "role": "user",
                    "is_active": True,
                    "created_at": "2025-01-28T10:00:00Z",
                    "updated_at": "2025-01-28T10:00:00Z"
                }
            }
        }
    )


class UserSessionResponse(BaseModel):
    """Schema for user session response."""
    id: int
    user_id: int
    jti: str
    token_type: str
    user_agent: Optional[str]
    ip_address: Optional[str]
    is_active: bool
    is_blacklisted: bool
    issued_at: datetime
    expires_at: datetime
    last_used_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Schema for simple message response."""
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str
    error_code: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid credentials",
                "error_code": "AUTH_001"
            }
        }
    )


class ValidationErrorResponse(BaseModel):
    """Schema for validation error response."""
    detail: str
    errors: list[Dict[str, Any]]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Validation error",
                "errors": [
                    {
                        "field": "password",
                        "message": "Password must be at least 8 characters long",
                        "code": "min_length"
                    }
                ]
            }
        }
    )


class UserProfileWithDefaults(BaseModel):
    """
    User profile data with default values for profile completion.
    
    This model provides sensible defaults for new user profiles.
    """
    full_name: str = "New User"
    bio: str = "Software developer passionate about code quality and AI-assisted development."
    avatar_url: str = "https://via.placeholder.com/150?text=AI"
    location: str = "Remote"
    company: str = "Tech Company"
    github_username: str = ""
    linkedin_url: str = ""
    website_url: str = ""
    
    # Notification settings with defaults
    email_notifications: bool = True
    security_alerts: bool = True
    scan_updates: bool = True
    weekly_reports: bool = False
    
    # App preferences with defaults
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"  # Only light theme available
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Alex Developer",
                "bio": "Full-stack developer with 5+ years experience in Python, React, and cloud technologies. Passionate about clean code and automated testing.",
                "avatar_url": "https://via.placeholder.com/150?text=AD", 
                "location": "San Francisco, CA",
                "company": "TechCorp Inc.",
                "github_username": "alexdev",
                "linkedin_url": "https://linkedin.com/in/alexdev",
                "website_url": "https://alexdev.portfolio.com",
                "email_notifications": True,
                "security_alerts": True,
                "scan_updates": True,
                "weekly_reports": True,
                "language": "en",
                "timezone": "America/Los_Angeles",
                "theme": "light",
            }
        } 