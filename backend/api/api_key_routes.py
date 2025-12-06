"""
API Key Management Routes
Handles API endpoints for managing platform API keys and integrations
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from services.api_key_service import api_key_service

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# ========== REQUEST/RESPONSE MODELS ==========

class APIKeyCreate(BaseModel):
    """Request model for creating/updating an API key"""
    organization_id: str = Field(..., description="Organization UUID")
    platform: str = Field(..., description="Platform name (openai, gemini, meta_ads, etc.)")
    key_name: str = Field(..., description="Key identifier (api_key, access_token, etc.)")
    key_value: str = Field(..., description="The actual key value (will be encrypted)")
    is_active: bool = Field(default=True, description="Whether the key is active")


class APIKeyBulkCreate(BaseModel):
    """Request model for saving multiple API keys for a platform"""
    organization_id: str = Field(..., description="Organization UUID")
    platform: str = Field(..., description="Platform name")
    keys: Dict[str, str] = Field(..., description="Dictionary of key_name: key_value")


class APIKeyDelete(BaseModel):
    """Request model for deleting an API key"""
    organization_id: str
    platform: str
    key_name: str


class TestConnectionRequest(BaseModel):
    """Request model for testing platform connection"""
    organization_id: str
    platform: str


# ========== ROUTES ==========

@router.post("/save")
async def save_api_key(request: APIKeyCreate):
    """
    Save or update a single API key
    
    - **organization_id**: Organization UUID
    - **platform**: Platform name (openai, gemini, meta_ads, etc.)
    - **key_name**: Key identifier (api_key, access_token, etc.)
    - **key_value**: The actual key value (will be encrypted)
    - **is_active**: Whether the key is active
    """
    result = await api_key_service.save_api_key(
        organization_id=request.organization_id,
        platform=request.platform,
        key_name=request.key_name,
        key_value=request.key_value,
        is_active=request.is_active
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to save API key'))
    
    return result


@router.post("/save-bulk")
async def save_bulk_api_keys(request: APIKeyBulkCreate):
    """
    Save multiple API keys for a platform at once
    
    Example:
    ```json
    {
        "organization_id": "uuid",
        "platform": "openai",
        "keys": {
            "api_key": "sk-..."
        }
    }
    ```
    """
    results = []
    errors = []
    
    for key_name, key_value in request.keys.items():
        result = await api_key_service.save_api_key(
            organization_id=request.organization_id,
            platform=request.platform,
            key_name=key_name,
            key_value=key_value
        )
        
        if result['success']:
            results.append(result)
        else:
            errors.append({
                'key_name': key_name,
                'error': result.get('error')
            })
    
    return {
        'success': len(errors) == 0,
        'saved': len(results),
        'errors': errors,
        'message': f'Saved {len(results)} API keys for {request.platform}'
    }


@router.get("/get/{organization_id}/{platform}/{key_name}")
async def get_api_key(organization_id: str, platform: str, key_name: str):
    """
    Get a specific API key (returns masked value for security)
    
    **Note**: This endpoint returns a masked version of the key for security.
    Use the actual key retrieval in backend services only.
    """
    key_value = await api_key_service.get_api_key(organization_id, platform, key_name)
    
    if key_value is None:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Return masked value for security
    masked_value = f"{key_value[:8]}...{key_value[-4:]}" if len(key_value) > 12 else "***"
    
    return {
        'platform': platform,
        'key_name': key_name,
        'key_value_masked': masked_value,
        'exists': True
    }


@router.get("/list/{organization_id}")
async def list_configured_platforms(organization_id: str):
    """
    List all platforms with configured API keys for an organization
    
    Returns:
    - List of platforms with their configuration status
    - Key names (not values) for each platform
    - Last updated timestamp
    """
    platforms = await api_key_service.list_configured_platforms(organization_id)
    
    return {
        'organization_id': organization_id,
        'platforms': platforms,
        'total': len(platforms)
    }


@router.delete("/delete")
async def delete_api_key(request: APIKeyDelete):
    """
    Delete a specific API key
    
    - **organization_id**: Organization UUID
    - **platform**: Platform name
    - **key_name**: Key identifier
    """
    result = await api_key_service.delete_api_key(
        organization_id=request.organization_id,
        platform=request.platform,
        key_name=request.key_name
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to delete API key'))
    
    return result


@router.post("/test-connection")
async def test_connection(request: TestConnectionRequest):
    """
    Test connection to a platform using stored API keys
    
    This endpoint will:
    1. Retrieve the API keys for the platform
    2. Make a test API call to verify connectivity
    3. Return connection status and any error messages
    
    - **organization_id**: Organization UUID
    - **platform**: Platform name (openai, gemini, meta_ads, etc.)
    """
    result = await api_key_service.test_connection(
        organization_id=request.organization_id,
        platform=request.platform
    )
    
    return result


@router.get("/status/{organization_id}/{platform}")
async def get_platform_status(organization_id: str, platform: str):
    """
    Get the configuration status for a specific platform
    
    Returns:
    - Whether API keys are configured
    - List of configured key names
    - Connection status (if tested)
    """
    keys = await api_key_service.get_all_keys_for_platform(organization_id, platform)
    
    if not keys:
        return {
            'platform': platform,
            'configured': False,
            'keys': [],
            'message': f'No API keys configured for {platform}'
        }
    
    return {
        'platform': platform,
        'configured': True,
        'keys': list(keys.keys()),
        'message': f'{len(keys)} API key(s) configured for {platform}'
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for API key service"""
    return {
        'status': 'healthy',
        'service': 'api_key_service',
        'message': 'API Key Management service is operational'
    }
