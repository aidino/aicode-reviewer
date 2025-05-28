"""
Security configuration for authentication system.

This module provides security headers and CORS configuration
to enhance the security of authentication endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    # CORS settings
    cors_allowed_origins: List[str] = [
        "http://localhost:3000",  # React development server
        "http://localhost:3001",  # Alternative development port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    cors_allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allowed_headers: List[str] = [
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ]
    cors_allow_credentials: bool = True
    cors_max_age: int = 86400  # 24 hours
    
    # Trusted hosts
    trusted_hosts: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.localhost"
    ]
    
    # Security headers
    enable_hsts: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    
    enable_content_security_policy: bool = True
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self' 'unsafe-inline' 'unsafe-eval'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data: https:"
    csp_connect_src: str = "'self'"
    csp_frame_ancestors: str = "'none'"
    
    enable_x_frame_options: bool = True
    x_frame_options: str = "DENY"
    
    enable_x_content_type_options: bool = True
    enable_x_xss_protection: bool = True
    enable_referrer_policy: bool = True
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    enable_permissions_policy: bool = True
    permissions_policy: str = (
        "camera=(), "
        "microphone=(), "
        "geolocation=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "accelerometer=(), "
        "gyroscope=()"
    )
    
    class Config:
        env_prefix = "SECURITY_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    def __init__(self, app, settings: SecuritySettings):
        """
        Initialize security headers middleware.
        
        Args:
            app: FastAPI application.
            settings: Security settings.
        """
        super().__init__(app)
        self.settings = settings
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Add security headers to response.
        
        Args:
            request: HTTP request.
            call_next: Next middleware in chain.
            
        Returns:
            HTTP response with security headers.
        """
        response = await call_next(request)
        
        # HTTP Strict Transport Security (HSTS)
        if self.settings.enable_hsts and request.url.scheme == "https":
            hsts_value = f"max-age={self.settings.hsts_max_age}"
            if self.settings.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.settings.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
        
        # Content Security Policy (CSP)
        if self.settings.enable_content_security_policy:
            csp_directives = [
                f"default-src {self.settings.csp_default_src}",
                f"script-src {self.settings.csp_script_src}",
                f"style-src {self.settings.csp_style_src}",
                f"img-src {self.settings.csp_img_src}",
                f"connect-src {self.settings.csp_connect_src}",
                f"frame-ancestors {self.settings.csp_frame_ancestors}"
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # X-Frame-Options
        if self.settings.enable_x_frame_options:
            response.headers["X-Frame-Options"] = self.settings.x_frame_options
        
        # X-Content-Type-Options
        if self.settings.enable_x_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        if self.settings.enable_x_xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        if self.settings.enable_referrer_policy:
            response.headers["Referrer-Policy"] = self.settings.referrer_policy
        
        # Permissions Policy
        if self.settings.enable_permissions_policy:
            response.headers["Permissions-Policy"] = self.settings.permissions_policy
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        
        return response


def configure_security(app: FastAPI, settings: Optional[SecuritySettings] = None) -> None:
    """
    Configure security middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance.
        settings: Security settings (if None, will use defaults).
    """
    if settings is None:
        settings = SecuritySettings()
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
        max_age=settings.cors_max_age
    )
    
    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts
    )
    
    # Security Headers Middleware
    app.add_middleware(
        SecurityHeadersMiddleware,
        settings=settings
    )


def get_security_settings() -> SecuritySettings:
    """
    Get security settings instance.
    
    Returns:
        Security settings.
    """
    return SecuritySettings()


# Development CORS settings for easier testing
def configure_development_cors(app: FastAPI) -> None:
    """
    Configure CORS for development environment.
    
    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        max_age=86400
    )


# Production security configuration
def configure_production_security(app: FastAPI) -> None:
    """
    Configure security for production environment.
    
    Args:
        app: FastAPI application instance.
    """
    settings = SecuritySettings(
        cors_allowed_origins=[
            "https://yourdomain.com",
            "https://www.yourdomain.com"
        ],
        trusted_hosts=[
            "yourdomain.com",
            "www.yourdomain.com"
        ],
        enable_hsts=True,
        enable_content_security_policy=True,
        csp_script_src="'self'",  # Stricter CSP for production
        csp_style_src="'self'"
    )
    
    configure_security(app, settings) 