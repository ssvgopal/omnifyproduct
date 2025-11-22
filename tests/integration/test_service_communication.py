"""
Integration Tests for Service-to-Service Communication
Tests the service client with authentication, retry, and circuit breaker
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from backend.core.service_client import ServiceClient, ServiceType
from backend.core.service_auth import ServiceAuth
from backend.core.circuit_breaker import CircuitBreaker, CircuitState


@pytest.fixture
def service_client():
    """Create a service client instance"""
    with patch.dict("os.environ", {
        "DEPLOYMENT_MODE": "microservices",
        "SERVICE_NAME": "test-service",
        "SERVICE_JWT_SECRET": "test-secret",
    }):
        return ServiceClient()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client"""
    with patch("httpx.AsyncClient") as mock:
        yield mock


@pytest.mark.asyncio
async def test_service_call_success(service_client, mock_httpx_client):
    """Test successful service call"""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = AsyncMock()
    mock_client_instance.request = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_httpx_client.return_value = mock_client_instance
    
    result = await service_client.call_service(
        ServiceType.AUTH,
        "/health",
        method="GET"
    )
    
    assert result == {"status": "ok"}
    mock_client_instance.request.assert_called_once()


@pytest.mark.asyncio
async def test_service_call_with_authentication(service_client, mock_httpx_client):
    """Test service call includes authentication token"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = AsyncMock()
    mock_client_instance.request = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_httpx_client.return_value = mock_client_instance
    
    await service_client.call_service(
        ServiceType.AUTH,
        "/health",
        method="GET"
    )
    
    # Verify Authorization header was added
    call_args = mock_client_instance.request.call_args
    headers = call_args[1]["headers"]
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")
    assert "X-Correlation-ID" in headers
    assert "X-Service-Name" in headers


@pytest.mark.asyncio
async def test_service_call_retry_on_failure(service_client, mock_httpx_client):
    """Test service call retries on transient failures"""
    import httpx
    
    # First two calls fail, third succeeds
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"status": "ok"}
    mock_response_success.raise_for_status = MagicMock()
    
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 500
    mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error",
        request=MagicMock(),
        response=mock_response_fail
    )
    
    mock_client_instance = AsyncMock()
    mock_client_instance.request = AsyncMock(side_effect=[
        mock_response_fail,
        mock_response_fail,
        mock_response_success
    ])
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_httpx_client.return_value = mock_client_instance
    
    result = await service_client.call_service(
        ServiceType.AUTH,
        "/health",
        method="GET"
    )
    
    assert result == {"status": "ok"}
    # Should have retried (3 attempts total)
    assert mock_client_instance.request.call_count == 3


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures(service_client):
    """Test circuit breaker opens after threshold failures"""
    from backend.core.circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
    
    config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=1)
    circuit_breaker = get_circuit_breaker("test_service", config)
    
    # Simulate failures
    async def failing_call():
        raise Exception("Service unavailable")
    
    # First failure
    try:
        await circuit_breaker.call(failing_call)
    except:
        pass
    
    # Second failure should open circuit
    try:
        await circuit_breaker.call(failing_call)
    except:
        pass
    
    # Circuit should be open now
    assert circuit_breaker.state == CircuitState.OPEN
    
    # Next call should be rejected immediately
    with pytest.raises(Exception, match="Circuit breaker.*is OPEN"):
        await circuit_breaker.call(failing_call)


@pytest.mark.asyncio
async def test_service_auth_token_generation():
    """Test service token generation and verification"""
    with patch.dict("os.environ", {"SERVICE_JWT_SECRET": "test-secret"}):
        auth = ServiceAuth()
        
        token = auth.generate_service_token("test-service", "target-service")
        assert token != ""
        
        payload = auth.verify_service_token(token)
        assert payload is not None
        assert payload["service"] == "test-service"
        assert payload["target_service"] == "target-service"
        assert payload["type"] == "service"


@pytest.mark.asyncio
async def test_service_auth_token_verification_fails_invalid():
    """Test service token verification fails for invalid tokens"""
    with patch.dict("os.environ", {"SERVICE_JWT_SECRET": "test-secret"}):
        auth = ServiceAuth()
        
        # Invalid token
        payload = auth.verify_service_token("invalid-token")
        assert payload is None
        
        # Expired token (would need to mock time)
        # This is tested in unit tests for jwt library


@pytest.mark.asyncio
async def test_correlation_id_propagation(service_client, mock_httpx_client):
    """Test correlation ID is propagated in service calls"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = AsyncMock()
    mock_client_instance.request = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_httpx_client.return_value = mock_client_instance
    
    correlation_id = "test-correlation-id-123"
    await service_client.call_service(
        ServiceType.AUTH,
        "/health",
        method="GET",
        correlation_id=correlation_id
    )
    
    # Verify correlation ID in headers
    call_args = mock_client_instance.request.call_args
    headers = call_args[1]["headers"]
    assert headers["X-Correlation-ID"] == correlation_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

