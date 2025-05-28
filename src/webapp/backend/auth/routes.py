"""
Authentication API routes for the AI Code Reviewer system.

This module provides FastAPI routes for user authentication including
registration, login, logout, profile management, and token operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..models.auth_models import User, UserProfile
from .service import AuthService
from .middleware import get_current_active_user
from .utils import get_auth_settings, security, decode_token
from .rate_limiting import rate_limit
from .schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    UserResponse,
    UserProfileResponse,
    UserWithProfileResponse,
    LoginResponse,
    TokenResponse,
    MessageResponse,
    UserSessionResponse
)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract client information from request.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        Tuple of (user_agent, ip_address).
    """
    user_agent = request.headers.get("user-agent")
    
    # Get IP address, considering proxy headers
    ip_address = request.headers.get("x-forwarded-for")
    if ip_address:
        # x-forwarded-for can contain multiple IPs, take the first one
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.headers.get("x-real-ip")
        if not ip_address:
            ip_address = request.client.host if request.client else None
    
    return user_agent, ip_address


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password."
)
@rate_limit("auth.register")
async def register_user(
    user_data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db_session)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data.
        request: FastAPI request object.
        db: Database session.
        
    Returns:
        Created user information.
        
    Raises:
        HTTPException: If registration fails.
    """
    auth_service = AuthService(db)
    
    try:
        user = auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        ) from e


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user and return access and refresh tokens."
)
@rate_limit("auth.login")
async def login_user(
    user_data: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db_session)
) -> LoginResponse:
    """
    Login user and return tokens.
    
    Args:
        user_data: User login credentials.
        request: FastAPI request object.
        db: Database session.
        
    Returns:
        Login response with tokens and user info.
        
    Raises:
        HTTPException: If login fails.
    """
    auth_service = AuthService(db)
    user_agent, ip_address = get_client_info(request)
    
    try:
        login_result = auth_service.login_user(
            username_or_email=user_data.username_or_email,
            password=user_data.password,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Get token expiry time
        settings = get_auth_settings()
        expires_in = settings.jwt_access_token_expire_minutes * 60
        
        return LoginResponse(
            access_token=login_result["access_token"],
            refresh_token=login_result["refresh_token"],
            token_type=login_result["token_type"],
            expires_in=expires_in,
            user=UserResponse.model_validate(login_result["user"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        ) from e


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Logout user by blacklisting the current access token."
)
@rate_limit("auth.logout")
async def logout_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> MessageResponse:
    """
    Logout user by blacklisting token.
    
    Args:
        credentials: Bearer token credentials.
        db: Database session.
        
    Returns:
        Success message.
    """
    auth_service = AuthService(db)
    
    try:
        success = auth_service.logout_user(credentials.credentials)
        
        if success:
            return MessageResponse(message="Logged out successfully")
        else:
            return MessageResponse(message="Token was already invalid")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        ) from e


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate new access and refresh tokens using a valid refresh token."
)
@rate_limit("auth.refresh")
async def refresh_token(
    token_data: TokenRefreshRequest,
    request: Request,
    db: Session = Depends(get_db_session)
) -> TokenResponse:
    """
    Refresh access token.
    
    Args:
        token_data: Refresh token data.
        request: FastAPI request object.
        db: Database session.
        
    Returns:
        New tokens.
        
    Raises:
        HTTPException: If refresh fails.
    """
    auth_service = AuthService(db)
    user_agent, ip_address = get_client_info(request)
    
    try:
        tokens = auth_service.refresh_token(
            refresh_token=token_data.refresh_token,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Get token expiry time
        settings = get_auth_settings()
        expires_in = settings.jwt_access_token_expire_minutes * 60
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        ) from e


@router.get(
    "/me",
    response_model=UserWithProfileResponse,
    summary="Get current user",
    description="Get current authenticated user information including profile."
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> UserWithProfileResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        User information with profile.
    """
    # Load profile if exists
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    # Create response with profile
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "profile": UserProfileResponse.model_validate(profile) if profile else None
    }
    
    return UserWithProfileResponse.model_validate(user_dict)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update current user's profile information."
)
async def update_user_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> UserProfileResponse:
    """
    Update user profile.
    
    Args:
        profile_data: Profile update data.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        Updated profile information.
        
    Raises:
        HTTPException: If update fails.
    """
    auth_service = AuthService(db)
    
    try:
        profile = auth_service.update_user_profile(
            user=current_user,
            full_name=profile_data.full_name,
            avatar_url=profile_data.avatar_url,
            timezone=profile_data.timezone,
            preferences=profile_data.preferences
        )
        
        return UserProfileResponse.model_validate(profile)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        ) from e


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change current user's password."
)
@rate_limit("auth.change_password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> MessageResponse:
    """
    Change user password.
    
    Args:
        password_data: Password change data.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: If password change fails.
    """
    auth_service = AuthService(db)
    
    try:
        success = auth_service.change_password(
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if success:
            return MessageResponse(
                message="Password changed successfully. Please log in again."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        ) from e


@router.get(
    "/sessions",
    response_model=list[UserSessionResponse],
    summary="Get user sessions",
    description="Get all active sessions for the current user."
)
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> list[UserSessionResponse]:
    """
    Get user sessions.
    
    Args:
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        List of user sessions.
    """
    auth_service = AuthService(db)
    
    sessions = auth_service.get_user_sessions(current_user)
    
    return [UserSessionResponse.model_validate(session) for session in sessions]


@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    summary="Revoke user session",
    description="Revoke a specific user session by ID."
)
async def revoke_user_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> MessageResponse:
    """
    Revoke a user session.
    
    Args:
        session_id: Session ID to revoke.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: If session not found or revocation fails.
    """
    auth_service = AuthService(db)
    
    success = auth_service.revoke_session(current_user, session_id)
    
    if success:
        return MessageResponse(message="Session revoked successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.delete(
    "/sessions",
    response_model=MessageResponse,
    summary="Revoke all sessions",
    description="Revoke all active sessions except the current one."
)
async def revoke_all_user_sessions(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> MessageResponse:
    """
    Revoke all user sessions except current.
    
    Args:
        current_user: Current authenticated user.
        credentials: Bearer token credentials.
        db: Database session.
        
    Returns:
        Success message.
    """
    auth_service = AuthService(db)
    
    try:
        # Get current token JTI to exclude from revocation
        payload = decode_token(credentials.credentials)
        current_jti = payload.get("jti")
        
        revoked_count = auth_service.revoke_all_sessions(
            current_user, 
            except_jti=current_jti
        )
        
        return MessageResponse(
            message=f"Revoked {revoked_count} sessions successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke sessions"
        ) from e 