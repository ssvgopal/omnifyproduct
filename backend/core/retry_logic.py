"""
Retry Logic with Exponential Backoff
For resilient external API calls and database operations
"""

import asyncio
import logging
from typing import Callable, Awaitable, TypeVar, Optional, List, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,),
        retryable_status_codes: List[int] = None
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
        self.retryable_status_codes = retryable_status_codes or [429, 500, 502, 503, 504]


class RetryError(Exception):
    """Exception raised when all retry attempts fail"""
    def __init__(self, message: str, attempts: int, last_exception: Exception):
        self.message = message
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(f"{message} (attempts: {attempts})")


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None,
    operation_name: str = "operation"
) -> T:
    """
    Retry an async function with exponential backoff
    
    Args:
        func: Async function to retry
        config: Retry configuration
        operation_name: Name of operation for logging
        
    Returns:
        Result of function call
        
    Raises:
        RetryError: If all attempts fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            result = await func()
            if attempt > 1:
                logger.info(f"{operation_name} succeeded on attempt {attempt}")
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if exception is retryable
            if not isinstance(e, config.retryable_exceptions):
                logger.error(f"{operation_name} failed with non-retryable exception: {e}")
                raise
            
            # Check if it's the last attempt
            if attempt >= config.max_attempts:
                logger.error(f"{operation_name} failed after {attempt} attempts: {e}")
                raise RetryError(
                    f"{operation_name} failed after {config.max_attempts} attempts",
                    attempt,
                    e
                )
            
            # Calculate delay with exponential backoff
            delay = min(
                config.initial_delay * (config.exponential_base ** (attempt - 1)),
                config.max_delay
            )
            
            # Add jitter to prevent thundering herd
            if config.jitter:
                jitter_amount = delay * 0.1 * random.random()
                delay = delay + jitter_amount
            
            logger.warning(
                f"{operation_name} failed on attempt {attempt}/{config.max_attempts}, "
                f"retrying in {delay:.2f}s: {e}"
            )
            
            await asyncio.sleep(delay)
    
    # Should not reach here, but just in case
    raise RetryError(
        f"{operation_name} failed after {config.max_attempts} attempts",
        config.max_attempts,
        last_exception
    )


async def retry_http_request(
    request_func: Callable[[], Awaitable[Any]],
    config: Optional[RetryConfig] = None,
    operation_name: str = "HTTP request"
) -> Any:
    """
    Retry HTTP request with status code handling
    
    Args:
        request_func: Async function that makes HTTP request
        config: Retry configuration
        operation_name: Name of operation for logging
        
    Returns:
        Response from HTTP request
    """
    if config is None:
        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=30.0
        )
    
    last_exception = None
    last_status_code = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            response = await request_func()
            
            # Check if response has status_code attribute
            if hasattr(response, 'status'):
                status_code = response.status
            elif hasattr(response, 'status_code'):
                status_code = response.status_code
            elif isinstance(response, dict) and 'status_code' in response:
                status_code = response['status_code']
            else:
                # Assume success if no status code
                if attempt > 1:
                    logger.info(f"{operation_name} succeeded on attempt {attempt}")
                return response
            
            # Check if status code is retryable
            if status_code not in config.retryable_status_codes:
                if attempt > 1:
                    logger.info(f"{operation_name} succeeded on attempt {attempt}")
                return response
            
            # Status code is retryable
            last_status_code = status_code
            if attempt >= config.max_attempts:
                logger.error(
                    f"{operation_name} failed with status {status_code} after {attempt} attempts"
                )
                raise RetryError(
                    f"{operation_name} failed with status {status_code}",
                    attempt,
                    Exception(f"HTTP {status_code}")
                )
            
            # Calculate delay
            delay = min(
                config.initial_delay * (config.exponential_base ** (attempt - 1)),
                config.max_delay
            )
            
            # For 429 (rate limit), use Retry-After header if available
            if status_code == 429 and hasattr(response, 'headers'):
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        pass
            
            if config.jitter:
                jitter_amount = delay * 0.1 * random.random()
                delay = delay + jitter_amount
            
            logger.warning(
                f"{operation_name} returned status {status_code} on attempt {attempt}/{config.max_attempts}, "
                f"retrying in {delay:.2f}s"
            )
            
            await asyncio.sleep(delay)
            
        except Exception as e:
            last_exception = e
            
            # Check if exception is retryable
            if not isinstance(e, config.retryable_exceptions):
                logger.error(f"{operation_name} failed with non-retryable exception: {e}")
                raise
            
            if attempt >= config.max_attempts:
                logger.error(f"{operation_name} failed after {attempt} attempts: {e}")
                raise RetryError(
                    f"{operation_name} failed after {config.max_attempts} attempts",
                    attempt,
                    e
                )
            
            # Calculate delay
            delay = min(
                config.initial_delay * (config.exponential_base ** (attempt - 1)),
                config.max_delay
            )
            
            if config.jitter:
                jitter_amount = delay * 0.1 * random.random()
                delay = delay + jitter_amount
            
            logger.warning(
                f"{operation_name} failed on attempt {attempt}/{config.max_attempts}, "
                f"retrying in {delay:.2f}s: {e}"
            )
            
            await asyncio.sleep(delay)
    
    raise RetryError(
        f"{operation_name} failed after {config.max_attempts} attempts",
        config.max_attempts,
        last_exception or Exception(f"HTTP {last_status_code}")
    )


async def retry_database_operation(
    operation_func: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None,
    operation_name: str = "database operation"
) -> T:
    """
    Retry database operation with connection retry
    
    Args:
        operation_func: Async function that performs database operation
        config: Retry configuration
        operation_name: Name of operation for logging
        
    Returns:
        Result of database operation
    """
    if config is None:
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.5,
            max_delay=5.0,
            retryable_exceptions=(Exception,)  # Retry all exceptions for DB
        )
    
    return await retry_with_backoff(operation_func, config, operation_name)

