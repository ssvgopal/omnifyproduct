"""
Tests for Error Handling
"""

import pytest
from fastapi import HTTPException, status
from core.error_handler import (
    StandardErrorResponse,
    handle_exception
)
from core.database_security import DatabaseSecurityError
from core.retry_logic import RetryError


class TestStandardErrorResponse:
    """Test standard error response creation"""
    
    def test_create_error_response(self):
        """Test basic error response creation"""
        response = StandardErrorResponse.create_error_response(
            error_type="TestError",
            message="Test message",
            status_code=400
        )
        
        assert response.status_code == 400
        content = response.body.decode()
        assert "TestError" in content
        assert "Test message" in content
    
    def test_validation_error(self):
        """Test validation error response"""
        field_errors = {"email": "Invalid format", "password": "Too short"}
        response = StandardErrorResponse.validation_error(
            "Validation failed",
            field_errors
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        content = response.body.decode()
        assert "ValidationError" in content
        assert "field_errors" in content
    
    def test_database_error(self):
        """Test database error response"""
        response = StandardErrorResponse.database_error(
            "Connection failed",
            operation="find_one"
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = response.body.decode()
        assert "DatabaseError" in content
    
    def test_external_api_error(self):
        """Test external API error response"""
        response = StandardErrorResponse.external_api_error(
            "google_ads",
            "API unavailable",
            status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        content = response.body.decode()
        assert "ExternalAPIError" in content
        assert "google_ads" in content
    
    def test_rate_limit_error(self):
        """Test rate limit error response"""
        response = StandardErrorResponse.rate_limit_error(retry_after=60.0)
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "60"
    
    def test_not_found_error(self):
        """Test not found error response"""
        response = StandardErrorResponse.not_found_error(
            "Campaign",
            "campaign_123"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.body.decode()
        assert "NotFoundError" in content
        assert "Campaign" in content


class TestHandleException:
    """Test exception handling"""
    
    def test_handle_http_exception(self):
        """Test handling HTTPException"""
        exc = HTTPException(
            status_code=404,
            detail="Resource not found"
        )
        
        response = handle_exception(exc)
        assert response.status_code == 404
    
    def test_handle_database_security_error(self):
        """Test handling DatabaseSecurityError"""
        exc = DatabaseSecurityError("Tenant isolation violation")
        
        response = handle_exception(exc)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content = response.body.decode()
        assert "SecurityError" in content
    
    def test_handle_retry_error(self):
        """Test handling RetryError"""
        last_exc = Exception("Connection failed")
        exc = RetryError("Operation failed", 3, last_exc)
        
        response = handle_exception(exc)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        content = response.body.decode()
        assert "ExternalAPIError" in content
    
    def test_handle_generic_exception(self):
        """Test handling generic exception"""
        exc = ValueError("Unexpected value")
        
        response = handle_exception(exc)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = response.body.decode()
        assert "InternalServerError" in content

