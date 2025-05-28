"""
Rate limiting middleware for authentication endpoints.

This module provides rate limiting functionality to prevent brute force attacks
and abuse of authentication endpoints like login, registration, and password reset.
"""

import time
import asyncio
from typing import Dict, Optional, Callable, Any
from functools import wraps
from collections import defaultdict, deque
from dataclasses import dataclass, field
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int = 5  # Maximum requests per window
    window_seconds: int = 60  # Time window in seconds
    block_duration_seconds: int = 300  # Block duration when limit exceeded (5 minutes)


@dataclass 
class ClientInfo:
    """Information about a client's requests."""
    request_times: deque = field(default_factory=deque)
    blocked_until: Optional[float] = None
    

class InMemoryRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.clients: Dict[str, ClientInfo] = defaultdict(ClientInfo)
        self.configs: Dict[str, RateLimitConfig] = {}
        self._cleanup_interval = 300  # Cleanup old entries every 5 minutes
        self._last_cleanup = time.time()
    
    def configure_endpoint(self, endpoint: str, config: RateLimitConfig) -> None:
        """
        Configure rate limiting for a specific endpoint.
        
        Args:
            endpoint: Endpoint identifier (e.g., "auth.login").
            config: Rate limiting configuration.
        """
        self.configs[endpoint] = config
    
    def _get_client_key(self, request: Request, endpoint: str) -> str:
        """
        Generate a unique key for the client.
        
        Args:
            request: FastAPI request object.
            endpoint: Endpoint identifier.
            
        Returns:
            Unique client key.
        """
        # Get IP address, considering proxy headers
        ip_address = request.headers.get("x-forwarded-for")
        if ip_address:
            ip_address = ip_address.split(",")[0].strip()
        else:
            ip_address = request.headers.get("x-real-ip")
            if not ip_address:
                ip_address = request.client.host if request.client else "unknown"
        
        return f"{endpoint}:{ip_address}"
    
    def _cleanup_old_entries(self) -> None:
        """Remove old entries to prevent memory leaks."""
        current_time = time.time()
        
        # Only cleanup every cleanup_interval seconds
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        keys_to_remove = []
        
        for client_key, client_info in self.clients.items():
            # Remove if client is not blocked and has no recent requests
            if (client_info.blocked_until is None or client_info.blocked_until < current_time):
                if not client_info.request_times:
                    keys_to_remove.append(client_key)
                elif client_info.request_times and \
                     current_time - client_info.request_times[-1] > 3600:  # 1 hour
                    keys_to_remove.append(client_key)
        
        for key in keys_to_remove:
            del self.clients[key]
        
        self._last_cleanup = current_time
    
    def is_allowed(self, request: Request, endpoint: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a request is allowed based on rate limiting.
        
        Args:
            request: FastAPI request object.
            endpoint: Endpoint identifier.
            
        Returns:
            Tuple of (is_allowed, headers_dict).
            headers_dict contains rate limit headers if applicable.
        """
        config = self.configs.get(endpoint)
        if not config:
            return True, None
        
        current_time = time.time()
        client_key = self._get_client_key(request, endpoint)
        client_info = self.clients[client_key]
        
        # Cleanup old entries periodically
        self._cleanup_old_entries()
        
        # Check if client is currently blocked
        if client_info.blocked_until and current_time < client_info.blocked_until:
            retry_after = int(client_info.blocked_until - current_time)
            headers = {
                "X-RateLimit-Limit": str(config.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(client_info.blocked_until)),
                "Retry-After": str(retry_after)
            }
            return False, headers
        
        # Remove expired requests from the sliding window
        window_start = current_time - config.window_seconds
        while client_info.request_times and client_info.request_times[0] < window_start:
            client_info.request_times.popleft()
        
        # Check if adding this request would exceed the limit
        current_requests = len(client_info.request_times)
        
        if current_requests >= config.max_requests:
            # Block the client
            client_info.blocked_until = current_time + config.block_duration_seconds
            
            headers = {
                "X-RateLimit-Limit": str(config.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(client_info.blocked_until)),
                "Retry-After": str(config.block_duration_seconds)
            }
            return False, headers
        
        # Add the current request
        client_info.request_times.append(current_time)
        
        # Calculate remaining requests
        remaining = config.max_requests - current_requests - 1
        reset_time = int(current_time + config.window_seconds)
        
        headers = {
            "X-RateLimit-Limit": str(config.max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time)
        }
        
        return True, headers


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def configure_auth_rate_limits():
    """Configure rate limits for authentication endpoints."""
    # Strict limits for sensitive endpoints
    rate_limiter.configure_endpoint("auth.login", RateLimitConfig(
        max_requests=5,
        window_seconds=60,
        block_duration_seconds=300  # 5 minutes
    ))
    
    rate_limiter.configure_endpoint("auth.register", RateLimitConfig(
        max_requests=3,
        window_seconds=300,  # 5 minutes
        block_duration_seconds=900  # 15 minutes
    ))
    
    rate_limiter.configure_endpoint("auth.change_password", RateLimitConfig(
        max_requests=3,
        window_seconds=60,
        block_duration_seconds=600  # 10 minutes
    ))
    
    # More lenient for other endpoints
    rate_limiter.configure_endpoint("auth.refresh", RateLimitConfig(
        max_requests=20,
        window_seconds=60,
        block_duration_seconds=60
    ))
    
    rate_limiter.configure_endpoint("auth.logout", RateLimitConfig(
        max_requests=10,
        window_seconds=60,
        block_duration_seconds=60
    ))


def rate_limit(endpoint: str):
    """
    Decorator for rate limiting FastAPI endpoints.
    
    Args:
        endpoint: Endpoint identifier for rate limiting configuration.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = None
            if 'request' in kwargs:
                request = kwargs['request']
            else:
                # Try to find Request object in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request is None:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Check rate limit
            is_allowed, headers = rate_limiter.is_allowed(request, endpoint)
            
            if not is_allowed:
                # Return rate limit exceeded response
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Too many requests.",
                        "error_code": "RATE_LIMIT_EXCEEDED"
                    }
                )
                
                # Add rate limit headers
                if headers:
                    for key, value in headers.items():
                        response.headers[key] = value
                
                return response
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Add rate limit headers to successful responses
            if headers and hasattr(result, 'headers'):
                for key, value in headers.items():
                    result.headers[key] = value
            
            return result
        
        return wrapper
    return decorator


# Initialize rate limits on module import
configure_auth_rate_limits() 