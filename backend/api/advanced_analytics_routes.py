"""
Advanced Analytics API Routes
Production-grade API endpoints for analytics and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.advanced_analytics_service import (
    get_advanced_analytics_service, AdvancedAnalyticsService,
    ReportConfig, ReportFormat, ReportType, ChartConfig, DashboardType
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class ChartConfigRequest(BaseModel):
    chart_type: str = Field(..., description="Type of chart (line, bar, pie, scatter, area, heatmap, funnel)")
    title: str = Field(..., description="Chart title")
    x_axis: str = Field(..., description="X-axis field")
    y_axis: str = Field(..., description="Y-axis field")
    color_by: Optional[str] = Field(None, description="Field to color by")
    filters: Optional[Dict[str, Any]] = Field(None, description="Chart filters")
    time_range: str = Field("30d", description="Time range for data")
    aggregation: str = Field("sum", description="Data aggregation method")

class DashboardConfigRequest(BaseModel):
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field("", description="Dashboard description")
    dashboard_type: str = Field("custom", description="Dashboard type")
    charts: List[ChartConfigRequest] = Field([], description="Charts configuration")
    layout: Optional[Dict[str, Any]] = Field({}, description="Dashboard layout")
    filters: Optional[Dict[str, Any]] = Field({}, description="Dashboard filters")

class ReportConfigRequest(BaseModel):
    name: str = Field(..., description="Report name")
    description: str = Field(..., description="Report description")
    report_type: str = Field(..., description="Report type")
    format: str = Field(..., description="Report format")
    schedule: Optional[str] = Field(None, description="Report schedule")
    recipients: Optional[List[str]] = Field([], description="Report recipients")
    charts: List[ChartConfigRequest] = Field([], description="Charts configuration")
    filters: Optional[Dict[str, Any]] = Field({}, description="Report filters")
    time_range: str = Field("30d", description="Time range for data")

class MetricsResponse(BaseModel):
    client_id: str
    metrics: Dict[str, Any]
    last_updated: str
    time_range: str

class DashboardResponse(BaseModel):
    dashboard_id: str
    client_id: str
    name: str
    description: str
    dashboard_type: str
    charts: List[Dict[str, Any]]
    layout: Dict[str, Any]
    filters: Dict[str, Any]
    created_at: str
    updated_at: str
    is_active: bool

class ReportResponse(BaseModel):
    report_id: str
    report_content: Dict[str, Any]
    file_content: bytes
    file_size: int
    generated_at: str

class AudienceInsightsResponse(BaseModel):
    age_groups: Dict[str, Any]
    genders: Dict[str, Any]
    locations: Dict[str, Any]
    period: Dict[str, str]

class CreativePerformanceResponse(BaseModel):
    top_performers: List[Dict[str, Any]]
    creative_types: Dict[str, Any]
    platform_performance: Dict[str, Any]
    period: Dict[str, str]

# Dependency
async def get_analytics_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedAnalyticsService:
    return get_advanced_analytics_service(db)

# Real-time Metrics Endpoints
@router.get("/api/analytics/metrics/{client_id}", response_model=MetricsResponse, summary="Get Real-time Metrics")
async def get_real_time_metrics(
    client_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get real-time metrics for a client's campaigns.
    Returns comprehensive performance data for the last 7 days.
    """
    try:
        metrics = await analytics_service.get_real_time_metrics(client_id)
        return MetricsResponse(**metrics)
    except Exception as e:
        logger.error(f"Error getting real-time metrics for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time metrics"
        )

