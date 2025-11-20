"""
API Versioning Support
Provides version management for API endpoints
"""

from fastapi import APIRouter, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Current API version
CURRENT_API_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1"]


def get_api_version(request: Request) -> str:
    """
    Get API version from request
    
    Checks in order:
    1. URL path (/api/v1/...)
    2. Header (X-API-Version)
    3. Query parameter (?version=v1)
    4. Defaults to current version
    
    Args:
        request: FastAPI request object
        
    Returns:
        API version string
    """
    # Check URL path
    path = request.url.path
    for version in SUPPORTED_VERSIONS:
        if f"/api/{version}/" in path:
            return version
    
    # Check header
    version_header = request.headers.get("X-API-Version")
    if version_header and version_header in SUPPORTED_VERSIONS:
        return version_header
    
    # Check query parameter
    version_param = request.query_params.get("version")
    if version_param and version_param in SUPPORTED_VERSIONS:
        return version_param
    
    # Default to current version
    return CURRENT_API_VERSION


def create_versioned_router(version: str = CURRENT_API_VERSION) -> APIRouter:
    """
    Create a versioned API router
    
    Args:
        version: API version (defaults to current)
        
    Returns:
        APIRouter with version prefix
    """
    if version not in SUPPORTED_VERSIONS:
        logger.warning(f"Unsupported API version: {version}, using {CURRENT_API_VERSION}")
        version = CURRENT_API_VERSION
    
    return APIRouter(prefix=f"/api/{version}", tags=[f"API {version}"])


def validate_api_version(version: Optional[str]) -> str:
    """
    Validate and return API version
    
    Args:
        version: Version to validate
        
    Returns:
        Validated version string
        
    Raises:
        ValueError: If version is not supported
    """
    if version is None:
        return CURRENT_API_VERSION
    
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(f"Unsupported API version: {version}. Supported versions: {SUPPORTED_VERSIONS}")
    
    return version

