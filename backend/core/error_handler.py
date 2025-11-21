"""
Enhanced Error Handler
Provides better error messages and user feedback
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    # User-friendly error messages
    ERROR_MESSAGES = {
        'validation_error': 'Please check your input and try again',
        'authentication_error': 'Invalid email or password. Please try again',
        'authorization_error': 'You do not have permission to perform this action',
        'not_found': 'The requested resource was not found',
        'rate_limit': 'Too many requests. Please try again later',
        'server_error': 'An unexpected error occurred. Please try again or contact support',
        'database_error': 'Database operation failed. Please try again',
        'external_api_error': 'Failed to connect to external service. Please try again later',
        'email_send_error': 'Failed to send email. Please check your email configuration',
        'file_upload_error': 'File upload failed. Please check file size and format',
        'integration_error': 'Platform integration failed. Please check your credentials',
    }
    
    @classmethod
    def get_user_friendly_message(cls, error_type: str, detail: Optional[str] = None) -> str:
        """Get user-friendly error message"""
        base_message = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES['server_error'])
        
        if detail:
            # Add detail if it's user-friendly (not a stack trace)
            if not any(keyword in detail.lower() for keyword in ['traceback', 'exception', 'file', 'line']):
                return f"{base_message}: {detail}"
        
        return base_message
    
    @classmethod
    def handle_exception(cls, exc: Exception, error_type: str = 'server_error') -> HTTPException:
        """Handle exception and return user-friendly HTTPException"""
        logger.error(f"Error ({error_type}): {exc}", exc_info=True)
        
        user_message = cls.get_user_friendly_message(error_type, str(exc))
        
        status_code_map = {
            'validation_error': status.HTTP_400_BAD_REQUEST,
            'authentication_error': status.HTTP_401_UNAUTHORIZED,
            'authorization_error': status.HTTP_403_FORBIDDEN,
            'not_found': status.HTTP_404_NOT_FOUND,
            'rate_limit': status.HTTP_429_TOO_MANY_REQUESTS,
            'server_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'database_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'external_api_error': status.HTTP_502_BAD_GATEWAY,
            'email_send_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'file_upload_error': status.HTTP_400_BAD_REQUEST,
            'integration_error': status.HTTP_502_BAD_GATEWAY,
        }
        
        status_code = status_code_map.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return HTTPException(
            status_code=status_code,
            detail=user_message
        )
    
    @classmethod
    def create_error_response(cls, error_type: str, detail: Optional[str] = None, 
                             status_code: Optional[int] = None) -> JSONResponse:
        """Create standardized error response"""
        user_message = cls.get_user_friendly_message(error_type, detail)
        
        if status_code is None:
            status_code_map = {
                'validation_error': status.HTTP_400_BAD_REQUEST,
                'authentication_error': status.HTTP_401_UNAUTHORIZED,
                'authorization_error': status.HTTP_403_FORBIDDEN,
                'not_found': status.HTTP_404_NOT_FOUND,
                'rate_limit': status.HTTP_429_TOO_MANY_REQUESTS,
                'server_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            status_code = status_code_map.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=status_code,
            content={
                'error': error_type,
                'message': user_message,
                'detail': detail if detail and not any(kw in detail.lower() for kw in ['traceback', 'exception']) else None
            }
        )


# Global error handler instance
error_handler = ErrorHandler()
