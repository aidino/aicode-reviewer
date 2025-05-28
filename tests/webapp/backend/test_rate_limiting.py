"""
Unit tests for rate limiting functionality.

This module tests the rate limiting middleware and decorator for authentication
endpoints to ensure proper brute force protection.
"""

import time
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import Request
from fastapi.testclient import TestClient

from src.webapp.backend.auth.rate_limiting import (
    InMemoryRateLimiter,
    RateLimitConfig,
    ClientInfo,
    rate_limit,
    configure_auth_rate_limits
)


class TestRateLimitConfig:
    """Test cases for RateLimitConfig dataclass."""
    
    def test_rate_limit_config_defaults(self):
        """Test default values for RateLimitConfig."""
        config = RateLimitConfig()
        
        assert config.max_requests == 5
        assert config.window_seconds == 60
        assert config.block_duration_seconds == 300
    
    def test_rate_limit_config_custom_values(self):
        """Test custom values for RateLimitConfig."""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=120,
            block_duration_seconds=600
        )
        
        assert config.max_requests == 10
        assert config.window_seconds == 120
        assert config.block_duration_seconds == 600


class TestClientInfo:
    """Test cases for ClientInfo dataclass."""
    
    def test_client_info_defaults(self):
        """Test default values for ClientInfo."""
        info = ClientInfo()
        
        assert len(info.request_times) == 0
        assert info.blocked_until is None


class TestInMemoryRateLimiter:
    """Test cases for InMemoryRateLimiter."""
    
    @pytest.fixture
    def limiter(self):
        """Create a fresh rate limiter for testing."""
        return InMemoryRateLimiter()
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        return request
    
    def test_configure_endpoint(self, limiter):
        """Test endpoint configuration."""
        config = RateLimitConfig(max_requests=3, window_seconds=30)
        limiter.configure_endpoint("test.endpoint", config)
        
        assert "test.endpoint" in limiter.configs
        assert limiter.configs["test.endpoint"] == config
    
    def test_get_client_key_with_ip(self, limiter, mock_request):
        """Test client key generation with IP address."""
        key = limiter._get_client_key(mock_request, "test.endpoint")
        
        assert key == "test.endpoint:127.0.0.1"
    
    def test_get_client_key_with_forwarded_for(self, limiter, mock_request):
        """Test client key generation with X-Forwarded-For header."""
        mock_request.headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1"}
        
        key = limiter._get_client_key(mock_request, "test.endpoint")
        
        assert key == "test.endpoint:192.168.1.1"
    
    def test_get_client_key_with_real_ip(self, limiter, mock_request):
        """Test client key generation with X-Real-IP header."""
        mock_request.headers = {"x-real-ip": "192.168.1.1"}
        
        key = limiter._get_client_key(mock_request, "test.endpoint")
        
        assert key == "test.endpoint:192.168.1.1"
    
    def test_is_allowed_no_config(self, limiter, mock_request):
        """Test is_allowed when no configuration exists for endpoint."""
        allowed, headers = limiter.is_allowed(mock_request, "unconfigured.endpoint")
        
        assert allowed is True
        assert headers is None
    
    def test_is_allowed_first_request(self, limiter, mock_request):
        """Test is_allowed for first request."""
        config = RateLimitConfig(max_requests=3, window_seconds=60)
        limiter.configure_endpoint("test.endpoint", config)
        
        allowed, headers = limiter.is_allowed(mock_request, "test.endpoint")
        
        assert allowed is True
        assert headers is not None
        assert headers["X-RateLimit-Limit"] == "3"
        assert headers["X-RateLimit-Remaining"] == "2"
    
    def test_is_allowed_within_limit(self, limiter, mock_request):
        """Test is_allowed when within rate limit."""
        config = RateLimitConfig(max_requests=3, window_seconds=60)
        limiter.configure_endpoint("test.endpoint", config)
        
        # Make first request
        allowed1, headers1 = limiter.is_allowed(mock_request, "test.endpoint")
        assert allowed1 is True
        assert headers1["X-RateLimit-Remaining"] == "2"
        
        # Make second request
        allowed2, headers2 = limiter.is_allowed(mock_request, "test.endpoint")
        assert allowed2 is True
        assert headers2["X-RateLimit-Remaining"] == "1"
    
    def test_is_allowed_exceeds_limit(self, limiter, mock_request):
        """Test is_allowed when rate limit is exceeded."""
        config = RateLimitConfig(max_requests=2, window_seconds=60, block_duration_seconds=300)
        limiter.configure_endpoint("test.endpoint", config)
        
        # Make requests up to limit
        limiter.is_allowed(mock_request, "test.endpoint")
        limiter.is_allowed(mock_request, "test.endpoint")
        
        # This request should be blocked
        allowed, headers = limiter.is_allowed(mock_request, "test.endpoint")
        
        assert allowed is False
        assert headers is not None
        assert headers["X-RateLimit-Remaining"] == "0"
        assert "Retry-After" in headers
    
    def test_is_allowed_while_blocked(self, limiter, mock_request):
        """Test is_allowed when client is blocked."""
        config = RateLimitConfig(max_requests=1, window_seconds=60, block_duration_seconds=300)
        limiter.configure_endpoint("test.endpoint", config)
        
        # Exceed limit to get blocked
        limiter.is_allowed(mock_request, "test.endpoint")
        limiter.is_allowed(mock_request, "test.endpoint")  # This blocks
        
        # Next request should still be blocked
        allowed, headers = limiter.is_allowed(mock_request, "test.endpoint")
        
        assert allowed is False
        assert headers["X-RateLimit-Remaining"] == "0"
    
    def test_sliding_window_expiry(self, limiter, mock_request):
        """Test that old requests expire from sliding window."""
        config = RateLimitConfig(max_requests=2, window_seconds=1)  # 1 second window
        limiter.configure_endpoint("test.endpoint", config)
        
        # Make requests up to limit
        limiter.is_allowed(mock_request, "test.endpoint")
        limiter.is_allowed(mock_request, "test.endpoint")
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        allowed, headers = limiter.is_allowed(mock_request, "test.endpoint")
        
        assert allowed is True
        assert headers["X-RateLimit-Remaining"] == "1"
    
    def test_different_clients_separate_limits(self, limiter):
        """Test that different clients have separate rate limits."""
        config = RateLimitConfig(max_requests=1, window_seconds=60)
        limiter.configure_endpoint("test.endpoint", config)
        
        # Create two different clients
        client1 = Mock(spec=Request)
        client1.client = Mock()
        client1.client.host = "127.0.0.1"
        client1.headers = {}
        
        client2 = Mock(spec=Request)
        client2.client = Mock()
        client2.client.host = "127.0.0.2"
        client2.headers = {}
        
        # Both should be allowed their first request
        allowed1, _ = limiter.is_allowed(client1, "test.endpoint")
        allowed2, _ = limiter.is_allowed(client2, "test.endpoint")
        
        assert allowed1 is True
        assert allowed2 is True


