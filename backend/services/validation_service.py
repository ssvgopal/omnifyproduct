"""
Comprehensive Input Validation and Error Handling for OmnifyProduct
"""

import re
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, validator, Field, ValidationError
from fastapi import HTTPException, status
import json

logger = logging.getLogger(__name__)


class ValidationError(HTTPException):
    """Custom validation error"""
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation Error", "field": field, "message": detail}
        )


class BusinessLogicError(HTTPException):
    """Custom business logic error"""
    def __init__(self, detail: str, code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": code, "message": detail}
        )


class NotFoundError(HTTPException):
    """Custom not found error"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "resource": resource, "identifier": identifier}
        )


class ValidationService:
    """Service for comprehensive input validation"""

    # Email regex pattern (RFC 5322 compliant)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # Phone number patterns for different formats
    PHONE_PATTERNS = {
        'us': re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
        'international': re.compile(r'^\+[1-9]\d{1,14}$')
    }

    # URL pattern
    URL_PATTERN = re.compile(
        r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?$'
    )

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not email or not isinstance(email, str):
            raise ValidationError("Email must be a non-empty string", "email")

        email = email.strip().lower()
        if len(email) > 254:  # RFC 5321 limit
            raise ValidationError("Email too long", "email")

        if not ValidationService.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format", "email")

        return email

    @staticmethod
    def validate_phone(phone: str, format_type: str = 'us') -> str:
        """Validate phone number"""
        if not phone or not isinstance(phone, str):
            raise ValidationError("Phone must be a non-empty string", "phone")

        phone = re.sub(r'[^\d+]', '', phone)  # Remove non-digit characters except +

        if format_type in ValidationService.PHONE_PATTERNS:
            if not ValidationService.PHONE_PATTERNS[format_type].match(phone):
                raise ValidationError(f"Invalid phone format for {format_type}", "phone")
        elif not ValidationService.PHONE_PATTERNS['international'].match(phone):
            raise ValidationError("Invalid international phone format", "phone")

        return phone

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string", "url")

        url = url.strip()
        if not ValidationService.URL_PATTERN.match(url):
            raise ValidationError("Invalid URL format", "url")

        return url

    @staticmethod
    def validate_organization_id(org_id: str) -> str:
        """Validate organization ID format"""
        if not org_id or not isinstance(org_id, str):
            raise ValidationError("Organization ID must be a non-empty string", "organization_id")

        if len(org_id) < 3 or len(org_id) > 50:
            raise ValidationError("Organization ID must be between 3-50 characters", "organization_id")

        # Allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', org_id):
            raise ValidationError("Organization ID can only contain letters, numbers, hyphens, and underscores", "organization_id")

        return org_id

    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validate user ID format"""
        if not user_id or not isinstance(user_id, str):
            raise ValidationError("User ID must be a non-empty string", "user_id")

        if len(user_id) < 3 or len(user_id) > 50:
            raise ValidationError("User ID must be between 3-50 characters", "user_id")

        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            raise ValidationError("User ID can only contain letters, numbers, hyphens, and underscores", "user_id")

        return user_id

    @staticmethod
    def validate_campaign_data(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign configuration data"""
        required_fields = ['name', 'objective']
        for field in required_fields:
            if field not in campaign_data:
                raise ValidationError(f"Campaign data missing required field: {field}", field)

        # Validate campaign name
        if not isinstance(campaign_data['name'], str) or len(campaign_data['name']) < 3:
            raise ValidationError("Campaign name must be at least 3 characters", "name")

        # Validate objective
        valid_objectives = ['awareness', 'traffic', 'engagement', 'leads', 'sales', 'conversions']
        if campaign_data['objective'] not in valid_objectives:
            raise ValidationError(f"Invalid campaign objective. Must be one of: {valid_objectives}", "objective")

        # Validate budget if present
        if 'budget_daily' in campaign_data:
            budget = campaign_data['budget_daily']
            if not isinstance(budget, (int, float)) or budget <= 0:
                raise ValidationError("Daily budget must be a positive number", "budget_daily")

        return campaign_data

    @staticmethod
    def validate_agent_config(agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent configuration"""
        required_fields = ['name', 'agent_type']
        for field in required_fields:
            if field not in agent_config:
                raise ValidationError(f"Agent config missing required field: {field}", field)

        # Validate agent name
        if not isinstance(agent_config['name'], str) or len(agent_config['name']) < 3:
            raise ValidationError("Agent name must be at least 3 characters", "name")

        # Validate agent type
        valid_types = ['creative_intelligence', 'marketing_automation', 'client_management', 'analytics']
        if agent_config['agent_type'] not in valid_types:
            raise ValidationError(f"Invalid agent type. Must be one of: {valid_types}", "agent_type")

        # Validate config structure
        if 'config' in agent_config and not isinstance(agent_config['config'], dict):
            raise ValidationError("Agent config must be a dictionary", "config")

        return agent_config

    @staticmethod
    def validate_workflow_data(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration"""
        required_fields = ['name', 'steps']
        for field in required_fields:
            if field not in workflow_data:
                raise ValidationError(f"Workflow data missing required field: {field}", field)

        # Validate workflow name
        if not isinstance(workflow_data['name'], str) or len(workflow_data['name']) < 3:
            raise ValidationError("Workflow name must be at least 3 characters", "name")

        # Validate steps
        if not isinstance(workflow_data['steps'], list) or len(workflow_data['steps']) == 0:
            raise ValidationError("Workflow must have at least one step", "steps")

        for i, step in enumerate(workflow_data['steps']):
            if not isinstance(step, dict):
                raise ValidationError(f"Step {i} must be a dictionary", f"steps[{i}]")

            if 'step_id' not in step:
                raise ValidationError(f"Step {i} missing step_id", f"steps[{i}].step_id")

            if 'agent_type' not in step:
                raise ValidationError(f"Step {i} missing agent_type", f"steps[{i}].agent_type")

        return workflow_data

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
        """Validate date range"""
        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")

        # Limit to reasonable range (not too far in the past/future)
        now = datetime.utcnow()
        if start_date < now.replace(year=now.year - 2):
            raise ValidationError("Start date cannot be more than 2 years in the past")

        if end_date > now.replace(year=now.year + 1):
            raise ValidationError("End date cannot be more than 1 year in the future")

        return start_date, end_date


class ErrorHandler:
    """Comprehensive error handling service"""

    @staticmethod
    def handle_validation_error(error: ValidationError) -> HTTPException:
        """Handle Pydantic validation errors"""
        logger.error(f"Validation error: {error}")
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Validation Error",
                "details": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def handle_database_error(error: Exception) -> HTTPException:
        """Handle database-related errors"""
        logger.error(f"Database error: {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database Error",
                "message": "A database error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def handle_external_service_error(error: Exception, service: str) -> HTTPException:
        """Handle external service errors"""
        logger.error(f"External service error ({service}): {error}")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "External Service Error",
                "service": service,
                "message": f"{service} service is currently unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def handle_rate_limit_error() -> HTTPException:
        """Handle rate limiting"""
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate Limit Exceeded",
                "message": "Too many requests. Please try again later.",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def handle_authentication_error(error: str = "Authentication failed") -> HTTPException:
        """Handle authentication errors"""
        logger.warning(f"Authentication error: {error}")
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Authentication Error",
                "message": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def handle_authorization_error(error: str = "Insufficient permissions") -> HTTPException:
        """Handle authorization errors"""
        logger.warning(f"Authorization error: {error}")
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Authorization Error",
                "message": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


def validate_request_data(data: Dict[str, Any], schema_class: type[BaseModel]) -> BaseModel:
    """Validate request data against a Pydantic schema"""
    try:
        return schema_class(**data)
    except ValidationError as e:
        logger.error(f"Schema validation error: {e}")
        raise ValidationError(f"Invalid data format: {e}")


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Expected string value")

    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', value)

    # Trim whitespace
    sanitized = sanitized.strip()

    # Check length
    if len(sanitized) > max_length:
        raise ValidationError(f"String too long (max {max_length} characters)")

    return sanitized


def validate_json_field(value: Any, field_name: str) -> Any:
    """Validate and parse JSON field"""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValidationError(f"Invalid JSON in field {field_name}", field_name)
    elif isinstance(value, (dict, list)):
        return value
    else:
        raise ValidationError(f"Field {field_name} must be valid JSON", field_name)


# Common Pydantic models for validation
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=20)

    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v


class DateRangeParams(BaseModel):
    """Date range parameters"""
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class OrganizationCreate(BaseModel):
    """Organization creation model"""
    name: str = Field(min_length=3, max_length=100)
    slug: str = Field(min_length=3, max_length=50, regex=r'^[a-z0-9-]+$')
    subscription_tier: str = Field(default="starter", regex=r'^(starter|professional|enterprise)$')

    @validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug can only contain lowercase letters, numbers, and hyphens')
        return v


class UserCreate(BaseModel):
    """User creation model"""
    email: str
    password: str
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    organization_id: str

    @validator('email')
    def validate_email(cls, v):
        return ValidationService.validate_email(v)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('organization_id')
    def validate_org_id(cls, v):
        return ValidationService.validate_organization_id(v)
