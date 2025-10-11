"""
Structured Logging Service for OmnifyProduct
Provides comprehensive tracing and logging capabilities
"""

import logging
import json
import uuid
import time
from datetime import datetime
from contextvars import ContextVar
from typing import Optional, Dict, Any
from pathlib import Path
import os

# Context variables for distributed tracing
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
organization_id: ContextVar[Optional[str]] = ContextVar('organization_id', default=None)
workflow_id: ContextVar[Optional[str]] = ContextVar('workflow_id', default=None)
session_id: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

class StructuredLogger:
    """
    Enhanced logging service with structured JSON output,
    correlation IDs, and tracing capabilities
    """

    def __init__(self, name: str, log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create formatters
        json_formatter = JSONFormatter()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

        # File handler for production logging
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(json_formatter)
            file_handler.setLevel(logging.INFO)
            self.logger.addHandler(file_handler)
        else:
            # Default file logging
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / f"{name}.log")
            file_handler.setFormatter(json_formatter)
            file_handler.setLevel(logging.INFO)
            self.logger.addHandler(file_handler)

        # Prevent duplicate logs from parent loggers
        self.logger.propagate = False

    def _get_context(self) -> Dict[str, Any]:
        """Get current tracing context"""
        context = {}
        try:
            if request_id.get():
                context['request_id'] = request_id.get()
            if user_id.get():
                context['user_id'] = user_id.get()
            if organization_id.get():
                context['organization_id'] = organization_id.get()
            if workflow_id.get():
                context['workflow_id'] = workflow_id.get()
            if session_id.get():
                context['session_id'] = session_id.get()
        except LookupError:
            pass
        return context

    def _log(self, level: int, message: str, event_type: Optional[str] = None,
             extra: Optional[Dict[str, Any]] = None, exc_info=None):
        """Internal logging method"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': logging.getLevelName(level),
            'logger': self.name,
            'message': message,
            'context': self._get_context()
        }

        if event_type:
            log_data['event_type'] = event_type

        if extra:
            log_data.update(extra)

        # Add exception info if provided
        if exc_info:
            log_data['exception'] = str(exc_info)
            if hasattr(exc_info, '__traceback__'):
                import traceback
                log_data['traceback'] = traceback.format_exception(
                    type(exc_info), exc_info, exc_info.__traceback__
                )

        # Log the structured data
        self.logger.log(level, json.dumps(log_data), exc_info=exc_info)

    def debug(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Debug level logging"""
        self._log(logging.DEBUG, message, event_type, kwargs)

    def info(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Info level logging"""
        self._log(logging.INFO, message, event_type, kwargs)

    def warning(self, message: str, event_type: Optional[str] = None, **kwargs):
        """Warning level logging"""
        self._log(logging.WARNING, message, event_type, kwargs)

    def error(self, message: str, event_type: Optional[str] = None,
              exc_info=None, **kwargs):
        """Error level logging with exception support"""
        self._log(logging.ERROR, message, event_type, kwargs, exc_info)

    def critical(self, message: str, event_type: Optional[str] = None,
                 exc_info=None, **kwargs):
        """Critical level logging"""
        self._log(logging.CRITICAL, message, event_type, kwargs, exc_info)

    # Specialized logging methods for OmnifyProduct

    def request_start(self, method: str, path: str, **kwargs):
        """Log API request start"""
        request_id.set(str(uuid.uuid4()))
        self.info(
            f"API Request started: {method} {path}",
            event_type='request_start',
            method=method,
            path=path,
            **kwargs
        )

    def request_complete(self, method: str, path: str, status_code: int,
                        duration_ms: float, **kwargs):
        """Log API request completion"""
        self.info(
            f"API Request completed: {method} {path}",
            event_type='request_complete',
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )

    def request_error(self, method: str, path: str, error: str,
                     duration_ms: float, **kwargs):
        """Log API request error"""
        self.error(
            f"API Request failed: {method} {path}",
            event_type='request_error',
            method=method,
            path=path,
            error=error,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )

    def workflow_start(self, workflow_id: str, user_id: str = None, **kwargs):
        """Log workflow execution start"""
        if user_id:
            user_id.set(user_id)
        workflow_id.set(workflow_id)

        self.info(
            f"Workflow {workflow_id} execution started",
            event_type='workflow_start',
            workflow_id=workflow_id,
            **kwargs
        )

    def workflow_step(self, step_id: str, status: str, **kwargs):
        """Log workflow step execution"""
        self.info(
            f"Workflow step {step_id}: {status}",
            event_type='workflow_step',
            step_id=step_id,
            step_status=status,
            **kwargs
        )

    def workflow_complete(self, workflow_id: str, total_steps: int,
                         duration_ms: float, **kwargs):
        """Log workflow execution completion"""
        self.info(
            f"Workflow {workflow_id} completed successfully",
            event_type='workflow_complete',
            workflow_id=workflow_id,
            total_steps=total_steps,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )

    def workflow_error(self, workflow_id: str, error: str,
                      step_id: Optional[str] = None, **kwargs):
        """Log workflow execution error"""
        self.error(
            f"Workflow {workflow_id} failed",
            event_type='workflow_error',
            workflow_id=workflow_id,
            error=error,
            step_id=step_id,
            **kwargs
        )

    def agent_execution_start(self, agent_id: str, agent_type: str, **kwargs):
        """Log agent execution start"""
        self.info(
            f"Agent {agent_id} ({agent_type}) execution started",
            event_type='agent_execution_start',
            agent_id=agent_id,
            agent_type=agent_type,
            **kwargs
        )

    def agent_execution_complete(self, agent_id: str, agent_type: str,
                                duration_ms: float, **kwargs):
        """Log agent execution completion"""
        self.info(
            f"Agent {agent_id} ({agent_type}) execution completed",
            event_type='agent_execution_complete',
            agent_id=agent_id,
            agent_type=agent_type,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )

    def agent_execution_error(self, agent_id: str, agent_type: str,
                             error: str, **kwargs):
        """Log agent execution error"""
        self.error(
            f"Agent {agent_id} ({agent_type}) execution failed",
            event_type='agent_execution_error',
            agent_id=agent_id,
            agent_type=agent_type,
            error=error,
            **kwargs
        )

    def database_query(self, operation: str, collection: str,
                      duration_ms: float, **kwargs):
        """Log database operations"""
        self.info(
            f"Database {operation} on {collection}",
            event_type='database_operation',
            operation=operation,
            collection=collection,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )

    def external_api_call(self, service: str, endpoint: str,
                         duration_ms: float, success: bool, **kwargs):
        """Log external API calls"""
        level = logging.INFO if success else logging.ERROR
        event_type = 'external_api_success' if success else 'external_api_error'

        log_method = self.info if success else self.error
        log_method(
            f"External API call to {service}: {endpoint}",
            event_type=event_type,
            service=service,
            endpoint=endpoint,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        # Try to parse if it's already JSON
        try:
            # If the message is JSON, parse and return it
            if record.getMessage().startswith('{'):
                return record.getMessage()
        except:
            pass

        # Create standard log record
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


# Global logger instance
logger = StructuredLogger(__name__, log_file="logs/omnify.log")
