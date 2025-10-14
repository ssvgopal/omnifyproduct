"""
Production-Ready Circuit Breaker Pattern for OmnifyProduct
Enterprise-grade fault tolerance and resilience for external API calls

Features:
- Automatic failure detection and circuit opening
- Configurable failure thresholds and recovery timeouts
- Half-open state for gradual recovery testing
- Success rate monitoring and alerting
- Redis-backed state persistence
- Async/await support for all Python async operations
- Comprehensive logging and metrics
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
import json

from services.redis_cache_service import redis_cache_service
from services.structured_logging import logger

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 60.0  # Seconds to wait before half-open
    success_threshold: int = 3  # Successes needed to close from half-open
    timeout: float = 30.0  # Request timeout
    expected_exception: tuple = (Exception,)  # Exceptions to count as failures
    name: str = "default"
    monitor_failures: bool = True

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit breaker '{name}' is OPEN. Retry after {retry_after:.1f} seconds")

class ProductionCircuitBreaker:
    """
    Production-grade circuit breaker with Redis persistence and metrics
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()
        self._last_state_change = time.time()

        # Redis keys for persistence
        self.state_key = f"circuit_breaker:{config.name}:state"
        self.metrics_key = f"circuit_breaker:{config.name}:metrics"

        logger.info("Circuit breaker initialized", extra={
            "name": config.name,
            "failure_threshold": config.failure_threshold,
            "recovery_timeout": config.recovery_timeout,
            "timeout": config.timeout
        })

    async def _load_state(self) -> None:
        """Load circuit breaker state from Redis"""
        try:
            if not redis_cache_service.redis_client:
                return

            # Load state
            state_data = await redis_cache_service.redis_client.get(self.state_key)
            if state_data:
                state_info = json.loads(state_data)
                self.state = CircuitBreakerState(state_info["state"])
                self._last_state_change = state_info["last_change"]

            # Load metrics
            metrics_data = await redis_cache_service.redis_client.get(self.metrics_key)
            if metrics_data:
                metrics_info = json.loads(metrics_data)
                self.metrics = CircuitBreakerMetrics(**metrics_info)

        except Exception as e:
            logger.warning("Failed to load circuit breaker state from Redis", exc_info=e)

    async def _save_state(self) -> None:
        """Save circuit breaker state to Redis"""
        try:
            if not redis_cache_service.redis_client:
                return

            # Save state
            state_data = {
                "state": self.state.value,
                "last_change": self._last_state_change
            }
            await redis_cache_service.redis_client.setex(
                self.state_key,
                3600,  # 1 hour TTL
                json.dumps(state_data)
            )

            # Save metrics
            metrics_data = {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "consecutive_failures": self.metrics.consecutive_failures,
                "last_failure_time": self.metrics.last_failure_time,
                "last_success_time": self.metrics.last_success_time,
                "state_changes": self.metrics.state_changes[-10:]  # Keep last 10 changes
            }
            await redis_cache_service.redis_client.setex(
                self.metrics_key,
                3600,  # 1 hour TTL
                json.dumps(metrics_data)
            )

        except Exception as e:
            logger.warning("Failed to save circuit breaker state to Redis", exc_info=e)

    async def _change_state(self, new_state: CircuitBreakerState) -> None:
        """Change circuit breaker state with logging"""
        old_state = self.state
        self.state = new_state
        self._last_state_change = time.time()

        # Record state change
        change_record = {
            "timestamp": self._last_state_change,
            "from_state": old_state.value,
            "to_state": new_state.value,
            "consecutive_failures": self.metrics.consecutive_failures,
            "total_requests": self.metrics.total_requests
        }
        self.metrics.state_changes.append(change_record)

        # Save to Redis
        await self._save_state()

        logger.info("Circuit breaker state changed", extra={
            "name": self.config.name,
            "from_state": old_state.value,
            "to_state": new_state.value,
            "consecutive_failures": self.metrics.consecutive_failures
        })

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.state != CircuitBreakerState.OPEN:
            return False

        time_since_open = time.time() - self._last_state_change
        return time_since_open >= self.config.recovery_timeout

    async def call(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection
        """
        async with self._lock:
            # Load current state
            await self._load_state()

            # Check if circuit should be opened
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    await self._change_state(CircuitBreakerState.HALF_OPEN)
                else:
                    retry_after = self.config.recovery_timeout - (time.time() - self._last_state_change)
                    raise CircuitBreakerOpenException(self.config.name, max(0, retry_after))

            # Record attempt
            self.metrics.total_requests += 1

            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )

                # Success handling
                await self._handle_success()
                return result

            except self.config.expected_exception as e:
                # Failure handling
                await self._handle_failure(e)
                raise
            except asyncio.TimeoutError as e:
                # Timeout handling (count as failure)
                await self._handle_failure(e)
                raise

    async def _handle_success(self) -> None:
        """Handle successful request"""
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.metrics.consecutive_failures = 0
            # Check if we have enough consecutive successes to close
            if self.metrics.successful_requests >= self.config.success_threshold:
                await self._change_state(CircuitBreakerState.CLOSED)
        else:
            self.metrics.consecutive_failures = 0

        await self._save_state()

    async def _handle_failure(self, exception: Exception) -> None:
        """Handle failed request"""
        self.metrics.failed_requests += 1
        self.metrics.consecutive_failures += 1
        self.metrics.last_failure_time = time.time()

        # Log failure
        logger.warning("Circuit breaker request failed", extra={
            "name": self.config.name,
            "consecutive_failures": self.metrics.consecutive_failures,
            "failure_threshold": self.config.failure_threshold,
            "exception_type": type(exception).__name__
        })

        # Check if should open circuit
        if (self.state == CircuitBreakerState.CLOSED and
            self.metrics.consecutive_failures >= self.config.failure_threshold):
            await self._change_state(CircuitBreakerState.OPEN)

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Single failure in half-open state sends back to open
            await self._change_state(CircuitBreakerState.OPEN)

        await self._save_state()

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        success_rate = 0.0
        if self.metrics.total_requests > 0:
            success_rate = (self.metrics.successful_requests / self.metrics.total_requests) * 100

        return {
            "name": self.config.name,
            "state": self.state.value,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "consecutive_failures": self.metrics.consecutive_failures,
            "success_rate": round(success_rate, 2),
            "last_failure_time": self.metrics.last_failure_time,
            "last_success_time": self.metrics.last_success_time,
            "last_state_change": self._last_state_change,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            }
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        metrics = self.get_metrics()

        # Determine health based on state and metrics
        if self.state == CircuitBreakerState.OPEN:
            health = "unhealthy"
            message = f"Circuit breaker is OPEN after {metrics['consecutive_failures']} consecutive failures"
        elif self.state == CircuitBreakerState.HALF_OPEN:
            health = "degraded"
            message = "Circuit breaker is testing service recovery"
        elif metrics['success_rate'] < 95.0 and metrics['total_requests'] > 10:
            health = "degraded"
            message = f"Low success rate: {metrics['success_rate']}%"
        else:
            health = "healthy"
            message = "Circuit breaker operating normally"

        return {
            "status": health,
            "message": message,
            "circuit_breaker": metrics
        }

# Global circuit breaker registry
_circuit_breakers: Dict[str, ProductionCircuitBreaker] = {}

def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> ProductionCircuitBreaker:
    """
    Get or create a circuit breaker instance
    """
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig(name=name)
        _circuit_breakers[name] = ProductionCircuitBreaker(config)

    return _circuit_breakers[name]

async def initialize_circuit_breakers() -> None:
    """Initialize circuit breakers for all platform integrations"""
    # Google Ads circuit breaker
    google_ads_config = CircuitBreakerConfig(
        name="google_ads_api",
        failure_threshold=3,  # Google Ads is strict, fail faster
        recovery_timeout=120.0,  # 2 minutes recovery time
        success_threshold=2,
        timeout=45.0,  # Google Ads can be slow
        expected_exception=(Exception,)  # Catch all exceptions
    )
    get_circuit_breaker("google_ads_api", google_ads_config)

    # Meta Ads circuit breaker
    meta_ads_config = CircuitBreakerConfig(
        name="meta_ads_api",
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=3,
        timeout=30.0,
        expected_exception=(Exception,)
    )
    get_circuit_breaker("meta_ads_api", meta_ads_config)

    # GoHighLevel circuit breaker
    gohighlevel_config = CircuitBreakerConfig(
        name="gohighlevel_api",
        failure_threshold=5,
        recovery_timeout=90.0,
        success_threshold=3,
        timeout=25.0,
        expected_exception=(Exception,)
    )
    get_circuit_breaker("gohighlevel_api", gohighlevel_config)

    # Redis circuit breaker (for cache failures)
    redis_config = CircuitBreakerConfig(
        name="redis_cache",
        failure_threshold=10,  # Redis should be reliable, higher threshold
        recovery_timeout=30.0,
        success_threshold=5,
        timeout=5.0,
        expected_exception=(Exception,)
    )
    get_circuit_breaker("redis_cache", redis_config)

    # MongoDB circuit breaker
    mongodb_config = CircuitBreakerConfig(
        name="mongodb",
        failure_threshold=3,
        recovery_timeout=60.0,
        success_threshold=3,
        timeout=10.0,
        expected_exception=(Exception,)
    )
    get_circuit_breaker("mongodb", mongodb_config)

    logger.info("Circuit breakers initialized for all platform integrations", extra={
        "circuit_breakers_count": len(_circuit_breakers)
    })

def get_all_circuit_breakers() -> Dict[str, ProductionCircuitBreaker]:
    """Get all circuit breaker instances"""
    return _circuit_breakers.copy()

async def get_circuit_breaker_health() -> Dict[str, Any]:
    """Get health status of all circuit breakers"""
    health_status = {}
    for name, cb in _circuit_breakers.items():
        health_status[name] = cb.get_health_status()

    # Overall health
    unhealthy_count = sum(1 for h in health_status.values() if h["status"] == "unhealthy")
    degraded_count = sum(1 for h in health_status.values() if h["status"] == "degraded")

    overall_status = "healthy"
    if unhealthy_count > 0:
        overall_status = "unhealthy"
    elif degraded_count > 0:
        overall_status = "degraded"

    return {
        "overall_status": overall_status,
        "total_circuit_breakers": len(health_status),
        "unhealthy_count": unhealthy_count,
        "degraded_count": degraded_count,
        "circuit_breakers": health_status
    }

# Convenience decorator for circuit breaker protection
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to apply circuit breaker protection to async functions
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cb = get_circuit_breaker(name, config)
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
