"""
TripleWhale API Routes
Attribution and analytics platform for DTC brands
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from core.auth import get_current_user
from integrations.triplewhale.client import TripleWhaleAdapter
from integrations.platform_manager import platform_integrations_manager, Platform

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/triplewhale", tags=["TripleWhale"])


class TripleWhaleConfigRequest(BaseModel):
    api_key: str
    base_url: Optional[str] = None


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


@router.post("/connect")
async def connect_triplewhale(
    config: TripleWhaleConfigRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Connect TripleWhale account"""
    try:
        organization_id = current_user["organization_id"]
        
        # Initialize adapter
        adapter = TripleWhaleAdapter()
        await adapter.initialize({
            "api_key": config.api_key,
            "base_url": config.base_url
        })
        
        # Test connection
        test_result = await adapter.test_connection(organization_id)
        if test_result.get("status") != "connected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to TripleWhale: {test_result.get('error', 'Unknown error')}"
            )
        
        # Store credentials
        from services.production_secrets_manager import production_secrets_manager
        await production_secrets_manager.store_secret(
            f"platform_creds_{organization_id}_triplewhale",
            {
                "api_key": config.api_key,
                "base_url": config.base_url or "https://api.triplewhale.com/v1"
            }
        )
        
        # Create integration record
        integration_record = {
            "integration_id": f"{organization_id}_triplewhale",
            "organization_id": organization_id,
            "platform": "triplewhale",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.platform_integrations.insert_one(integration_record)
        
        logger.info(f"TripleWhale connected for organization {organization_id}")
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_record["integration_id"],
                "platform": "triplewhale",
                "status": "connected"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to connect TripleWhale: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect TripleWhale: {str(e)}"
        )


@router.get("/attribution")
async def get_attribution(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    channel: Optional[str] = Query(None, description="Channel filter (meta, google, tiktok, etc.)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get attribution data from TripleWhale"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.TRIPLEWHALE,
            "get_attribution",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "channel": channel
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get TripleWhale attribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribution: {str(e)}"
        )


@router.get("/revenue")
async def get_revenue_metrics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    breakdown: Optional[str] = Query(None, description="Breakdown (channel, campaign, creative, etc.)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get revenue metrics from TripleWhale (ROAS, CLV, LTV)"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.TRIPLEWHALE,
            "get_revenue_metrics",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "breakdown": breakdown
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get TripleWhale revenue metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revenue metrics: {str(e)}"
        )


@router.get("/creatives/performance")
async def get_creative_performance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    channel: Optional[str] = Query(None, description="Channel filter"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get creative performance data for ORACLE module (fatigue prediction)"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.TRIPLEWHALE,
            "get_creative_performance",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "channel": channel
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get TripleWhale creative performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get creative performance: {str(e)}"
        )


@router.get("/roas")
async def get_roas(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    channel: Optional[str] = Query(None, description="Channel filter"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get ROAS data from TripleWhale"""
    try:
        organization_id = current_user["organization_id"]
        
        result = await platform_integrations_manager.execute_platform_action(
            Platform.TRIPLEWHALE,
            "get_roas",
            organization_id,
            {
                "start_date": start_date,
                "end_date": end_date,
                "channel": channel
            }
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get TripleWhale ROAS: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ROAS: {str(e)}"
        )


@router.get("/status")
async def get_triplewhale_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get TripleWhale integration status"""
    try:
        organization_id = current_user["organization_id"]
        
        status_result = await platform_integrations_manager.get_platform_status(
            organization_id,
            Platform.TRIPLEWHALE
        )
        
        return {
            "success": True,
            "data": status_result
        }
        
    except Exception as e:
        logger.error(f"Failed to get TripleWhale status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )

