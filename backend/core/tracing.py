"""
Distributed Tracing with OpenTelemetry
Provides distributed tracing across services
"""

import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

# OpenTelemetry imports (optional)
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning("OpenTelemetry not installed. Tracing will be disabled.")


class TracingService:
    """Distributed tracing service"""
    
    def __init__(self, service_name: str = "omnify-cloud-connect"):
        """
        Initialize tracing service
        
        Args:
            service_name: Name of the service for tracing
        """
        self.service_name = service_name
        self.tracer = None
        self.enabled = False
        
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available, tracing disabled")
            return
        
        self._initialize_tracer()
    
    def _initialize_tracer(self):
        """Initialize OpenTelemetry tracer"""
        try:
            # Get OTLP endpoint from environment
            otlp_endpoint = os.getenv('OTLP_ENDPOINT', 'http://localhost:4317')
            
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": os.getenv('SERVICE_VERSION', '1.0.0'),
            })
            
            # Create tracer provider
            provider = TracerProvider(resource=resource)
            
            # Add OTLP exporter if endpoint is configured
            if otlp_endpoint and otlp_endpoint != 'http://localhost:4317':
                otlp_exporter = OTLPSpanExporter(
                    endpoint=otlp_endpoint,
                    insecure=os.getenv('OTLP_INSECURE', 'false').lower() == 'true'
                )
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            else:
                # Use console exporter for development
                console_exporter = ConsoleSpanExporter()
                provider.add_span_processor(BatchSpanProcessor(console_exporter))
            
            # Set global tracer provider
            trace.set_tracer_provider(provider)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            self.enabled = True
            
            logger.info(f"Tracing initialized for service: {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self.enabled = False
    
    def get_tracer(self):
        """Get OpenTelemetry tracer"""
        if not self.enabled or not self.tracer:
            # Return a no-op tracer if tracing is disabled
            return trace.NoOpTracer()
        return self.tracer
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Start a new span
        
        Args:
            name: Span name
            attributes: Optional span attributes
            
        Returns:
            Span context manager
        """
        if not self.enabled:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        tracer = self.get_tracer()
        span = tracer.start_as_current_span(name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to current span"""
        if not self.enabled:
            return
        
        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """Set attribute on current span"""
        if not self.enabled:
            return
        
        span = trace.get_current_span()
        if span and span.is_recording():
            span.set_attribute(key, str(value))
    
    def set_status(self, status_code: str, description: Optional[str] = None):
        """
        Set span status
        
        Args:
            status_code: 'OK' or 'ERROR'
            description: Optional status description
        """
        if not self.enabled:
            return
        
        span = trace.get_current_span()
        if span and span.is_recording():
            from opentelemetry.trace import Status, StatusCode
            if status_code == 'ERROR':
                span.set_status(Status(StatusCode.ERROR, description))
            else:
                span.set_status(Status(StatusCode.OK))


# Global tracing service instance
_tracing_service: Optional[TracingService] = None


def get_tracing_service() -> TracingService:
    """Get global tracing service instance"""
    global _tracing_service
    if _tracing_service is None:
        _tracing_service = TracingService()
    return _tracing_service


def instrument_fastapi(app):
    """Instrument FastAPI application for tracing"""
    if not OPENTELEMETRY_AVAILABLE:
        return
    
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented for tracing")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


def instrument_requests():
    """Instrument requests library for tracing"""
    if not OPENTELEMETRY_AVAILABLE:
        return
    
    try:
        RequestsInstrumentor().instrument()
        logger.info("Requests library instrumented for tracing")
    except Exception as e:
        logger.error(f"Failed to instrument requests: {e}")


def instrument_aiohttp():
    """Instrument aiohttp for tracing"""
    if not OPENTELEMETRY_AVAILABLE:
        return
    
    try:
        AioHttpClientInstrumentor().instrument()
        logger.info("aiohttp instrumented for tracing")
    except Exception as e:
        logger.error(f"Failed to instrument aiohttp: {e}")

