from fastapi import HTTPException, status, Request
from typing import Dict, Any
from collections import defaultdict
import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            'default': {'requests': 100, 'window': 60},
            'agentkit': {'requests': 200, 'window': 60},
            'gohighlevel': {'requests': 150, 'window': 60},
            'custom': {'requests': 300, 'window': 60}
        }
    
    async def check_limit(self, request: Request, platform: str = 'default') -> bool:
        """Check if request is within rate limit"""
        # Get client identifier (IP or user ID)
        client_id = request.client.host if request.client else 'unknown'
        
        # Get platform-specific limits
        limit_config = self.limits.get(platform, self.limits['default'])
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        now = time.time()
        key = f"{client_id}:{platform}"
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {client_id} on {platform}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window} seconds."
            )
        
        # Add new request
        self.requests[key].append(now)
        return True
    
    def get_remaining_requests(self, client_id: str, platform: str = 'default') -> int:
        """Get remaining requests for client"""
        limit_config = self.limits.get(platform, self.limits['default'])
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        now = time.time()
        key = f"{client_id}:{platform}"
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        return max_requests - len(self.requests[key])

rate_limiter = RateLimiter()