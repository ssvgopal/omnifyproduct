"""
Error Handler Middleware
Catches exceptions and returns standardized error responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import logging
import uuid

from core.error_handler import handle_exception

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions and return standardized errors"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors"""
        # Generate request ID for correlation
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Handle exception with standardized error response
            error_response = handle_exception(exc, request_id)
            return error_response

