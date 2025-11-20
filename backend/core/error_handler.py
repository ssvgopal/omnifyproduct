"""
Standardized Error Handler
Provides consistent error response format and handling
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class StandardErrorResponse:
    """Standard error response format"""
    
    @staticmethod
    def create_error_response(
        error_type: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Create standardized error response
        
        Args:
            error_type: Type of error (e.g., "ValidationError", "DatabaseError")
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
            error_code: Application-specific error code
            request_id: Request correlation ID
            
        Returns:
            JSONResponse with error details
        """
        error_response = {
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        if error_code:
            error_response["error"]["code"] = error_code
        
        if request_id:
            error_response["error"]["request_id"] = request_id
        
        if details:
            error_response["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    @staticmethod
    def validation_error(
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create validation error response"""
        details = {"field_errors": field_errors} if field_errors else None
        return StandardErrorResponse.create_error_response(
            error_type="ValidationError",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            error_code="VALIDATION_ERROR",
            request_id=request_id
        )
    
    @staticmethod
    def database_error(
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create database error response"""
        details = {"operation": operation} if operation else None
        return StandardErrorResponse.create_error_response(
            error_type="DatabaseError",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="DATABASE_ERROR",
            request_id=request_id
        )
    
    @staticmethod
    def external_api_error(
        service: str,
        message: str,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create external API error response"""
        details = {"service": service}
        return StandardErrorResponse.create_error_response(
            error_type="ExternalAPIError",
            message=message,
            status_code=status_code,
            details=details,
            error_code="EXTERNAL_API_ERROR",
            request_id=request_id
        )
    
    @staticmethod
    def authentication_error(
        message: str = "Authentication failed",
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create authentication error response"""
        return StandardErrorResponse.create_error_response(
            error_type="AuthenticationError",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            request_id=request_id
        )
    
    @staticmethod
    def authorization_error(
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create authorization error response"""
        details = {"required_permission": required_permission} if required_permission else None
        return StandardErrorResponse.create_error_response(
            error_type="AuthorizationError",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
            error_code="AUTHORIZATION_ERROR",
            request_id=request_id
        )
    
    @staticmethod
    def not_found_error(
        resource_type: str,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create not found error response"""
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        return StandardErrorResponse.create_error_response(
            error_type="NotFoundError",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
            error_code="NOT_FOUND",
            request_id=request_id
        )
    
    @staticmethod
    def rate_limit_error(
        retry_after: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create rate limit error response"""
        message = "Rate limit exceeded"
        details = {"retry_after": retry_after} if retry_after else None
        
        response = StandardErrorResponse.create_error_response(
            error_type="RateLimitError",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
            error_code="RATE_LIMIT_EXCEEDED",
            request_id=request_id
        )
        
        # Add Retry-After header
        if retry_after:
            response.headers["Retry-After"] = str(int(retry_after))
        
        return response
    
    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        error_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create internal server error response"""
        details = {"error_id": error_id} if error_id else None
        return StandardErrorResponse.create_error_response(
            error_type="InternalServerError",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="INTERNAL_ERROR",
            request_id=request_id
        )


def handle_exception(
    exc: Exception,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Handle exception and return standardized error response
    
    Args:
        exc: Exception to handle
        request_id: Request correlation ID
        
    Returns:
        JSONResponse with error details
    """
    # Log the exception
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Handle specific exception types
    if isinstance(exc, HTTPException):
        return StandardErrorResponse.create_error_response(
            error_type="HTTPException",
            message=exc.detail,
            status_code=exc.status_code,
            request_id=request_id
        )
    
    # Handle database security errors
    from core.database_security import DatabaseSecurityError
    if isinstance(exc, DatabaseSecurityError):
        return StandardErrorResponse.create_error_response(
            error_type="SecurityError",
            message=str(exc),
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="SECURITY_VIOLATION",
            request_id=request_id
        )
    
    # Handle retry errors
    from core.retry_logic import RetryError
    if isinstance(exc, RetryError):
        return StandardErrorResponse.external_api_error(
            service="unknown",
            message=f"Operation failed after {exc.attempts} attempts: {exc.last_exception}",
            request_id=request_id
        )
    
    # Generic internal server error
    return StandardErrorResponse.internal_server_error(
        message="An unexpected error occurred",
        request_id=request_id
    )

