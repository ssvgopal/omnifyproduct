from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UnifiedAPIGateway:
    """Unified API Gateway for all platform operations"""
    
    def __init__(self):
        self.rate_limits = defaultdict(list)
        self.request_logs = []
        
    async def route_request(self, platform: str, operation: str, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Route requests to appropriate platform adapter"""
        logger.info(f"Routing request to {platform} for operation {operation}")
        
        # Platform routing logic
        routing_map = {
            'agentkit': 'AgentKit',
            'gohighlevel': 'GoHighLevel',
            'custom': 'Custom Platform'
        }
        
        if platform not in routing_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown platform: {platform}"
            )
        
        return {
            'platform': routing_map[platform],
            'operation': operation,
            'status': 'routed',
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
    
    def check_rate_limit(self, client_id: str, limit: int = 100, window: int = 60) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        # Clean old requests
        self.rate_limits[client_id] = [
            req_time for req_time in self.rate_limits[client_id]
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.rate_limits[client_id]) >= limit:
            return False
        
        # Add new request
        self.rate_limits[client_id].append(now)
        return True
    
    async def aggregate_response(self, responses: list) -> Dict[Any, Any]:
        """Aggregate responses from multiple platforms"""
        return {
            'aggregated': True,
            'total_responses': len(responses),
            'responses': responses,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def log_request(self, request_data: Dict[Any, Any]):
        """Log request for analytics"""
        self.request_logs.append({
            **request_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only last 1000 logs in memory
        if len(self.request_logs) > 1000:
            self.request_logs = self.request_logs[-1000:]

gateway = UnifiedAPIGateway()