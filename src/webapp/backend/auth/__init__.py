# Authentication module for the AI Code Reviewer system

from .utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

from .service import AuthService
from .middleware import get_current_active_user, require_role
from .routes import router as auth_router
from .rate_limiting import rate_limit, configure_auth_rate_limits
from .security import (
    configure_security,
    configure_development_cors,
    configure_production_security,
    get_security_settings
)

__all__ = [
    "hash_password",
    "verify_password", 
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "AuthService",
    "get_current_active_user",
    "require_role",
    "auth_router",
    "rate_limit",
    "configure_auth_rate_limits",
    "configure_security",
    "configure_development_cors",
    "configure_production_security",
    "get_security_settings",
] 