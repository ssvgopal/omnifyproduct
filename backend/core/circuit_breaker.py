"""
Circuit Breaker Pattern Implementation
Prevents cascading failures by stopping requests to failing services
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes (half-open)
    timeout_seconds: int = 60  # Time before trying half-open
    expected_exception: type = Exception  # Exception type to catch


class CircuitBreaker:
    """Circuit breaker for service calls"""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: If circuit is open or function fails
        """
        async with self.lock:
            # Check if circuit should transition
            await self._check_state_transition()
            
            # Reject if circuit is open
            if self.state == CircuitState.OPEN:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            # Call the function
            result = await func(*args, **kwargs)
            
            # Record success
            async with self.lock:
                await self._record_success()
            
            return result
        
        except self.config.expected_exception as e:
            # Record failure
            async with self.lock:
                await self._record_failure()
            
            raise
    
    async def _check_state_transition(self):
        """Check and update circuit breaker state"""
        now = datetime.utcnow()
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (now - self.last_failure_time).total_seconds()
                if elapsed >= self.config.timeout_seconds:
                    logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
        
        elif self.state == CircuitState.HALF_OPEN:
            # Check if we have enough successes
            if self.success_count >= self.config.success_threshold:
                logger.info(f"Circuit breaker {self.name} transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
    
    async def _record_success(self):
        """Record a successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    async def _record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                logger.warning(
                    f"Circuit breaker {self.name} opening after {self.failure_count} failures"
                )
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            # Failed during test, go back to open
            logger.warning(f"Circuit breaker {self.name} failed during half-open, reopening")
            self.state = CircuitState.OPEN
            self.success_count = 0
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


# Global circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Get or create circuit breaker for a service"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]

