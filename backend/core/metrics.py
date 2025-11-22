"""
Prometheus Metrics
Exposes metrics endpoints for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from typing import Optional

# Service call metrics
service_calls_total = Counter(
    'service_calls_total',
    'Total number of service calls',
    ['service', 'method', 'status']
)

service_call_duration = Histogram(
    'service_call_duration_seconds',
    'Service call duration in seconds',
    ['service', 'method']
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service']
)

circuit_breaker_failures = Counter(
    'circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['service']
)

# Database metrics
database_connections = Gauge(
    'database_connections',
    'Number of active database connections'
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


def record_service_call(service: str, method: str, status: str, duration: float):
    """Record a service call metric"""
    service_calls_total.labels(service=service, method=method, status=status).inc()
    service_call_duration.labels(service=service, method=method).observe(duration)


def record_circuit_breaker_state(service: str, state: str):
    """Record circuit breaker state"""
    state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, -1)
    circuit_breaker_state.labels(service=service).set(state_value)


def record_circuit_breaker_failure(service: str):
    """Record a circuit breaker failure"""
    circuit_breaker_failures.labels(service=service).inc()


def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Record an HTTP request metric"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def get_metrics_response() -> Response:
    """Get Prometheus metrics as HTTP response"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

