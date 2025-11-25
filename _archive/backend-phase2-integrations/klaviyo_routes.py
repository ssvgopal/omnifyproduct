"""
Klaviyo API Routes
Lifecycle Marketing and Retention platform
Note: Klaviyo uses API keys, not OAuth2
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from core.auth import get_current_user
from integrations.klaviyo.client import KlaviyoAdapter
from integrations.platform_manager import platform_integrations_manager, Platform

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/klaviyo", tags=["Klaviyo"])


class KlaviyoConfigRequest(BaseModel):
    api_key: str
    base_url: Optional[str] = None


class CreateCampaignRequest(BaseModel):
    campaign_data: Dict[str, Any]


class CreateFlowRequest(BaseModel):
    flow_data: Dict[str, Any]


class TriggerFlowRequest(BaseModel):
    flow_id: str
    profile_id: str


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


@router.post("/connect")
async def connect_klaviyo(
    config: KlaviyoConfigRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Connect Klaviyo account (API key authentication)"""
    try:
        organization_id = current_user["organization_id"]
        
        # Initialize adapter
        adapter = KlaviyoAdapter()
        await adapter.initialize({
            "api_key": config.api_key,
            "base_url": config.base_url
        })
        
        # Test connection
        test_result = await adapter.test_connection(organization_id)
        if test_result.get("status") != "connected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to Klaviyo: {test_result.get('error', 'Unknown error')}"
            )
        
        # Store credentials
        from services.production_secrets_manager import production_secrets_manager
        await production_secrets_manager.store_secret(
            f"platform_creds_{organization_id}_klaviyo",
            {
                "api_key": config.api_key,
                "base_url": config.base_url or "https://a.klaviyo.com/api"
            }
        )
        
        # Create integration record
        integration_record = {
            "integration_id": f"{organization_id}_klaviyo",
            "organization_id": organization_id,
            "platform": "klaviyo",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.platform_integrations.insert_one(integration_record)
        
        logger.info(f"Klaviyo connected for organization {organization_id}")
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_record["integration_id"],
                "platform": "klaviyo",
                "status": "connected"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to connect Klaviyo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect Klaviyo: {str(e)}"
        )


@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create an email/SMS campaign in Klaviyo"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.KLAVIYO,
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
        logger.error(f"Failed to create Klaviyo campaign: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.post("/flows")
async def create_flow(
    request: CreateFlowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a lifecycle automation flow in Klaviyo"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.KLAVIYO,
            "create_flow",
            organization_id,
            {
                "flow_data": request.flow_data
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create Klaviyo flow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create flow: {str(e)}"
        )


@router.post("/flows/trigger")
async def trigger_flow(
    request: TriggerFlowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Trigger a flow for a profile"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.KLAVIYO,
            "trigger_flow",
            organization_id,
            {
                "flow_id": request.flow_id,
                "profile_id": request.profile_id
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger Klaviyo flow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger flow: {str(e)}"
        )


@router.get("/analytics")
async def get_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    metric_type: str = Query("email", description="Metric type (email, sms, etc.)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get analytics data from Klaviyo"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.KLAVIYO,
            "get_analytics",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "metric_type": metric_type
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get Klaviyo analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/status")
async def get_klaviyo_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get Klaviyo integration status"""
    try:
        organization_id = current_user["organization_id"]
        
        status_result = await platform_integrations_manager.get_platform_status(
            organization_id,
            Platform.KLAVIYO
        )
        
        return {
            "success": True,
            "data": status_result
        }
        
    except Exception as e:
        logger.error(f"Failed to get Klaviyo status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )

