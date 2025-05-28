"""
Authentication service for user management.

This module provides high-level authentication services including
user registration, login, password validation, and session management.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.auth_models import User, UserProfile, UserSession, UserRole
from .utils import (
    hash_password, 
    verify_password, 
    create_user_tokens,
    decode_token,
    blacklist_token,
    get_auth_settings
)

# Configure logging
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for user management.
    
    This service provides methods for user registration, login,
    password validation, and session management.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the authentication service.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    def validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength.
        
        DEVELOPMENT MODE: Relaxed validation - only requires at least 1 character
        
        Args:
            password: Password to validate.
            
        Returns:
            True if password meets requirements, False otherwise.
        """
        # Development mode: only require at least 1 character
        if len(password) < 1:
            return False
        
        return True
        
        # Original strict validation (commented out for development)
        # if len(password) < 8:
        #     return False
        # 
        # # Check for uppercase letter
        # if not re.search(r"[A-Z]", password):
        #     return False
        # 
        # # Check for lowercase letter
        # if not re.search(r"[a-z]", password):
        #     return False
        # 
        # # Check for digit
        # if not re.search(r"\d", password):
        #     return False
        # 
        # # Check for special character
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        #     return False
        # 
        # return True
    
    def validate_email_format(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if email format is valid, False otherwise.
        """
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None
    
    def check_username_availability(self, username: str) -> bool:
        """
        Check if username is available.
        
        Args:
            username: Username to check.
            
        Returns:
            True if username is available, False otherwise.
        """
        existing_user = self.db.query(User).filter(
            User.username == username
        ).first()
        return existing_user is None
    
    def check_email_availability(self, email: str) -> bool:
        """
        Check if email is available.
        
        Args:
            email: Email to check.
            
        Returns:
            True if email is available, False otherwise.
        """
        existing_user = self.db.query(User).filter(
            User.email == email
        ).first()
        return existing_user is None
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Register a new user.
        
        Args:
            username: Unique username.
            email: User email address.
            password: Plain text password.
            full_name: Optional full name.
            role: User role (default: USER).
            
        Returns:
            Created user object.
            
        Raises:
            HTTPException: If validation fails or user already exists.
        """
        logger.info(f"🚀 Starting registration process for username: {username}, email: {email}")
        
        # Validate email format
        logger.info("📧 Validating email format...")
        if not self.validate_email_format(email):
            logger.error(f"❌ Invalid email format: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        logger.info("✅ Email format valid")
        
        # Validate password strength
        logger.info("🔐 Validating password strength...")
        if not self.validate_password_strength(password):
            logger.error("❌ Password does not meet strength requirements")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet strength requirements"
            )
        logger.info("✅ Password validation passed")
        
        # Check username availability
        logger.info(f"👤 Checking username availability: {username}")
        if not self.check_username_availability(username):
            logger.error(f"❌ Username already exists: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        logger.info("✅ Username available")
        
        # Check email availability
        logger.info(f"📧 Checking email availability: {email}")
        if not self.check_email_availability(email):
            logger.error(f"❌ Email already registered: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logger.info("✅ Email available")
        
        # Hash password
        logger.info("🔒 Hashing password...")
        password_hash = hash_password(password)
        logger.info("✅ Password hashed successfully")
        
        # Create user
        logger.info("📝 Creating user in database...")
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        
        self.db.add(user)
        
        try:
            self.db.commit()
            logger.info("✅ User committed to database")
        except Exception as e:
            logger.error(f"💥 Database commit failed: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            ) from e
        
        self.db.refresh(user)
        logger.info(f"👤 User created with ID: {user.id}")
        
        # Create user profile if full_name provided
        if full_name:
            logger.info(f"📋 Creating user profile with full name: {full_name}")
            profile = UserProfile(
                user_id=user.id,
                full_name=full_name
            )
            self.db.add(profile)
            
            try:
                self.db.commit()
                logger.info("✅ User profile created successfully")
            except Exception as e:
                logger.error(f"💥 Failed to create user profile: {str(e)}")
                # Don't fail registration if profile creation fails
                self.db.rollback()
        
        logger.info(f"🎉 Registration complete for user: {username} (ID: {user.id})")
        return user
    
    def authenticate_user(
        self,
        username_or_email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with username/email and password.
        
        Args:
            username_or_email: Username or email address.
            password: Plain text password.
            
        Returns:
            User object if authentication successful, None otherwise.
        """
        logger.info(f"🔍 Authenticating user: {username_or_email}")
        
        # Try to find user by username or email
        user = self.db.query(User).filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()
        
        if not user:
            logger.warning(f"❌ User not found: {username_or_email}")
            return None
        
        logger.info(f"👤 User found: {user.username} (ID: {user.id})")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"❌ User is inactive: {user.username}")
            return None
        
        logger.info(f"✅ User is active: {user.username}")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"❌ Password verification failed for user: {user.username}")
            return None
        
        logger.info(f"✅ Password verified for user: {user.username}")
        return user
    
    def login_user(
        self,
        username_or_email: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Login a user and create tokens.
        
        Args:
            username_or_email: Username or email address.
            password: Plain text password.
            user_agent: Client user agent string.
            ip_address: Client IP address.
            
        Returns:
            Dictionary containing tokens and user info.
            
        Raises:
            HTTPException: If authentication fails.
        """
        logger.info(f"🚀 Starting login process for: {username_or_email}")
        
        # Authenticate user
        user = self.authenticate_user(username_or_email, password)
        if not user:
            logger.error(f"❌ Authentication failed for: {username_or_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.info(f"✅ User authenticated successfully: {user.username}")
        
        # Create tokens
        logger.info(f"🔑 Creating tokens for user: {user.username}")
        try:
            tokens = create_user_tokens(
                user=user,
                user_agent=user_agent,
                ip_address=ip_address,
                db=self.db
            )
            logger.info(f"✅ Tokens created successfully for user: {user.username}")
        except Exception as e:
            logger.error(f"💥 Token creation failed for user {user.username}: {str(e)}", exc_info=True)
            raise
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role if isinstance(user.role, str) else user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        logger.info(f"📋 User data prepared: {user_data['username']} (role: {user_data['role']})")
        
        result = {
            **tokens,
            "user": user_data
        }
        
        logger.info(f"🎉 Login process completed successfully for: {user.username}")
        return result
    
    def logout_user(self, token: str) -> bool:
        """
        Logout a user by blacklisting their token.
        
        Args:
            token: JWT access token to blacklist.
            
        Returns:
            True if logout successful, False otherwise.
        """
        try:
            # Decode token to get JTI
            payload = decode_token(token)
            jti = payload.get("jti")
            
            if jti:
                # Blacklist the token
                return blacklist_token(jti, self.db)
        except Exception:
            # Token is invalid or already expired
            pass
        
        return False
    
    def refresh_token(
        self,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token.
            user_agent: Client user agent string.
            ip_address: Client IP address.
            
        Returns:
            Dictionary containing new tokens.
            
        Raises:
            HTTPException: If refresh token is invalid.
        """
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            
            # Validate token type
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Get user ID and JTI
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            if not user_id or not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Check if refresh token session exists and is valid
            session = self.db.query(UserSession).filter(
                UserSession.jti == jti,
                UserSession.token_type == "refresh"
            ).first()
            
            if not session or not session.is_valid():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token is invalid or expired"
                )
            
            # Get user
            user = self.db.query(User).filter(User.id == int(user_id)).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Blacklist old refresh token
            session.blacklist()
            
            # Create new tokens
            tokens = create_user_tokens(
                user=user,
                user_agent=user_agent,
                ip_address=ip_address,
                db=self.db
            )
            
            return tokens
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            ) from e
    
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user: User to change password for.
            current_password: Current password.
            new_password: New password.
            
        Returns:
            True if password changed successfully.
            
        Raises:
            HTTPException: If validation fails.
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        if not self.validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password does not meet strength requirements"
            )
        
        # Hash and update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        
        # Invalidate all user sessions to force re-login
        self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).update({
            "is_blacklisted": True,
            "is_active": False,
            "blacklisted_at": datetime.now(timezone.utc)
        })
        
        self.db.commit()
        
        return True
    
    def update_user_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        timezone: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Update user profile information.
        
        Args:
            user: User to update profile for.
            full_name: New full name.
            avatar_url: New avatar URL.
            timezone: New timezone.
            preferences: New preferences.
            
        Returns:
            Updated user profile.
        """
        # Get or create user profile
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user.id
        ).first()
        
        if not profile:
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)
        
        # Update fields if provided
        if full_name is not None:
            profile.full_name = full_name
        
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        
        if timezone is not None:
            profile.timezone = timezone
        
        if preferences is not None:
            profile.preferences = preferences
        
        profile.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def get_user_sessions(self, user: User) -> list[UserSession]:
        """
        Get all active sessions for a user.
        
        Args:
            user: User to get sessions for.
            
        Returns:
            List of active user sessions.
        """
        return self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).order_by(UserSession.last_used_at.desc()).all()
    
    def revoke_session(self, user: User, session_id: int) -> bool:
        """
        Revoke a specific user session.
        
        Args:
            user: User who owns the session.
            session_id: Session ID to revoke.
            
        Returns:
            True if session was revoked, False if not found.
        """
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.blacklist()
            self.db.commit()
            return True
        
        return False
    
    def revoke_all_sessions(self, user: User, except_jti: Optional[str] = None) -> int:
        """
        Revoke all active sessions for a user.
        
        Args:
            user: User to revoke sessions for.
            except_jti: Optional JTI to exclude from revocation.
            
        Returns:
            Number of sessions revoked.
        """
        query = self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        )
        
        if except_jti:
            query = query.filter(UserSession.jti != except_jti)
        
        sessions = query.all()
        
        for session in sessions:
            session.blacklist()
        
        self.db.commit()
        
        return len(sessions) 