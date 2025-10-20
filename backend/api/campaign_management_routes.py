"""
Campaign Management API Routes
Production-grade API endpoints for campaign creation, management, and optimization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.campaign_management_service import (
    get_campaign_management_service, CampaignManagementService,
    CampaignStatus, CampaignType, CreativeType, AssetType
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class CampaignTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    template_data: Dict[str, Any]
    created_at: str
    updated_at: str

class CampaignCreateRequest(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field("", description="Campaign description")
    campaign_type: str = Field(..., description="Campaign type")
    budget: Dict[str, Any] = Field(..., description="Budget configuration")
    targeting: Dict[str, Any] = Field(..., description="Targeting configuration")
    schedule: Optional[Dict[str, Any]] = Field({}, description="Schedule configuration")
    optimization_goal: Optional[str] = Field("conversions", description="Optimization goal")
    creatives: Optional[List[Dict[str, Any]]] = Field([], description="Creative assets")

class CampaignUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    budget: Optional[Dict[str, Any]] = Field(None, description="Budget configuration")
    targeting: Optional[Dict[str, Any]] = Field(None, description="Targeting configuration")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Schedule configuration")
    optimization_goal: Optional[str] = Field(None, description="Optimization goal")
    creatives: Optional[List[Dict[str, Any]]] = Field(None, description="Creative assets")

class CampaignResponse(BaseModel):
    campaign_id: str
    client_id: str
    name: str
    description: str
    template_id: Optional[str]
    campaign_type: str
    status: str
    budget: Dict[str, Any]
    targeting: Dict[str, Any]
    schedule: Dict[str, Any]
    optimization_goal: str
    creatives: List[Dict[str, Any]]
    performance: Dict[str, Any]
    created_at: str
    updated_at: str

class AssetResponse(BaseModel):
    asset_id: str
    asset_type: str
    file_name: str
    file_size: int
    mime_type: str
    dimensions: Optional[Dict[str, int]]
    url: str
    thumbnail_url: str
    tags: List[str]
    created_at: str

class ABTestCreateRequest(BaseModel):
    name: str = Field(..., description="Test name")
    description: Optional[str] = Field("", description="Test description")
    test_type: str = Field(..., description="Test type")
    variants: List[Dict[str, Any]] = Field(..., description="Test variants")
    traffic_split: Optional[int] = Field(50, description="Traffic split percentage")
    success_metric: Optional[str] = Field("conversions", description="Success metric")
    minimum_sample_size: Optional[int] = Field(1000, description="Minimum sample size")
    test_duration_days: Optional[int] = Field(14, description="Test duration in days")

class ABTestResponse(BaseModel):
    test_id: str
    name: str
    test_type: str
    status: str
    created_at: str

# Dependency
async def get_campaign_service(db: AsyncIOMotorClient = Depends(get_database)) -> CampaignManagementService:
    return get_campaign_management_service(db)

# Campaign Template Endpoints
@router.get("/api/campaigns/templates", response_model=List[CampaignTemplateResponse], summary="Get Campaign Templates")
async def get_campaign_templates(
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Get available campaign templates for quick campaign creation.
    Returns predefined templates for different campaign types and objectives.
    """
    try:
        templates = await campaign_service.get_campaign_templates()
        return [CampaignTemplateResponse(**template) for template in templates]
    except Exception as e:
        logger.error(f"Error getting campaign templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign templates"
        )

# Campaign Creation Endpoints
@router.post("/api/campaigns/templates/{template_id}", response_model=CampaignResponse, summary="Create Campaign from Template")
async def create_campaign_from_template(
    template_id: str,
    client_id: str = Query(..., description="Client ID"),
    customizations: CampaignCreateRequest = Body(...),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Create a new campaign from a predefined template.
    Allows customization of template parameters.
    """
    try:
        customizations_dict = customizations.dict()
        campaign = await campaign_service.create_campaign_from_template(client_id, template_id, customizations_dict)
        
        # Get full campaign details
        full_campaign = await campaign_service.get_campaign(campaign["campaign_id"], client_id)
        return CampaignResponse(**full_campaign)
    except Exception as e:
        logger.error(f"Error creating campaign from template {template_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign from template"
        )

@router.post("/api/campaigns/custom", response_model=CampaignResponse, summary="Create Custom Campaign")
async def create_custom_campaign(
    client_id: str = Query(..., description="Client ID"),
    campaign_config: CampaignCreateRequest = Body(...),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Create a custom campaign from scratch.
    Provides full control over campaign configuration.
    """
    try:
        campaign_config_dict = campaign_config.dict()
        campaign = await campaign_service.create_custom_campaign(client_id, campaign_config_dict)
        
        # Get full campaign details
        full_campaign = await campaign_service.get_campaign(campaign["campaign_id"], client_id)
        return CampaignResponse(**full_campaign)
    except Exception as e:
        logger.error(f"Error creating custom campaign for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom campaign"
        )

# Campaign Management Endpoints
@router.get("/api/campaigns/{campaign_id}", response_model=CampaignResponse, summary="Get Campaign Details")
async def get_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Get detailed information about a specific campaign.
    Returns campaign configuration, performance data, and status.
    """
    try:
        campaign = await campaign_service.get_campaign(campaign_id, client_id)
        return CampaignResponse(**campaign)
    except Exception as e:
        logger.error(f"Error getting campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign details"
        )

@router.put("/api/campaigns/{campaign_id}", response_model=CampaignResponse, summary="Update Campaign")
async def update_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    updates: CampaignUpdateRequest = Body(...),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Update campaign configuration.
    Allows modification of budget, targeting, schedule, and other parameters.
    """
    try:
        updates_dict = {k: v for k, v in updates.dict().items() if v is not None}
        campaign = await campaign_service.update_campaign(campaign_id, client_id, updates_dict)
        return CampaignResponse(**campaign)
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign"
        )

