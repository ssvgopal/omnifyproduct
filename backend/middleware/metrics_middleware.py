"""
Metrics Middleware
Records HTTP request metrics for Prometheus
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import time
import logging

from services.prometheus_metrics import metrics_collector

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record HTTP metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and record metrics"""
        start_time = time.time()
        
        # Get endpoint path (normalize)
        endpoint = request.url.path
        # Remove IDs from path for better aggregation
        if '/api/' in endpoint:
            # Replace UUIDs and IDs with placeholders
            import re
            endpoint = re.sub(r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '/{id}', endpoint)
            endpoint = re.sub(r'/\d+', '/{id}', endpoint)
        
        method = request.method
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            # Re-raise to let error handler deal with it
            raise
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            try:
                metrics_collector.record_http_request(method, endpoint, status_code, duration)
            except Exception as e:
                logger.error(f"Error recording metrics: {e}")
        
        return response

