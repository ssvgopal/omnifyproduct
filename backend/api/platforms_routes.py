"""
Platform Integration Routes
Handles API endpoints for all marketing platforms
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from services.meta_ads_service import meta_ads_service
from services.google_ads_service import google_ads_service
from services.data_sync_service import data_sync_service

router = APIRouter(prefix="/platforms", tags=["Platforms"])

# ========== REQUEST MODELS ==========

class DateRange(BaseModel):
    start: str = Field(..., description="Start date YYYY-MM-DD")
    end: str = Field(..., description="End date YYYY-MM-DD")

class MetricsRequest(BaseModel):
    organization_id: str
    date_range: Optional[DateRange] = None

class SyncRequest(BaseModel):
    organization_id: str
    days: int = Field(default=7, description="Number of days to sync")

# ========== META ADS ROUTES ==========

@router.post("/meta-ads/account")
async def get_meta_account(request: MetricsRequest):
    """Get Meta Ads account information"""
    result = await meta_ads_service.fetch_account_info(request.organization_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/meta-ads/campaigns")
async def get_meta_campaigns(request: MetricsRequest):
    """Get all Meta Ads campaigns"""
    result = await meta_ads_service.fetch_campaigns(request.organization_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/meta-ads/insights")
async def get_meta_insights(request: MetricsRequest):
    """Get Meta Ads performance insights"""
    date_range = request.date_range.dict() if request.date_range else None
    result = await meta_ads_service.fetch_insights(request.organization_id, date_range)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/meta-ads/summary")
async def get_meta_summary(request: MetricsRequest):
    """Get Meta Ads summary metrics for dashboard"""
    result = await meta_ads_service.calculate_summary_metrics(request.organization_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# ========== GOOGLE ADS ROUTES ==========

@router.post("/google-ads/campaigns")
async def get_google_campaigns(request: MetricsRequest):
    """Get all Google Ads campaigns"""
    result = await google_ads_service.fetch_campaigns(request.organization_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/google-ads/metrics")
async def get_google_metrics(request: MetricsRequest):
    """Get Google Ads performance metrics"""
    date_range = request.date_range.dict() if request.date_range else None
    result = await google_ads_service.fetch_metrics(request.organization_id, date_range)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/google-ads/summary")
async def get_google_summary(request: MetricsRequest):
    """Get Google Ads summary metrics for dashboard"""
    result = await google_ads_service.calculate_summary_metrics(request.organization_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# ========== DATA SYNC ROUTES ==========

@router.post("/sync/{platform}")
async def sync_platform(platform: str, request: SyncRequest):
    """
    Sync data from a specific platform
    
    Platforms: meta_ads, google_ads, tiktok, shopify
    """
    result = await data_sync_service.sync_platform_data(
        request.organization_id,
        platform,
        request.days
    )
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/sync/all")
async def sync_all_platforms(request: SyncRequest):
    """Sync data from all configured platforms"""
    result = await data_sync_service.sync_all_platforms(
        request.organization_id,
        request.days
    )
    return result

@router.post("/unified-metrics")
async def get_unified_metrics(request: MetricsRequest):
    """
    Get unified metrics across all platforms
    
    Returns blended metrics and platform breakdown
    """
    date_range = request.date_range.dict() if request.date_range else None
    result = await data_sync_service.get_unified_metrics(
        request.organization_id,
        date_range
    )
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.get("/health")
async def health_check():
    """Health check endpoint for platforms service"""
    return {
        'status': 'healthy',
        'service': 'platforms',
        'message': 'Platform integration service is operational'
    }