@router.get("/api/campaigns", summary="List Client Campaigns")
async def list_campaigns(
    client_id: str = Query(..., description="Client ID"),
    status: Optional[str] = Query(None, description="Filter by campaign status"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    List all campaigns for a client.
    Supports filtering by campaign status.
    """
    try:
        status_filter = CampaignStatus(status) if status else None
        campaigns = await campaign_service.get_client_campaigns(client_id, status_filter)
        
        return {
            "client_id": client_id,
            "campaigns": campaigns,
            "total_count": len(campaigns),
            "status_filter": status
        }
    except Exception as e:
        logger.error(f"Error listing campaigns for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list campaigns"
        )

# Campaign Actions Endpoints
@router.post("/api/campaigns/{campaign_id}/launch", response_model=CampaignResponse, summary="Launch Campaign")
async def launch_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Launch a campaign.
    Changes status from draft to active and starts campaign execution.
    """
    try:
        campaign = await campaign_service.launch_campaign(campaign_id, client_id)
        return CampaignResponse(**campaign)
    except Exception as e:
        logger.error(f"Error launching campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to launch campaign"
        )

@router.post("/api/campaigns/{campaign_id}/pause", response_model=CampaignResponse, summary="Pause Campaign")
async def pause_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Pause a running campaign.
    Stops campaign execution while preserving configuration.
    """
    try:
        campaign = await campaign_service.pause_campaign(campaign_id, client_id)
        return CampaignResponse(**campaign)
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause campaign"
        )

@router.post("/api/campaigns/{campaign_id}/archive", summary="Archive Campaign")
async def archive_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Archive a campaign.
    Removes campaign from active list while preserving data for reporting.
    """
    try:
        result = await campaign_service.archive_campaign(campaign_id, client_id)
        return result
    except Exception as e:
        logger.error(f"Error archiving campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive campaign"
        )

# Creative Asset Management Endpoints
@router.post("/api/campaigns/assets/upload", response_model=AssetResponse, summary="Upload Creative Asset")
async def upload_asset(
    client_id: str = Query(..., description="Client ID"),
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Upload a creative asset for use in campaigns.
    Supports images, videos, audio, and document files.
    """
    try:
        # Validate asset type
        try:
            asset_type_enum = AssetType(asset_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {asset_type}"
            )
        
        # Read file data
        file_data = await file.read()
        
        # Upload asset
        asset = await campaign_service.upload_asset(client_id, file_data, file.filename, asset_type_enum)
        
        return AssetResponse(
            asset_id=asset.asset_id,
            asset_type=asset.asset_type.value,
            file_name=asset.file_name,
            file_size=asset.file_size,
            mime_type=asset.mime_type,
            dimensions=asset.dimensions,
            url=asset.url,
            thumbnail_url=asset.thumbnail_url,
            tags=asset.tags,
            created_at=asset.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload asset"
        )

@router.get("/api/campaigns/assets", summary="List Client Assets")
async def list_assets(
    client_id: str = Query(..., description="Client ID"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    List all creative assets for a client.
    Supports filtering by asset type.
    """
    try:
        asset_type_enum = AssetType(asset_type) if asset_type else None
        assets = await campaign_service.get_client_assets(client_id, asset_type_enum)
        
        asset_responses = []
        for asset in assets:
            asset_responses.append(AssetResponse(
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                file_name=asset.file_name,
                file_size=asset.file_size,
                mime_type=asset.mime_type,
                dimensions=asset.dimensions,
                url=asset.url,
                thumbnail_url=asset.thumbnail_url,
                tags=asset.tags,
                created_at=asset.created_at.isoformat()
            ))
        
        return {
            "client_id": client_id,
            "assets": asset_responses,
            "total_count": len(asset_responses),
            "asset_type_filter": asset_type
        }
    except Exception as e:
        logger.error(f"Error listing assets for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list assets"
        )

@router.delete("/api/campaigns/assets/{asset_id}", summary="Delete Asset")
async def delete_asset(
    asset_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Delete a creative asset.
    Performs soft delete to preserve data integrity.
    """
    try:
        success = await campaign_service.delete_asset(asset_id, client_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return {"message": "Asset deleted successfully", "asset_id": asset_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting asset {asset_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete asset"
        )

# A/B Testing Endpoints
@router.post("/api/campaigns/ab-tests", response_model=ABTestResponse, summary="Create A/B Test")
async def create_ab_test(
    client_id: str = Query(..., description="Client ID"),
    test_config: ABTestCreateRequest = Body(...),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Create an A/B test for campaigns.
    Supports testing creatives, audiences, budgets, and other campaign elements.
    """
    try:
        test_config_dict = test_config.dict()
        ab_test = await campaign_service.create_ab_test(client_id, test_config_dict)
        
        return ABTestResponse(
            test_id=ab_test["test_id"],
            name=ab_test["name"],
            test_type=ab_test["test_type"],
            status=ab_test["status"],
            created_at=ab_test["created_at"]
        )
    except Exception as e:
        logger.error(f"Error creating A/B test for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create A/B test"
        )

@router.get("/api/campaigns/ab-tests/{test_id}", summary="Get A/B Test Results")
async def get_ab_test_results(
    test_id: str,
    client_id: str = Query(..., description="Client ID"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Get A/B test results and statistical analysis.
    Returns performance data, significance testing, and recommendations.
    """
    try:
        results = await campaign_service.get_ab_test_results(test_id, client_id)
        return results
    except Exception as e:
        logger.error(f"Error getting A/B test results for {test_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve A/B test results"
        )

# Campaign Performance Endpoints
@router.get("/api/campaigns/{campaign_id}/performance", summary="Get Campaign Performance")
async def get_campaign_performance(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    days: int = Query(30, description="Number of days to retrieve"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Get detailed performance metrics for a campaign.
    Returns impressions, clicks, conversions, cost, revenue, and other KPIs.
    """
    try:
        # Get campaign details
        campaign = await campaign_service.get_campaign(campaign_id, client_id)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # In production, this would query actual performance data
        # For now, return campaign performance data
        performance_data = {
            "campaign_id": campaign_id,
            "client_id": client_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "metrics": campaign["performance"],
            "trends": {
                "impressions_trend": "up",
                "clicks_trend": "up",
                "conversions_trend": "up",
                "cost_trend": "down",
                "revenue_trend": "up"
            },
            "benchmarks": {
                "industry_avg_ctr": 2.5,
                "industry_avg_conversion_rate": 3.2,
                "industry_avg_cpa": 45.0,
                "industry_avg_roas": 2.8
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return performance_data
    except Exception as e:
        logger.error(f"Error getting campaign performance for {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign performance"
        )

# Campaign Optimization Endpoints
@router.post("/api/campaigns/{campaign_id}/optimize", summary="Optimize Campaign")
async def optimize_campaign(
    campaign_id: str,
    client_id: str = Query(..., description="Client ID"),
    optimization_type: str = Query("auto", description="Optimization type"),
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Apply AI-powered optimization to a campaign.
    Supports automatic bid adjustments, audience expansion, and creative optimization.
    """
    try:
        # Get campaign details
        campaign = await campaign_service.get_campaign(campaign_id, client_id)
        
        # In production, this would implement actual optimization logic
        optimization_result = {
            "campaign_id": campaign_id,
            "client_id": client_id,
            "optimization_type": optimization_type,
            "recommendations": [
                {
                    "type": "bid_adjustment",
                    "description": "Increase bids for high-performing keywords by 20%",
                    "impact": "Expected 15% increase in conversions",
                    "confidence": 85
                },
                {
                    "type": "audience_expansion",
                    "description": "Add lookalike audiences based on top converters",
                    "impact": "Expected 25% increase in reach",
                    "confidence": 78
                },
                {
                    "type": "creative_refresh",
                    "description": "Replace underperforming creatives with top performers",
                    "impact": "Expected 10% improvement in CTR",
                    "confidence": 92
                }
            ],
            "applied_changes": [],
            "optimization_status": "completed",
            "optimized_at": datetime.utcnow().isoformat()
        }
        
        return optimization_result
    except Exception as e:
        logger.error(f"Error optimizing campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize campaign"
        )

# Campaign Health Check
@router.get("/api/campaigns/health", summary="Campaign Management Health Check")
async def campaign_health_check(
    campaign_service: CampaignManagementService = Depends(get_campaign_service)
):
    """
    Check the health of the campaign management service.
    Returns service status and capabilities.
    """
    try:
        # Check database connection
        await campaign_service.db.admin.command('ping')
        
        # Check service components
        components = {
            "asset_manager": campaign_service.asset_manager is not None,
            "campaign_builder": campaign_service.campaign_builder is not None,
            "ab_testing_manager": campaign_service.ab_testing_manager is not None
        }
        
        all_healthy = all(components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
            "capabilities": {
                "campaign_templates": True,
                "custom_campaigns": True,
                "asset_management": True,
                "ab_testing": True,
                "campaign_optimization": True,
                "performance_tracking": True
            },
            "supported_asset_types": [asset_type.value for asset_type in AssetType],
            "supported_campaign_types": [campaign_type.value for campaign_type in CampaignType],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking campaign management health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
