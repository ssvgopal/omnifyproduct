"""
Database Security Middleware
Automatically enforces tenant isolation on database operations
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

from core.database_security import SecureDatabaseClient

logger = logging.getLogger(__name__)

# Global secure_db instance (will be initialized in lifespan)
_secure_db_instance = None


def get_secure_db():
    """Get global secure database client instance"""
    global _secure_db_instance
    return _secure_db_instance


def set_secure_db(db):
    """Set global secure database client instance"""
    global _secure_db_instance
    if db:
        _secure_db_instance = SecureDatabaseClient(db)
        logger.info("Secure database client initialized")


class DatabaseSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce database security and tenant isolation"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with database security"""
        # Get secure_db from global instance
        secure_db = get_secure_db()
        if secure_db:
            request.state.secure_db = secure_db
        
        # Try to get user context for tenant isolation
        try:
            # This will be set by auth middleware if user is authenticated
            user = getattr(request.state, 'current_user', None)
            if user:
                request.state.organization_id = user.get('organization_id')
                request.state.user_id = user.get('user_id')
        except:
            pass
        
        response = await call_next(request)
        return response
