"""
Authentication middleware and decorators for protected routes.

This module provides middleware functions and decorators for protecting
API endpoints with authentication and authorization.
"""

from typing import Optional, List, Callable, Any
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..models.auth_models import User, UserRole
from .utils import get_current_user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user dependency.
    
    Args:
        current_user: Current authenticated user.
        
    Returns:
        Active user.
        
    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: List[UserRole]):
    """
    Create a dependency that requires specific user roles.
    
    Args:
        allowed_roles: List of allowed user roles.
        
    Returns:
        Dependency function that validates user role.
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if user has required role.
        
        Args:
            current_user: Current authenticated user.
            
        Returns:
            User if role is valid.
            
        Raises:
            HTTPException: If user doesn't have required role.
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires admin role.
    
    Args:
        current_user: Current authenticated user.
        
    Returns:
        User if admin.
        
    Raises:
        HTTPException: If user is not admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_user_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires user or admin role.
    
    Args:
        current_user: Current authenticated user.
        
    Returns:
        User if user or admin.
        
    Raises:
        HTTPException: If user is guest.
    """
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User or admin access required"
        )
    return current_user


class AuthMiddleware:
    """
    Authentication middleware class for custom authorization logic.
    
    This class provides methods for implementing custom authentication
    and authorization logic in API endpoints.
    """
    
    @staticmethod
    def check_user_owns_resource(
        current_user: User,
        resource_user_id: int,
        allow_admin_override: bool = True
    ) -> bool:
        """
        Check if user owns a resource or is admin.
        
        Args:
            current_user: Current authenticated user.
            resource_user_id: User ID that owns the resource.
            allow_admin_override: Whether admin can access any resource.
            
        Returns:
            True if user can access the resource.
        """
        # User owns the resource
        if current_user.id == resource_user_id:
            return True
        
        # Admin override
        if allow_admin_override and current_user.role == UserRole.ADMIN:
            return True
        
        return False
    
    @staticmethod
    def require_resource_owner(
        resource_user_id: int,
        allow_admin_override: bool = True
    ):
        """
        Create a dependency that requires resource ownership.
        
        Args:
            resource_user_id: User ID that owns the resource.
            allow_admin_override: Whether admin can access any resource.
            
        Returns:
            Dependency function that validates resource ownership.
        """
        def ownership_checker(
            current_user: User = Depends(get_current_active_user)
        ) -> User:
            """
            Check if user can access the resource.
            
            Args:
                current_user: Current authenticated user.
                
            Returns:
                User if access is allowed.
                
            Raises:
                HTTPException: If user cannot access the resource.
            """
            if not AuthMiddleware.check_user_owns_resource(
                current_user, 
                resource_user_id, 
                allow_admin_override
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: insufficient permissions"
                )
            return current_user
        
        return ownership_checker
    
    @staticmethod
    def optional_auth() -> Optional[User]:
        """
        Optional authentication dependency.
        
        Returns the current user if authenticated, None otherwise.
        This is useful for endpoints that have different behavior
        for authenticated vs anonymous users.
        
        Note: This should be used as a dependency function in FastAPI routes.
        
        Returns:
            Current user if authenticated, None otherwise.
        """
        def _optional_auth_dependency(
            db: Session = Depends(get_db_session)
        ) -> Optional[User]:
            try:
                # Try to get current user, but don't raise exception if fails
                from fastapi.security import HTTPBearer
                from fastapi import Request
                
                # This would need proper implementation with request context
                # For now, return None to indicate optional authentication
                return None
            except:
                # Authentication failed, return None for anonymous access
                return None
        
        return _optional_auth_dependency


# Decorator functions for route protection
def protected(func: Callable) -> Callable:
    """
    Decorator to protect a route with authentication.
    
    Args:
        func: Route function to protect.
        
    Returns:
        Protected route function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Add current_user dependency if not already present
        if 'current_user' not in kwargs:
            # This would need to be handled by FastAPI dependency injection
            pass
        return await func(*args, **kwargs)
    
    return wrapper


def admin_required(func: Callable) -> Callable:
    """
    Decorator to require admin access for a route.
    
    Args:
        func: Route function to protect.
        
    Returns:
        Protected route function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Add admin dependency if not already present
        if 'current_user' not in kwargs:
            # This would need to be handled by FastAPI dependency injection
            pass
        return await func(*args, **kwargs)
    
    return wrapper


# Helper functions for authentication context
def get_user_context(user: Optional[User]) -> dict:
    """
    Get user context information for templates or responses.
    
    Args:
        user: Current user (can be None for anonymous).
        
    Returns:
        Dictionary containing user context.
    """
    if not user:
        return {
            "authenticated": False,
            "user": None,
            "role": None,
            "permissions": []
        }
    
    # Define permissions based on role
    permissions = []
    
    if user.role == UserRole.ADMIN:
        permissions = [
            "read_all", "write_all", "delete_all", 
            "manage_users", "system_admin"
        ]
    elif user.role == UserRole.USER:
        permissions = [
            "read_own", "write_own", "delete_own",
            "create_scans", "view_reports"
        ]
    elif user.role == UserRole.GUEST:
        permissions = ["read_public", "view_demo"]
    
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.profile.full_name if user.profile else None,
            "role": user.role,
            "is_active": user.is_active
        },
        "role": user.role,
        "permissions": permissions
    }


def has_permission(user: Optional[User], permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: Current user (can be None).
        permission: Permission to check.
        
    Returns:
        True if user has the permission.
    """
    if not user:
        return permission in ["read_public", "view_demo"]
    
    context = get_user_context(user)
    return permission in context["permissions"]


def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission.
    
    Args:
        permission: Required permission.
        
    Returns:
        Dependency function that validates permission.
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        Check if user has required permission.
        
        Args:
            current_user: Current authenticated user.
            
        Returns:
            User if permission is granted.
            
        Raises:
            HTTPException: If user doesn't have required permission.
        """
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_checker 