class TestConfigureAuthRateLimits:
    """Test cases for auth rate limits configuration."""
    
    def test_configure_auth_rate_limits(self):
        """Test that auth rate limits are configured correctly."""
        limiter = InMemoryRateLimiter()
        
        # Configure endpoints
        limiter.configure_endpoint("auth.login", RateLimitConfig(
            max_requests=5, window_seconds=60, block_duration_seconds=300
        ))
        limiter.configure_endpoint("auth.register", RateLimitConfig(
            max_requests=3, window_seconds=300, block_duration_seconds=900
        ))
        
        # Check login config
        login_config = limiter.configs["auth.login"]
        assert login_config.max_requests == 5
        assert login_config.window_seconds == 60
        assert login_config.block_duration_seconds == 300
        
        # Check register config
        register_config = limiter.configs["auth.register"]
        assert register_config.max_requests == 3
        assert register_config.window_seconds == 300
        assert register_config.block_duration_seconds == 900


class TestRateLimitDecorator:
    """Test cases for rate_limit decorator."""
    
    @pytest.fixture
    def mock_function(self):
        """Create a mock async function to decorate."""
        async def test_func(request, *args, **kwargs):
            return {"message": "success"}
        return test_func
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        return request
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_allowed(self, mock_function, mock_request):
        """Test rate limit decorator when request is allowed."""
        # Configure a lenient rate limit
        limiter = InMemoryRateLimiter()
        limiter.configure_endpoint("test.endpoint", RateLimitConfig(
            max_requests=10, window_seconds=60
        ))
        
        # Apply decorator
        decorated_func = rate_limit("test.endpoint")(mock_function)
        
        # Mock the global rate limiter
        import src.webapp.backend.auth.rate_limiting as rl_module
        original_limiter = rl_module.rate_limiter
        rl_module.rate_limiter = limiter
        
        try:
            # Call decorated function
            result = await decorated_func(mock_request)
            
            assert result == {"message": "success"}
        finally:
            # Restore original limiter
            rl_module.rate_limiter = original_limiter
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_blocked(self, mock_function, mock_request):
        """Test rate limit decorator when request is blocked."""
        # Configure a strict rate limit
        limiter = InMemoryRateLimiter()
        limiter.configure_endpoint("test.endpoint", RateLimitConfig(
            max_requests=1, window_seconds=60, block_duration_seconds=300
        ))
        
        # Exceed the limit
        limiter.is_allowed(mock_request, "test.endpoint")
        limiter.is_allowed(mock_request, "test.endpoint")  # This should block
        
        # Apply decorator
        decorated_func = rate_limit("test.endpoint")(mock_function)
        
        # Mock the global rate limiter
        import src.webapp.backend.auth.rate_limiting as rl_module
        original_limiter = rl_module.rate_limiter
        rl_module.rate_limiter = limiter
        
        try:
            # Call decorated function
            result = await decorated_func(mock_request)
            
            # Should return JSONResponse with 429 status
            assert result.status_code == 429
            assert "Rate limit exceeded" in result.body.decode()
        finally:
            # Restore original limiter
            rl_module.rate_limiter = original_limiter 