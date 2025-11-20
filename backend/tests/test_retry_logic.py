"""
Tests for Retry Logic
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.retry_logic import (
    retry_with_backoff,
    retry_http_request,
    retry_database_operation,
    RetryConfig,
    RetryError
)


@pytest.mark.asyncio
class TestRetryWithBackoff:
    """Test retry with exponential backoff"""
    
    async def test_success_on_first_attempt(self):
        """Test function succeeds on first attempt"""
        func = AsyncMock(return_value="success")
        
        result = await retry_with_backoff(func, operation_name="test")
        
        assert result == "success"
        assert func.call_count == 1
    
    async def test_success_after_retries(self):
        """Test function succeeds after retries"""
        func = AsyncMock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        result = await retry_with_backoff(func, config, "test")
        
        assert result == "success"
        assert func.call_count == 3
    
    async def test_failure_after_max_attempts(self):
        """Test function fails after max attempts"""
        func = AsyncMock(side_effect=Exception("fail"))
        
        config = RetryConfig(max_attempts=2, initial_delay=0.1)
        
        with pytest.raises(RetryError):
            await retry_with_backoff(func, config, "test")
        
        assert func.call_count == 2
    
    async def test_non_retryable_exception(self):
        """Test non-retryable exception is not retried"""
        func = AsyncMock(side_effect=ValueError("non-retryable"))
        
        config = RetryConfig(
            max_attempts=3,
            retryable_exceptions=(RuntimeError,)
        )
        
        with pytest.raises(ValueError):
            await retry_with_backoff(func, config, "test")
        
        assert func.call_count == 1


@pytest.mark.asyncio
class TestRetryHTTPRequest:
    """Test HTTP request retry logic"""
    
    async def test_success_on_first_attempt(self):
        """Test HTTP request succeeds on first attempt"""
        mock_response = MagicMock()
        mock_response.status = 200
        
        request_func = AsyncMock(return_value=mock_response)
        
        result = await retry_http_request(request_func, operation_name="test")
        
        assert result == mock_response
        assert request_func.call_count == 1
    
    async def test_retry_on_500_error(self):
        """Test HTTP request retries on 500 error"""
        mock_response_500 = MagicMock()
        mock_response_500.status = 500
        
        mock_response_200 = MagicMock()
        mock_response_200.status = 200
        
        request_func = AsyncMock(side_effect=[mock_response_500, mock_response_200])
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            retryable_status_codes=[500, 502, 503]
        )
        
        result = await retry_http_request(request_func, config, "test")
        
        assert result.status == 200
        assert request_func.call_count == 2
    
    async def test_retry_on_429_rate_limit(self):
        """Test HTTP request retries on 429 rate limit"""
        mock_response_429 = MagicMock()
        mock_response_429.status = 429
        mock_response_429.headers = {"Retry-After": "1"}
        
        mock_response_200 = MagicMock()
        mock_response_200.status = 200
        
        request_func = AsyncMock(side_effect=[mock_response_429, mock_response_200])
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            retryable_status_codes=[429, 500]
        )
        
        result = await retry_http_request(request_func, config, "test")
        
        assert result.status == 200
        assert request_func.call_count == 2


@pytest.mark.asyncio
class TestRetryDatabaseOperation:
    """Test database operation retry logic"""
    
    async def test_database_operation_success(self):
        """Test database operation succeeds"""
        operation_func = AsyncMock(return_value={"result": "success"})
        
        result = await retry_database_operation(operation_func, operation_name="test")
        
        assert result == {"result": "success"}
        assert operation_func.call_count == 1
    
    async def test_database_operation_retry(self):
        """Test database operation retries on failure"""
        operation_func = AsyncMock(side_effect=[Exception("connection error"), {"result": "success"}])
        
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        
        result = await retry_database_operation(operation_func, config, "test")
        
        assert result == {"result": "success"}
        assert operation_func.call_count == 2

