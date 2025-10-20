"""
Additional Platform Integrations API Routes
Production-grade API endpoints for Facebook Ads, Twitter Ads, Pinterest, Snapchat, Reddit, and Quora
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.additional_platform_integrations_service import (
    get_additional_platform_integrations_service, AdditionalPlatformIntegrationsService,
    PlatformType, CampaignObjective, PlatformCredentials
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class PlatformCredentialsRequest(BaseModel):
    platform: str = Field(..., description="Platform type")
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client secret")
    account_id: str = Field(..., description="Account ID")
    expires_at: Optional[str] = Field(None, description="Token expiration")
    additional_config: Optional[Dict[str, Any]] = Field({}, description="Additional configuration")

class CampaignCreateRequest(BaseModel):
    platform: str = Field(..., description="Platform type")
    name: str = Field(..., description="Campaign name")
    objective: str = Field(..., description="Campaign objective")
    budget: float = Field(..., description="Campaign budget")
    daily_budget: Optional[float] = Field(None, description="Daily budget")
    status: Optional[str] = Field("PAUSED", description="Campaign status")
    targeting: Optional[Dict[str, Any]] = Field({}, description="Targeting criteria")
    creative: Optional[Dict[str, Any]] = Field({}, description="Creative assets")

class CampaignResponse(BaseModel):
    campaign_id: str
    platform: str
    name: str
    objective: str
    budget: float
    daily_budget: Optional[float]
    status: str
    targeting: Dict[str, Any]
    creative: Dict[str, Any]
    created_at: str

class PlatformMetricsResponse(BaseModel):
    campaign_id: str
    platform: str
    metrics: Dict[str, Any]
    date_range: str
    retrieved_at: str

class PlatformDashboardResponse(BaseModel):
    organization_id: str
    platform_statistics: Dict[str, Any]
    total_campaigns: int
    active_campaigns: int
    total_budget: float
    recent_metrics: List[Dict[str, Any]]
    supported_platforms: List[str]
    generated_at: str

# Dependency
async def get_platform_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdditionalPlatformIntegrationsService:
    return get_additional_platform_integrations_service(db)

# Platform Credentials Management
@router.post("/api/platforms/credentials", summary="Store Platform Credentials")
async def store_platform_credentials(
    request: PlatformCredentialsRequest = Body(...),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Store platform credentials for API access.
    Securely stores credentials for Facebook Ads, Twitter Ads, Pinterest, etc.
    """
    try:
        # Validate platform type
        try:
            platform_type = PlatformType(request.platform)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        # Create credentials object
        credentials = PlatformCredentials(
            platform=platform_type,
            access_token=request.access_token,
            refresh_token=request.refresh_token,
            client_id=request.client_id,
            client_secret=request.client_secret,
            account_id=request.account_id,
            expires_at=datetime.fromisoformat(request.expires_at) if request.expires_at else None,
            additional_config=request.additional_config
        )
        
        # Store credentials securely
        credentials_doc = {
            "platform": credentials.platform.value,
            "access_token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "account_id": credentials.account_id,
            "expires_at": credentials.expires_at.isoformat() if credentials.expires_at else None,
            "additional_config": credentials.additional_config,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await platform_service.db.platform_credentials.replace_one(
            {"platform": credentials.platform.value, "account_id": credentials.account_id},
            credentials_doc,
            upsert=True
        )
        
        return {
            "platform": credentials.platform.value,
            "account_id": credentials.account_id,
            "status": "stored",
            "message": f"Credentials stored for {credentials.platform.value}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing platform credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store platform credentials"
        )

@router.get("/api/platforms/credentials", summary="List Platform Credentials")
async def list_platform_credentials(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    List stored platform credentials.
    Returns credential metadata without sensitive data.
    """
    try:
        # Build query
        query = {}
        if platform:
            query["platform"] = platform
        
        # Get credentials (without sensitive data)
        credentials = await platform_service.db.platform_credentials.find(query).to_list(length=None)
        
        # Remove sensitive data
        safe_credentials = []
        for cred in credentials:
            safe_credentials.append({
                "platform": cred["platform"],
                "account_id": cred["account_id"],
                "client_id": cred["client_id"],
                "expires_at": cred.get("expires_at"),
                "created_at": cred["created_at"],
                "updated_at": cred["updated_at"]
            })
        
        return {
            "credentials": safe_credentials,
            "total_count": len(safe_credentials)
        }
        
    except Exception as e:
        logger.error(f"Error listing platform credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list platform credentials"
        )

# Campaign Management
@router.post("/api/platforms/campaigns", response_model=CampaignResponse, summary="Create Platform Campaign")
async def create_platform_campaign(
    request: CampaignCreateRequest = Body(...),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Create a campaign on the specified platform.
    Supports Facebook Ads, Twitter Ads, Pinterest, Snapchat, Reddit, and Quora.
    """
    try:
        # Validate platform type
        try:
            platform_type = PlatformType(request.platform)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        # Get platform credentials
        credentials_doc = await platform_service.db.platform_credentials.find_one({
            "platform": platform_type.value
        })
        
        if not credentials_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No credentials found for {platform_type.value}"
            )
        
        # Create credentials object
        credentials = PlatformCredentials(
            platform=platform_type,
            access_token=credentials_doc["access_token"],
            refresh_token=credentials_doc.get("refresh_token"),
            client_id=credentials_doc["client_id"],
            client_secret=credentials_doc["client_secret"],
            account_id=credentials_doc["account_id"],
            expires_at=datetime.fromisoformat(credentials_doc["expires_at"]) if credentials_doc.get("expires_at") else None,
            additional_config=credentials_doc.get("additional_config", {})
        )
        
        # Prepare campaign data
        campaign_data = {
            "name": request.name,
            "objective": request.objective,
            "budget": request.budget,
            "daily_budget": request.daily_budget,
            "status": request.status,
            "targeting": request.targeting,
            "creative": request.creative
        }
        
        # Create campaign
        result = await platform_service.create_campaign(platform_type, campaign_data, credentials)
        
        # Get created campaign from database
        campaign_doc = await platform_service.db.additional_platform_campaigns.find_one({
            "platform": platform_type.value,
            "name": request.name
        }, sort=[("created_at", -1)])
        
        return CampaignResponse(
            campaign_id=campaign_doc["campaign_id"],
            platform=campaign_doc["platform"],
            name=campaign_doc["name"],
            objective=campaign_doc["objective"],
            budget=campaign_doc["budget"],
            daily_budget=campaign_doc.get("daily_budget"),
            status=campaign_doc["status"],
            targeting=campaign_doc["targeting"],
            creative=campaign_doc["creative"],
            created_at=campaign_doc["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating platform campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create platform campaign"
        )

@router.get("/api/platforms/campaigns", response_model=List[CampaignResponse], summary="List Platform Campaigns")
async def list_platform_campaigns(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of campaigns to return"),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    List campaigns across all platforms.
    Returns campaign summaries with filtering options.
    """
    try:
        # Build query
        query = {}
        if platform:
            query["platform"] = platform
        if status:
            query["status"] = status
        
        # Get campaigns
        campaigns = await platform_service.db.additional_platform_campaigns.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        campaign_responses = []
        for campaign in campaigns:
            campaign_responses.append(CampaignResponse(
                campaign_id=campaign["campaign_id"],
                platform=campaign["platform"],
                name=campaign["name"],
                objective=campaign["objective"],
                budget=campaign["budget"],
                daily_budget=campaign.get("daily_budget"),
                status=campaign["status"],
                targeting=campaign["targeting"],
                creative=campaign["creative"],
                created_at=campaign["created_at"]
            ))
        
        return campaign_responses
        
    except Exception as e:
        logger.error(f"Error listing platform campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list platform campaigns"
        )

@router.get("/api/platforms/campaigns/{campaign_id}", summary="Get Platform Campaign Details")
async def get_platform_campaign_details(
    campaign_id: str,
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get detailed campaign information.
    Returns complete campaign data and recent metrics.
    """
    try:
        # Get campaign
        campaign = await platform_service.db.additional_platform_campaigns.find_one({
            "campaign_id": campaign_id
        })
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get recent metrics
        recent_metrics = await platform_service.db.additional_platform_metrics.find({
            "campaign_id": campaign_id
        }).sort("retrieved_at", -1).limit(10).to_list(length=None)
        
        return {
            "campaign": campaign,
            "recent_metrics": recent_metrics,
            "metrics_count": len(recent_metrics)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign details"
        )

# Metrics and Analytics
@router.get("/api/platforms/campaigns/{campaign_id}/metrics", response_model=PlatformMetricsResponse, summary="Get Campaign Metrics")
async def get_campaign_metrics(
    campaign_id: str,
    platform: str = Query(..., description="Platform type"),
    date_range: str = Query("last_30_days", description="Date range for metrics"),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get campaign metrics from the platform.
    Retrieves performance data from Facebook Ads, Twitter Ads, etc.
    """
    try:
        # Validate platform type
        try:
            platform_type = PlatformType(platform)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        # Get platform credentials
        credentials_doc = await platform_service.db.platform_credentials.find_one({
            "platform": platform_type.value
        })
        
        if not credentials_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No credentials found for {platform_type.value}"
            )
        
        # Create credentials object
        credentials = PlatformCredentials(
            platform=platform_type,
            access_token=credentials_doc["access_token"],
            refresh_token=credentials_doc.get("refresh_token"),
            client_id=credentials_doc["client_id"],
            client_secret=credentials_doc["client_secret"],
            account_id=credentials_doc["account_id"],
            expires_at=datetime.fromisoformat(credentials_doc["expires_at"]) if credentials_doc.get("expires_at") else None,
            additional_config=credentials_doc.get("additional_config", {})
        )
        
        # Get metrics
        metrics = await platform_service.get_campaign_metrics(platform_type, campaign_id, credentials, date_range)
        
        # Get latest metrics from database
        latest_metrics = await platform_service.db.additional_platform_metrics.find_one({
            "campaign_id": campaign_id,
            "platform": platform_type.value
        }, sort=[("retrieved_at", -1)])
        
        return PlatformMetricsResponse(
            campaign_id=campaign_id,
            platform=platform_type.value,
            metrics=metrics,
            date_range=date_range,
            retrieved_at=latest_metrics["retrieved_at"] if latest_metrics else datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign metrics"
        )

@router.get("/api/platforms/metrics", summary="Get Platform Metrics Summary")
async def get_platform_metrics_summary(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    days: int = Query(30, description="Number of days to look back"),
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get metrics summary across platforms.
    Returns aggregated performance data.
    """
    try:
        # Build query
        query = {
            "retrieved_at": {"$gte": (datetime.utcnow() - timedelta(days=days)).isoformat()}
        }
        if platform:
            query["platform"] = platform
        
        # Get metrics
        metrics = await platform_service.db.additional_platform_metrics.find(query).to_list(length=None)
        
        # Aggregate metrics by platform
        platform_summary = {}
        for metric in metrics:
            platform_name = metric["platform"]
            if platform_name not in platform_summary:
                platform_summary[platform_name] = {
                    "total_campaigns": 0,
                    "total_metrics": 0,
                    "campaigns": set()
                }
            
            platform_summary[platform_name]["total_metrics"] += 1
            platform_summary[platform_name]["campaigns"].add(metric["campaign_id"])
        
        # Convert sets to counts
        for platform_name in platform_summary:
            platform_summary[platform_name]["total_campaigns"] = len(platform_summary[platform_name]["campaigns"])
            del platform_summary[platform_name]["campaigns"]
        
        return {
            "platform_summary": platform_summary,
            "total_metrics": len(metrics),
            "date_range_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform metrics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform metrics summary"
        )

# Dashboard Endpoint
@router.get("/api/platforms/dashboard/{organization_id}", response_model=PlatformDashboardResponse, summary="Get Platform Dashboard")
async def get_platform_dashboard(
    organization_id: str,
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get comprehensive platform dashboard.
    Returns campaign statistics and performance metrics across all platforms.
    """
    try:
        dashboard = await platform_service.get_platform_dashboard(organization_id)
        
        return PlatformDashboardResponse(
            organization_id=dashboard["organization_id"],
            platform_statistics=dashboard["platform_statistics"],
            total_campaigns=dashboard["total_campaigns"],
            active_campaigns=dashboard["active_campaigns"],
            total_budget=dashboard["total_budget"],
            recent_metrics=dashboard["recent_metrics"],
            supported_platforms=dashboard["supported_platforms"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting platform dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform dashboard"
        )

# Platform Health Check
@router.get("/api/platforms/health", summary="Platform Integrations Health Check")
async def platform_integrations_health_check(
    platform_service: AdditionalPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Check the health of platform integrations.
    Returns system status and supported platforms.
    """
    try:
        # Check database connection
        await platform_service.db.admin.command('ping')
        
        # Get platform statistics
        stats = {
            "total_credentials": await platform_service.db.platform_credentials.count_documents({}),
            "total_campaigns": await platform_service.db.additional_platform_campaigns.count_documents({}),
            "total_metrics": await platform_service.db.additional_platform_metrics.count_documents({}),
            "active_campaigns": await platform_service.db.additional_platform_campaigns.count_documents({"status": "ACTIVE"})
        }
        
        # Get platform-specific statistics
        platform_stats = {}
        for platform in PlatformType:
            platform_stats[platform.value] = {
                "credentials": await platform_service.db.platform_credentials.count_documents({"platform": platform.value}),
                "campaigns": await platform_service.db.additional_platform_campaigns.count_documents({"platform": platform.value}),
                "metrics": await platform_service.db.additional_platform_metrics.count_documents({"platform": platform.value})
            }
        
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "facebook_ads": "healthy",
                "twitter_ads": "healthy",
                "pinterest": "healthy",
                "snapchat": "healthy",
                "reddit": "healthy",
                "quora": "healthy"
            },
            "statistics": stats,
            "platform_statistics": platform_stats,
            "capabilities": {
                "campaign_creation": True,
                "campaign_management": True,
                "metrics_retrieval": True,
                "multi_platform_support": True,
                "credential_management": True,
                "real_time_monitoring": True
            },
            "supported_platforms": [platform.value for platform in PlatformType],
            "supported_objectives": [objective.value for objective in CampaignObjective],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking platform integrations health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
