"""
Prometheus Metrics Export
Exports application metrics for monitoring
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database Metrics
database_operations_total = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'collection', 'status']
)

database_operation_duration_seconds = Histogram(
    'database_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'collection']
)

# External API Metrics
external_api_requests_total = Counter(
    'external_api_requests_total',
    'Total external API requests',
    ['service', 'endpoint', 'status']
)

external_api_request_duration_seconds = Histogram(
    'external_api_request_duration_seconds',
    'External API request duration in seconds',
    ['service', 'endpoint']
)

external_api_circuit_breaker_state = Gauge(
    'external_api_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service']
)

# Business Metrics
campaigns_total = Gauge(
    'campaigns_total',
    'Total number of campaigns',
    ['status', 'platform']
)

campaign_performance_roas = Gauge(
    'campaign_performance_roas',
    'Campaign ROAS',
    ['campaign_id', 'platform']
)

# System Metrics
active_sessions = Gauge(
    'active_sessions_total',
    'Total active user sessions'
)

active_users = Gauge(
    'active_users_total',
    'Total active users',
    ['organization_id']
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['type', 'severity']
)


class MetricsCollector:
    """Collects and exports metrics"""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        http_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_database_operation(operation: str, collection: str, status: str, duration: float):
        """Record database operation metrics"""
        database_operations_total.labels(operation=operation, collection=collection, status=status).inc()
        database_operation_duration_seconds.labels(operation=operation, collection=collection).observe(duration)
    
    @staticmethod
    def record_external_api_request(service: str, endpoint: str, status_code: int, duration: float):
        """Record external API request metrics"""
        external_api_requests_total.labels(service=service, endpoint=endpoint, status=str(status_code)).inc()
        external_api_request_duration_seconds.labels(service=service, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_circuit_breaker_state(service: str, state: str):
        """Record circuit breaker state"""
        state_map = {'closed': 0, 'open': 1, 'half_open': 2}
        external_api_circuit_breaker_state.labels(service=service).set(state_map.get(state, 0))
    
    @staticmethod
    def record_campaign_metrics(campaign_id: str, platform: str, status: str, roas: float):
        """Record campaign metrics"""
        campaigns_total.labels(status=status, platform=platform).inc()
        campaign_performance_roas.labels(campaign_id=campaign_id, platform=platform).set(roas)
    
    @staticmethod
    def record_error(error_type: str, severity: str):
        """Record error"""
        errors_total.labels(type=error_type, severity=severity).inc()
    
    @staticmethod
    def get_metrics() -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest(REGISTRY)


# Global metrics collector instance
metrics_collector = MetricsCollector()