@router.get("/api/analytics/metrics/{client_id}/historical", summary="Get Historical Metrics")
async def get_historical_metrics(
    client_id: str,
    days: int = Query(30, description="Number of days to retrieve"),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get historical metrics for a client's campaigns.
    Returns performance data for the specified number of days.
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        data_processor = analytics_service.data_processor
        metrics = await data_processor.get_campaign_metrics(client_id, start_date, end_date)
        
        return {
            "client_id": client_id,
            "metrics": metrics,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting historical metrics for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve historical metrics"
        )

# Dashboard Endpoints
@router.post("/api/analytics/dashboards", response_model=DashboardResponse, summary="Create Dashboard")
async def create_dashboard(
    client_id: str = Query(..., description="Client ID"),
    dashboard_config: DashboardConfigRequest = Body(...),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Create a new custom dashboard for a client.
    Supports various chart types and layouts.
    """
    try:
        dashboard_data = dashboard_config.dict()
        dashboard = await analytics_service.create_custom_dashboard(client_id, dashboard_data)
        return DashboardResponse(**dashboard)
    except Exception as e:
        logger.error(f"Error creating dashboard for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dashboard"
        )

@router.get("/api/analytics/dashboards/{dashboard_id}", summary="Get Dashboard Data")
async def get_dashboard_data(
    dashboard_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get real-time data for a specific dashboard.
    Returns updated metrics and chart data.
    """
    try:
        dashboard_data = await analytics_service.get_dashboard_data(dashboard_id)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data for {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )

@router.get("/api/analytics/dashboards", summary="List Client Dashboards")
async def list_dashboards(
    client_id: str = Query(..., description="Client ID"),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    List all dashboards for a client.
    Returns dashboard metadata and configuration.
    """
    try:
        dashboards = await analytics_service.db.dashboards.find(
            {"client_id": client_id, "is_active": True}
        ).to_list(length=None)
        
        return {
            "client_id": client_id,
            "dashboards": dashboards,
            "total_count": len(dashboards)
        }
    except Exception as e:
        logger.error(f"Error listing dashboards for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list dashboards"
        )

@router.put("/api/analytics/dashboards/{dashboard_id}", summary="Update Dashboard")
async def update_dashboard(
    dashboard_id: str,
    dashboard_config: DashboardConfigRequest = Body(...),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Update an existing dashboard configuration.
    """
    try:
        update_data = dashboard_config.dict()
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await analytics_service.db.dashboards.update_one(
            {"dashboard_id": dashboard_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        return {"message": "Dashboard updated successfully", "dashboard_id": dashboard_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dashboard"
        )

@router.delete("/api/analytics/dashboards/{dashboard_id}", summary="Delete Dashboard")
async def delete_dashboard(
    dashboard_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Delete a dashboard (soft delete).
    """
    try:
        result = await analytics_service.db.dashboards.update_one(
            {"dashboard_id": dashboard_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        return {"message": "Dashboard deleted successfully", "dashboard_id": dashboard_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dashboard"
        )

# Report Generation Endpoints
@router.post("/api/analytics/reports/generate", summary="Generate Custom Report")
async def generate_custom_report(
    client_id: str = Query(..., description="Client ID"),
    report_config: ReportConfigRequest = Body(...),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Generate a custom report with specified configuration.
    Returns report data and file content.
    """
    try:
        # Convert request to ReportConfig
        charts = [ChartConfig(**chart.dict()) for chart in report_config.charts]
        
        config = ReportConfig(
            name=report_config.name,
            description=report_config.description,
            report_type=ReportType(report_config.report_type),
            format=ReportFormat(report_config.format),
            schedule=report_config.schedule,
            recipients=report_config.recipients,
            charts=charts,
            filters=report_config.filters,
            time_range=report_config.time_range
        )
        
        report_result = await analytics_service.generate_custom_report(client_id, config)
        
        return {
            "report_id": report_result["report_id"],
            "report_content": report_result["report_content"],
            "file_size": report_result["file_size"],
            "generated_at": report_result["generated_at"],
            "download_url": f"/api/analytics/reports/{report_result['report_id']}/download"
        }
    except Exception as e:
        logger.error(f"Error generating custom report for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate custom report"
        )

@router.get("/api/analytics/reports/{report_id}/download", summary="Download Report")
async def download_report(
    report_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Download a generated report file.
    """
    try:
        # This would retrieve the report from storage
        # For now, return a placeholder response
        return {
            "report_id": report_id,
            "message": "Report download endpoint - implementation needed",
            "status": "pending"
        }
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download report"
        )

# Scheduled Reports Endpoints
@router.post("/api/analytics/reports/scheduled", summary="Create Scheduled Report")
async def create_scheduled_report(
    client_id: str = Query(..., description="Client ID"),
    report_config: ReportConfigRequest = Body(...),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Create a scheduled report that runs automatically.
    Supports daily, weekly, and monthly schedules.
    """
    try:
        # Convert request to ReportConfig
        charts = [ChartConfig(**chart.dict()) for chart in report_config.charts]
        
        config = ReportConfig(
            name=report_config.name,
            description=report_config.description,
            report_type=ReportType(report_config.report_type),
            format=ReportFormat(report_config.format),
            schedule=report_config.schedule,
            recipients=report_config.recipients,
            charts=charts,
            filters=report_config.filters,
            time_range=report_config.time_range
        )
        
        scheduled_report = await analytics_service.create_scheduled_report(client_id, config)
        
        return {
            "report_id": scheduled_report["report_id"],
            "name": scheduled_report["name"],
            "schedule": scheduled_report["schedule"],
            "next_run": scheduled_report["next_run"],
            "recipients": scheduled_report["recipients"],
            "created_at": scheduled_report["created_at"]
        }
    except Exception as e:
        logger.error(f"Error creating scheduled report for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scheduled report"
        )

@router.get("/api/analytics/reports/scheduled", summary="List Scheduled Reports")
async def list_scheduled_reports(
    client_id: str = Query(..., description="Client ID"),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    List all scheduled reports for a client.
    """
    try:
        scheduled_reports = await analytics_service.db.scheduled_reports.find(
            {"client_id": client_id, "is_active": True}
        ).to_list(length=None)
        
        return {
            "client_id": client_id,
            "scheduled_reports": scheduled_reports,
            "total_count": len(scheduled_reports)
        }
    except Exception as e:
        logger.error(f"Error listing scheduled reports for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list scheduled reports"
        )

@router.post("/api/analytics/reports/scheduled/{report_id}/execute", summary="Execute Scheduled Report")
async def execute_scheduled_report(
    report_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Manually execute a scheduled report.
    """
    try:
        report_result = await analytics_service.scheduled_report_manager.execute_scheduled_report(report_id)
        
        return {
            "report_id": report_id,
            "execution_status": "completed",
            "generated_at": report_result["generated_at"],
            "file_size": report_result["file_size"]
        }
    except Exception as e:
        logger.error(f"Error executing scheduled report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute scheduled report"
        )

# Audience Insights Endpoints
@router.get("/api/analytics/audience/{client_id}", response_model=AudienceInsightsResponse, summary="Get Audience Insights")
async def get_audience_insights(
    client_id: str,
    time_range: str = Query("30d", description="Time range (7d, 30d, 90d)"),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get audience insights and demographics for a client.
    Returns age groups, genders, locations, and performance data.
    """
    try:
        insights = await analytics_service.get_audience_insights(client_id, time_range)
        return AudienceInsightsResponse(**insights)
    except Exception as e:
        logger.error(f"Error getting audience insights for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audience insights"
        )

# Creative Performance Endpoints
@router.get("/api/analytics/creative/{client_id}", response_model=CreativePerformanceResponse, summary="Get Creative Performance")
async def get_creative_performance(
    client_id: str,
    time_range: str = Query("30d", description="Time range (7d, 30d, 90d)"),
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get creative performance analysis for a client.
    Returns top performers, creative types, and platform performance.
    """
    try:
        performance = await analytics_service.get_creative_performance(client_id, time_range)
        return CreativePerformanceResponse(**performance)
    except Exception as e:
        logger.error(f"Error getting creative performance for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve creative performance"
        )

# Executive Dashboard Endpoints
@router.get("/api/analytics/executive/{client_id}", summary="Get Executive Dashboard")
async def get_executive_dashboard(
    client_id: str,
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get executive-level dashboard with key performance indicators.
    Returns high-level metrics and trends.
    """
    try:
        # Get comprehensive metrics
        metrics = await analytics_service.get_real_time_metrics(client_id)
        
        # Get audience insights
        audience_insights = await analytics_service.get_audience_insights(client_id, "30d")
        
        # Get creative performance
        creative_performance = await analytics_service.get_creative_performance(client_id, "30d")
        
        # Calculate executive KPIs
        overall_metrics = metrics["metrics"]["overall"]
        
        executive_kpis = {
            "total_revenue": overall_metrics["total_revenue"],
            "total_spend": overall_metrics["total_cost"],
            "roas": overall_metrics["overall_roas"],
            "cpa": overall_metrics["overall_cpa"],
            "conversion_rate": overall_metrics["overall_conversion_rate"],
            "ctr": overall_metrics["overall_ctr"],
            "total_campaigns": len(metrics["metrics"]["platforms"]),
            "top_performing_platform": max(metrics["metrics"]["platforms"], key=lambda x: x["total_revenue"])["_id"] if metrics["metrics"]["platforms"] else None
        }
        
        return {
            "client_id": client_id,
            "executive_kpis": executive_kpis,
            "audience_summary": {
                "top_age_group": max(audience_insights["age_groups"].items(), key=lambda x: x[1]["revenue"])[0] if audience_insights["age_groups"] else None,
                "top_gender": max(audience_insights["genders"].items(), key=lambda x: x[1]["revenue"])[0] if audience_insights["genders"] else None,
                "top_location": max(audience_insights["locations"].items(), key=lambda x: x[1]["revenue"])[0] if audience_insights["locations"] else None
            },
            "creative_summary": {
                "top_creative_type": max(creative_performance["creative_types"].items(), key=lambda x: x[1]["total_revenue"])[0] if creative_performance["creative_types"] else None,
                "total_creatives": len(creative_performance["top_performers"])
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting executive dashboard for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve executive dashboard"
        )

# Analytics Health Check
@router.get("/api/analytics/health", summary="Analytics Health Check")
async def analytics_health_check(
    analytics_service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Check the health of the analytics service.
    Returns service status and capabilities.
    """
    try:
        # Check database connection
        await analytics_service.db.admin.command('ping')
        
        # Check service components
        components = {
            "data_processor": analytics_service.data_processor is not None,
            "chart_generator": analytics_service.chart_generator is not None,
            "report_generator": analytics_service.report_generator is not None,
            "dashboard_manager": analytics_service.dashboard_manager is not None,
            "scheduled_report_manager": analytics_service.scheduled_report_manager is not None
        }
        
        all_healthy = all(components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
            "capabilities": {
                "real_time_metrics": True,
                "custom_dashboards": True,
                "report_generation": True,
                "scheduled_reports": True,
                "audience_insights": True,
                "creative_performance": True,
                "executive_dashboards": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking analytics health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
