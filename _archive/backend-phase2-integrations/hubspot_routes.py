"""
HubSpot API Routes
CRM and Marketing Automation platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from core.auth import get_current_user
from integrations.hubspot.client import HubSpotAdapter
from integrations.platform_manager import platform_integrations_manager, Platform

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/hubspot", tags=["HubSpot"])


class HubSpotConfigRequest(BaseModel):
    access_token: str
    base_url: Optional[str] = None


class CreateContactRequest(BaseModel):
    contact_data: Dict[str, Any]


class CreateCampaignRequest(BaseModel):
    campaign_data: Dict[str, Any]


class CreateWorkflowRequest(BaseModel):
    workflow_data: Dict[str, Any]


class TriggerWorkflowRequest(BaseModel):
    workflow_id: str
    contact_id: str


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


@router.post("/connect")
async def connect_hubspot(
    config: HubSpotConfigRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Connect HubSpot account"""
    try:
        organization_id = current_user["organization_id"]
        
        # Initialize adapter
        adapter = HubSpotAdapter()
        await adapter.initialize({
            "access_token": config.access_token,
            "base_url": config.base_url
        })
        
        # Test connection
        test_result = await adapter.test_connection(organization_id)
        if test_result.get("status") != "connected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to HubSpot: {test_result.get('error', 'Unknown error')}"
            )
        
        # Store credentials
        from services.production_secrets_manager import production_secrets_manager
        await production_secrets_manager.store_secret(
            f"platform_creds_{organization_id}_hubspot",
            {
                "access_token": config.access_token,
                "base_url": config.base_url or "https://api.hubapi.com"
            }
        )
        
        # Create integration record
        integration_record = {
            "integration_id": f"{organization_id}_hubspot",
            "organization_id": organization_id,
            "platform": "hubspot",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.platform_integrations.insert_one(integration_record)
        
        logger.info(f"HubSpot connected for organization {organization_id}")
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_record["integration_id"],
                "platform": "hubspot",
                "status": "connected"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to connect HubSpot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect HubSpot: {str(e)}"
        )


@router.post("/contacts")
async def create_contact(
    request: CreateContactRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a contact in HubSpot CRM"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.HUBSPOT,
            "create_contact",
            organization_id,
            {
                "contact_data": request.contact_data
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create HubSpot contact: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contact: {str(e)}"
        )


@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a marketing campaign in HubSpot"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.HUBSPOT,
            "create_campaign",
            organization_id,
            {
                "campaign_data": request.campaign_data
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create HubSpot campaign: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.post("/workflows")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a marketing automation workflow in HubSpot"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.HUBSPOT,
            "create_workflow",
            organization_id,
            {
                "workflow_data": request.workflow_data
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create HubSpot workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/workflows/trigger")
async def trigger_workflow(
    request: TriggerWorkflowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Trigger a workflow for a contact"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.HUBSPOT,
            "trigger_workflow",
            organization_id,
            {
                "workflow_id": request.workflow_id,
                "contact_id": request.contact_id
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger HubSpot workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}"
        )


@router.get("/analytics")
async def get_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    object_type: str = Query("contacts", description="Object type (contacts, deals, companies, etc.)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get analytics data from HubSpot"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.HUBSPOT,
            "get_analytics",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "object_type": object_type
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get HubSpot analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/status")
async def get_hubspot_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get HubSpot integration status"""
    try:
        organization_id = current_user["organization_id"]
        
        status_result = await platform_integrations_manager.get_platform_status(
            organization_id,
            Platform.HUBSPOT
        )
        
        return {
            "success": True,
            "data": status_result
        }
        
    except Exception as e:
        logger.error(f"Failed to get HubSpot status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )

