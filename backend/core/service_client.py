"""
Service Client - HTTP client for inter-service communication
Enables services to call each other in microservices mode
Falls back to direct calls in monolith mode

Features:
- Service-to-service authentication (JWT)
- Retry logic with exponential backoff
- Circuit breaker pattern
- Correlation IDs for tracing
"""

import os
import httpx
import logging
import uuid
from typing import Dict, Any, Optional
from enum import Enum
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from backend.core.service_auth import get_service_auth, ServiceAuth
from backend.core.circuit_breaker import get_circuit_breaker, CircuitBreakerConfig

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Service types"""
    AUTH = "auth"
    INTEGRATIONS = "integrations"
    AGENTKIT = "agentkit"
    ANALYTICS = "analytics"
    ONBOARDING = "onboarding"
    ML = "ml"
    INFRASTRUCTURE = "infrastructure"


class ServiceClient:
    """Client for calling other services with resilience patterns"""
    
    # Service URLs (can be overridden by environment variables)
    SERVICE_URLS = {
        ServiceType.AUTH: os.getenv('AUTH_SERVICE_URL', 'http://auth-service:80'),
        ServiceType.INTEGRATIONS: os.getenv('INTEGRATIONS_SERVICE_URL', 'http://integrations-service:80'),
        ServiceType.AGENTKIT: os.getenv('AGENTKIT_SERVICE_URL', 'http://agentkit-service:80'),
        ServiceType.ANALYTICS: os.getenv('ANALYTICS_SERVICE_URL', 'http://analytics-service:80'),
        ServiceType.ONBOARDING: os.getenv('ONBOARDING_SERVICE_URL', 'http://onboarding-service:80'),
        ServiceType.ML: os.getenv('ML_SERVICE_URL', 'http://ml-service:80'),
        ServiceType.INFRASTRUCTURE: os.getenv('INFRASTRUCTURE_SERVICE_URL', 'http://infrastructure-service:80'),
    }
    
    def __init__(self):
        self.deployment_mode = os.getenv("DEPLOYMENT_MODE", "monolith")
        self.timeout = float(os.getenv("SERVICE_CLIENT_TIMEOUT", "30.0"))
        self.service_auth = get_service_auth()
        self.service_name = self.service_auth.get_service_name()
        
        # Retry configuration
        self.max_retries = int(os.getenv("SERVICE_CLIENT_MAX_RETRIES", "3"))
        self.retry_backoff_base = float(os.getenv("SERVICE_CLIENT_RETRY_BACKOFF", "2.0"))
        
        # Circuit breaker configuration
        self.circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
            success_threshold=int(os.getenv("CIRCUIT_BREAKER_SUCCESS_THRESHOLD", "2")),
            timeout_seconds=int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60")),
        )
    
    async def call_service(
        self,
        service_type: ServiceType,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call another service with retry logic, circuit breaker, and authentication
        
        Args:
            service_type: Type of service to call
            endpoint: API endpoint (e.g., '/api/auth/login')
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body data
            headers: Additional headers
            params: Query parameters
            correlation_id: Optional correlation ID for tracing
        
        Returns:
            Response data as dictionary
        
        Raises:
            Exception: If service call fails after retries or circuit is open
        """
        if self.deployment_mode == "monolith":
            # In monolith mode, services are in the same process
            # For now, we'll still use HTTP calls (can be optimized later)
            logger.debug(f"Monolith mode: calling {service_type.value} via HTTP")
        
        base_url = self.SERVICE_URLS.get(service_type)
        if not base_url:
            raise ValueError(f"Service {service_type.value} not found in service registry")
        
        url = f"{base_url.rstrip('/')}{endpoint}"
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Get circuit breaker for this service
        circuit_breaker = get_circuit_breaker(
            f"{service_type.value}_service",
            self.circuit_breaker_config
        )
        
        # Generate service token for authentication
        service_token = self.service_auth.generate_service_token(
            self.service_name,
            service_type.value
        )
        
        # Add default headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Omnify-ServiceClient/1.0",
            "X-Correlation-ID": correlation_id,
            "X-Service-Name": self.service_name,
        }
        
        # Add service authentication token
        if service_token:
            request_headers["Authorization"] = f"Bearer {service_token}"
        
        if headers:
            request_headers.update(headers)
        
        # Define the actual HTTP call function with retry
        async def _make_request():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    headers=request_headers,
                    params=params
                )
                # Don't retry on 4xx errors (client errors)
                if response.status_code >= 400 and response.status_code < 500:
                    response.raise_for_status()
                # Retry on 5xx errors and network errors
                response.raise_for_status()
                return response.json()
        
        # Retry wrapper - only retries on network errors and 5xx errors
        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.retry_backoff_base, min=1, max=10),
            retry=retry_if_exception_type((httpx.RequestError,)),
            reraise=True
        )
        async def _make_request_with_retry():
            try:
                return await _make_request()
            except httpx.HTTPStatusError as e:
                # Only retry on 5xx errors
                if e.response.status_code >= 500:
                    raise httpx.RequestError("Server error, retrying", request=e.request) from e
                # Don't retry on 4xx errors
                raise
        
        # Call with circuit breaker protection
        try:
            result = await circuit_breaker.call(_make_request_with_retry)
            logger.debug(
                f"Service call successful: {service_type.value} {endpoint} "
                f"[correlation_id={correlation_id}]"
            )
            return result
        
        except RetryError as e:
            logger.error(
                f"Service call failed after retries: {service_type.value} {endpoint} "
                f"[correlation_id={correlation_id}]: {e}"
            )
            raise Exception(f"Service {service_type.value} unavailable after retries") from e
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error calling {service_type.value}: {e.response.status_code} - {e.response.text} "
                f"[correlation_id={correlation_id}]"
            )
            raise
        except httpx.RequestError as e:
            logger.error(
                f"Request error calling {service_type.value}: {str(e)} "
                f"[correlation_id={correlation_id}]"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error calling {service_type.value}: {str(e)} "
                f"[correlation_id={correlation_id}]"
            )
            raise
    
    
    async def call_auth_service(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Convenience method to call auth service"""
        return await self.call_service(ServiceType.AUTH, endpoint, method, data, headers)
    
    async def call_integrations_service(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Convenience method to call integrations service"""
        return await self.call_service(ServiceType.INTEGRATIONS, endpoint, method, data, headers)
    
    async def health_check(self, service_type: ServiceType) -> Dict[str, Any]:
        """Check health of a service"""
        try:
            return await self.call_service(service_type, "/health", method="GET")
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": service_type.value,
                "error": str(e)
            }


# Global service client instance
_service_client = None

def get_service_client() -> ServiceClient:
    """Get global service client instance"""
    global _service_client
    if _service_client is None:
        _service_client = ServiceClient()
    return _service_client

