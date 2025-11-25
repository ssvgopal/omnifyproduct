"""
Airbyte ETL/ELT Management Routes
API endpoints for managing data connectors, sync operations, and webhook handling
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel

from services.airbyte_etl import (
    airbyte_service, ConnectorConfig, ConnectorType, SyncType, WebhookEvent
)
from services.oidc_auth import get_current_user, TokenValidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/airbyte", tags=["Airbyte ETL/ELT Management"])

# Request/Response Models
class ConnectorRequest(BaseModel):
    """Request to create a connector"""
    connector_type: str
    name: str
    credentials: Dict[str, Any]
    sync_schedule: str = "0 */6 * * *"  # Every 6 hours
    sync_type: str = "incremental"
    enabled: bool = True

class SyncRequest(BaseModel):
    """Request to start a sync"""
    connector_id: str
    sync_type: Optional[str] = None

class WebhookRequest(BaseModel):
    """Webhook request"""
    event_type: str
    platform: str
    organization_id: str
    data: Dict[str, Any]
    signature: Optional[str] = None

class ConnectorResponse(BaseModel):
    """Connector response"""
    connector_id: str
    name: str
    type: str
    status: str
    created_at: str

class SyncResponse(BaseModel):
    """Sync response"""
    sync_id: str
    connector_id: str
    status: str
    started_at: str

class SyncStatusResponse(BaseModel):
    """Sync status response"""
    sync_id: str
    status: str
    records_synced: int
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None

class ConnectorStatsResponse(BaseModel):
    """Connector statistics response"""
    connector_id: str
    name: str
    type: str
    organization_id: str
    enabled: bool
    sync_schedule: str
    active_syncs: int
    last_sync: Optional[str] = None
    total_records_synced: int

# ========== AIRBYTE MANAGEMENT ROUTES ==========

@router.get("/health")
async def airbyte_health_check():
    """Check Airbyte service health"""
    try:
        return await airbyte_service.health_check()
    except Exception as e:
        logger.error(f"Airbyte health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Airbyte health check failed: {str(e)}"
        )

@router.post("/setup-default", response_model=Dict[str, Any])
async def setup_default_connectors(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Setup default connectors for organization"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled. Set ENABLE_AIRBYTE=true to enable."
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required for connector setup"
            )

        result = await airbyte_service.setup_default_connectors(current_user.organization_id)
        
        logger.info("Default connectors setup completed", extra={
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id,
            "connectors_created": len(result.get("connectors", []))
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to setup default connectors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup connectors: {str(e)}"
        )

@router.post("/connectors", response_model=ConnectorResponse)
async def create_connector(
    request: ConnectorRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new data connector"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Validate connector type
        try:
            connector_type = ConnectorType(request.connector_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid connector type: {request.connector_type}"
            )

        # Validate sync type
        try:
            sync_type = SyncType(request.sync_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sync type: {request.sync_type}"
            )

        # Create connector configuration
        config = ConnectorConfig(
            connector_type=connector_type,
            name=request.name,
            organization_id=current_user.organization_id,
            credentials=request.credentials,
            sync_schedule=request.sync_schedule,
            sync_type=sync_type,
            enabled=request.enabled
        )

        result = await airbyte_service.create_connector(config)
        
        return ConnectorResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create connector: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connector: {str(e)}"
        )

@router.post("/sync", response_model=SyncResponse)
async def start_sync(
    request: SyncRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Start a data sync operation"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        result = await airbyte_service.start_sync(request.connector_id, current_user.organization_id)
        
        logger.info("Sync started", extra={
            "sync_id": result["sync_id"],
            "connector_id": request.connector_id,
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id
        })

        return SyncResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start sync: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start sync: {str(e)}"
        )

@router.get("/sync/{sync_id}/status", response_model=SyncStatusResponse)
async def get_sync_status(
    sync_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get sync operation status"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        result = await airbyte_service.get_sync_status(sync_id)
        
        return SyncStatusResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )

@router.post("/sync/{sync_id}/cancel")
async def cancel_sync(
    sync_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Cancel a sync operation"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required to cancel syncs"
            )

        success = await airbyte_service.cancel_sync(sync_id)
        
        if success:
            logger.info("Sync cancelled", extra={
                "sync_id": sync_id,
                "user_id": current_user.user_id
            })
            
            return {
                "status": "success",
                "message": f"Sync {sync_id} cancelled successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel sync"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel sync: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel sync: {str(e)}"
        )

@router.get("/connectors/{connector_id}/stats", response_model=ConnectorStatsResponse)
async def get_connector_stats(
    connector_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get connector statistics"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        result = await airbyte_service.get_connector_stats(connector_id)
        
        return ConnectorStatsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connector stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connector stats: {str(e)}"
        )

@router.post("/webhooks/{platform}")
async def handle_webhook(
    platform: str,
    request: WebhookRequest,
    http_request: Request
):
    """Handle webhook events from external platforms"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        # Create webhook event
        event = WebhookEvent(
            event_type=request.event_type,
            platform=platform,
            organization_id=request.organization_id,
            data=request.data,
            timestamp=datetime.utcnow(),
            signature=request.signature
        )

        result = await airbyte_service.handle_webhook(event)
        
        logger.info("Webhook processed", extra={
            "platform": platform,
            "event_type": request.event_type,
            "organization_id": request.organization_id,
            "sync_triggered": result.get("sync_triggered", False)
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )

@router.get("/connectors")
async def list_connectors(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """List connectors for organization"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        # Filter connectors by organization
        org_connectors = [
            {
                "connector_id": cid,
                "name": config.name,
                "type": config.connector_type.value,
                "organization_id": config.organization_id,
                "enabled": config.enabled,
                "sync_schedule": config.sync_schedule,
                "sync_type": config.sync_type.value
            }
            for cid, config in airbyte_service.connector_configs.items()
            if config.organization_id == current_user.organization_id
        ]

        return {
            "connectors": org_connectors,
            "total": len(org_connectors),
            "organization_id": current_user.organization_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list connectors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list connectors: {str(e)}"
        )

@router.get("/syncs")
async def list_syncs(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """List sync operations for organization"""
    try:
        if not airbyte_service.enable_airbyte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airbyte is not enabled"
            )

        # Filter syncs by organization
        org_syncs = [
            {
                "sync_id": sync.sync_id,
                "connector_id": sync.connector_id,
                "status": sync.status.value,
                "records_synced": sync.records_synced,
                "started_at": sync.started_at.isoformat(),
                "completed_at": sync.completed_at.isoformat() if sync.completed_at else None,
                "duration_seconds": sync.duration_seconds,
                "error_message": sync.error_message
            }
            for sync in airbyte_service.active_syncs.values()
            if sync.organization_id == current_user.organization_id
        ]

        return {
            "syncs": org_syncs,
            "total": len(org_syncs),
            "organization_id": current_user.organization_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list syncs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list syncs: {str(e)}"
        )

@router.get("/configuration")
async def get_airbyte_configuration(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get Airbyte service configuration"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        return {
            "airbyte_enabled": airbyte_service.enable_airbyte,
            "airbyte_url": airbyte_service.airbyte_url,
            "sync_schedule": airbyte_service.sync_schedule,
            "timeout": airbyte_service.timeout,
            "active_connectors": len(airbyte_service.connector_configs),
            "active_syncs": len(airbyte_service.active_syncs),
            "supported_connectors": [ct.value for ct in ConnectorType],
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Airbyte configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )
