"""
Dashboard API Routes
Aggregated statistics and metrics for dashboard display
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from core.auth import get_current_user
from database.connection_manager import get_database

router = APIRouter(prefix="/api/analytics", tags=["Dashboard"])


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_campaigns: int
    active_campaigns: int
    paused_campaigns: int
    total_spend: float
    total_revenue: float
    roas: float
    active_users: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    avg_ctr: float
    avg_cpa: float
    platform_breakdown: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    days: int = Query(30, description="Number of days to look back"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get aggregated dashboard statistics"""
    try:
        # Use organization_id from user if not provided
        if not organization_id:
            organization_id = current_user.get('organization_id')
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID is required"
            )
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all campaigns for organization
        campaigns = await db.campaigns.find({
            'organization_id': organization_id,
            'created_at': {'$gte': start_date.isoformat()}
        }).to_list(length=1000)
        
        # Calculate campaign statistics
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.get('status') == 'active'])
        paused_campaigns = len([c for c in campaigns if c.get('status') == 'paused'])
        
        # Aggregate performance metrics
        total_spend = 0.0
        total_revenue = 0.0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        
        platform_breakdown = {}
        
        for campaign in campaigns:
            performance = campaign.get('performance', {})
            
            # Aggregate spend and revenue
            budget = campaign.get('budget', {})
            daily_budget = budget.get('daily_budget', 0)
            total_spend += daily_budget * days  # Approximate
            
            revenue = performance.get('revenue', 0)
            total_revenue += revenue
            
            # Aggregate metrics
            total_impressions += performance.get('impressions', 0)
            total_clicks += performance.get('clicks', 0)
            total_conversions += performance.get('conversions', 0)
            
            # Platform breakdown
            platform = campaign.get('platform', 'unknown')
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    'campaigns': 0,
                    'spend': 0.0,
                    'revenue': 0.0,
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0
                }
            
            platform_breakdown[platform]['campaigns'] += 1
            platform_breakdown[platform]['spend'] += daily_budget * days
            platform_breakdown[platform]['revenue'] += revenue
            platform_breakdown[platform]['impressions'] += performance.get('impressions', 0)
            platform_breakdown[platform]['clicks'] += performance.get('clicks', 0)
            platform_breakdown[platform]['conversions'] += performance.get('conversions', 0)
        
        # Calculate derived metrics
        roas = total_revenue / total_spend if total_spend > 0 else 0.0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0.0
        
        # Calculate ROAS for each platform
        for platform in platform_breakdown:
            platform_data = platform_breakdown[platform]
            platform_data['roas'] = platform_data['revenue'] / platform_data['spend'] if platform_data['spend'] > 0 else 0.0
            platform_data['ctr'] = (platform_data['clicks'] / platform_data['impressions'] * 100) if platform_data['impressions'] > 0 else 0.0
        
        # Get active users (users who logged in within last 30 days)
        active_users = await db.users.count_documents({
            'organization_id': organization_id,
            'last_login': {'$gte': (datetime.utcnow() - timedelta(days=30)).isoformat()}
        })
        
        # Get recent activity
        recent_activity = await db.activity_logs.find({
            'organization_id': organization_id,
            'timestamp': {'$gte': start_date.isoformat()}
        }).sort('timestamp', -1).limit(10).to_list(length=10)
        
        # Format recent activity
        formatted_activity = []
        for activity in recent_activity:
            formatted_activity.append({
                'type': activity.get('type', 'unknown'),
                'description': activity.get('description', ''),
                'timestamp': activity.get('timestamp', ''),
                'user': activity.get('user_id', '')
            })
        
        return DashboardStatsResponse(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            paused_campaigns=paused_campaigns,
            total_spend=total_spend,
            total_revenue=total_revenue,
            roas=roas,
            active_users=active_users,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            total_conversions=total_conversions,
            avg_ctr=avg_ctr,
            avg_cpa=avg_cpa,
            platform_breakdown=platform_breakdown,
            recent_activity=formatted_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}"
        )

