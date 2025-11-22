"""
Structured Logging Configuration
Provides JSON logging with correlation IDs
"""

import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime
import structlog
from contextvars import ContextVar

# Correlation ID context variable
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

def get_correlation_id() -> str:
    """Get current correlation ID from context"""
    return correlation_id.get()

def set_correlation_id(cid: str):
    """Set correlation ID in context"""
    correlation_id.set(cid)


def configure_structured_logging(level: str = "INFO", json_output: bool = True):
    """
    Configure structured logging with correlation IDs
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output JSON logs (for production)
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # Add correlation ID
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class CorrelationIDMiddleware:
    """Middleware to extract and set correlation ID from headers"""
    
    async def __call__(self, request, call_next):
        # Extract correlation ID from header or generate new one
        cid = request.headers.get("X-Correlation-ID", "")
        if not cid:
            import uuid
            cid = str(uuid.uuid4())
        
        # Set in context
        set_correlation_id(cid)
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        
        return response

