"""
Resilient HTTP Client with Circuit Breaker and Retry Logic
Wraps aiohttp with production-ready resilience patterns
"""

import logging
from typing import Dict, Any, Optional, Callable, Awaitable
import aiohttp
from aiohttp import ClientTimeout, ClientError

from services.production_circuit_breaker import ProductionCircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenException
from core.retry_logic import retry_http_request, RetryConfig

logger = logging.getLogger(__name__)


class ResilientHTTPClient:
    """HTTP client with circuit breaker and retry logic"""
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = ClientTimeout(total=timeout)
        self.default_headers = default_headers or {}
        
        # Initialize circuit breaker
        if circuit_breaker_config is None:
            circuit_breaker_config = CircuitBreakerConfig(
                name=f"http_client_{base_url}",
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=timeout
            )
        
        self.circuit_breaker = ProductionCircuitBreaker(circuit_breaker_config)
        
        # Retry config
        if retry_config is None:
            retry_config = RetryConfig(
                max_attempts=3,
                initial_delay=1.0,
                max_delay=30.0
            )
        self.retry_config = retry_config
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.default_headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Make HTTP request with circuit breaker"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async def request_func():
            try:
                # Check circuit breaker
                if not await self.circuit_breaker.call_allowed():
                    raise CircuitBreakerOpenException(
                        self.circuit_breaker.config.name,
                        await self.circuit_breaker.get_retry_after()
                    )
                
                # Make request
                async with self.session.request(method, url, **kwargs) as response:
                    # Record result in circuit breaker
                    if response.status < 400:
                        await self.circuit_breaker.record_success()
                    else:
                        await self.circuit_breaker.record_failure()
                    
                    # Raise exception for error status codes
                    if response.status >= 400:
                        # Read response body for error details
                        try:
                            error_body = await response.text()
                        except:
                            error_body = ""
                        
                        error_msg = f"HTTP {response.status}: {error_body[:200]}"
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_msg
                        )
                    
                    return response
                    
            except CircuitBreakerOpenException:
                raise
            except (ClientError, aiohttp.ClientResponseError) as e:
                # Record failure in circuit breaker
                await self.circuit_breaker.record_failure()
                raise
            except Exception as e:
                # Record failure for unexpected errors
                await self.circuit_breaker.record_failure()
                raise
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """GET request with retry and circuit breaker"""
        request_headers = {**self.default_headers, **(headers or {})}
        
        return await retry_http_request(
            lambda: self._make_request('GET', endpoint, params=params, headers=request_headers, **kwargs),
            self.retry_config,
            f"GET {endpoint}"
        )
    
    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """POST request with retry and circuit breaker"""
        request_headers = {**self.default_headers, **(headers or {})}
        
        return await retry_http_request(
            lambda: self._make_request('POST', endpoint, json=json, data=data, headers=request_headers, **kwargs),
            self.retry_config,
            f"POST {endpoint}"
        )
    
    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """PUT request with retry and circuit breaker"""
        request_headers = {**self.default_headers, **(headers or {})}
        
        return await retry_http_request(
            lambda: self._make_request('PUT', endpoint, json=json, data=data, headers=request_headers, **kwargs),
            self.retry_config,
            f"PUT {endpoint}"
        )
    
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """DELETE request with retry and circuit breaker"""
        request_headers = {**self.default_headers, **(headers or {})}
        
        return await retry_http_request(
            lambda: self._make_request('DELETE', endpoint, headers=request_headers, **kwargs),
            self.retry_config,
            f"DELETE {endpoint}"
        )

