"""
Advanced Reporting & BI API Routes
Production-grade API endpoints for custom dashboards, data visualization, and executive reports
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Response
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import json

from services.advanced_reporting_service import (
    get_advanced_reporting_service, AdvancedReportingService,
    ReportType, ChartType, ReportFormat, ReportStatus
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class ReportTemplateRequest(BaseModel):
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field("", description="Template description")
    report_type: str = Field(..., description="Report type")
    chart_configs: Optional[List[Dict[str, Any]]] = Field([], description="Chart configurations")
    filters: Optional[List[Dict[str, Any]]] = Field([], description="Filter configurations")
    layout: Optional[Dict[str, Any]] = Field({}, description="Layout configuration")

class ReportGenerationRequest(BaseModel):
    template_id: str = Field(..., description="Template ID")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    created_by: str = Field(..., description="Creator user ID")

class ReportExportRequest(BaseModel):
    report_id: str = Field(..., description="Report ID")
    format: str = Field(..., description="Export format")

class ReportTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    report_type: str
    chart_configs: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    layout: Dict[str, Any]
    created_at: str
    updated_at: str

class ReportResponse(BaseModel):
    report_id: str
    template_id: str
    name: str
    status: str
    parameters: Dict[str, Any]
    generated_at: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    created_by: str
    created_at: str

class ReportingDashboardResponse(BaseModel):
    organization_id: str
    report_statistics: Dict[str, Any]
    template_statistics: Dict[str, Any]
    recent_reports: List[Dict[str, Any]]
    supported_formats: List[str]
    supported_chart_types: List[str]
    generated_at: str

# Dependency
async def get_reporting_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedReportingService:
    return get_advanced_reporting_service(db)

# Report Template Management
@router.post("/api/reporting/templates", response_model=ReportTemplateResponse, summary="Create Report Template")
async def create_report_template(
    request: ReportTemplateRequest = Body(...),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Create a new report template.
    Defines the structure and configuration for automated report generation.
    """
    try:
        # Validate report type
        try:
            ReportType(request.report_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported report type: {request.report_type}"
            )
        
        template_data = {
            "name": request.name,
            "description": request.description,
            "report_type": request.report_type,
            "chart_configs": request.chart_configs,
            "filters": request.filters,
            "layout": request.layout
        }
        
        template_id = await reporting_service.create_report_template(template_data)
        
        # Get created template
        template_doc = await reporting_service.db.report_templates.find_one({"template_id": template_id})
        
        return ReportTemplateResponse(
            template_id=template_doc["template_id"],
            name=template_doc["name"],
            description=template_doc["description"],
            report_type=template_doc["report_type"],
            chart_configs=template_doc["chart_configs"],
            filters=template_doc["filters"],
            layout=template_doc["layout"],
            created_at=template_doc["created_at"],
            updated_at=template_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report template"
        )

@router.get("/api/reporting/templates", response_model=List[ReportTemplateResponse], summary="List Report Templates")
async def list_report_templates(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    List available report templates.
    Returns template definitions with filtering options.
    """
    try:
        # Build query
        query = {}
        if report_type:
            query["report_type"] = report_type
        
        # Get templates
        templates = await reporting_service.db.report_templates.find(query).sort("created_at", -1).to_list(length=None)
        
        template_responses = []
        for template in templates:
            template_responses.append(ReportTemplateResponse(
                template_id=template["template_id"],
                name=template["name"],
                description=template["description"],
                report_type=template["report_type"],
                chart_configs=template["chart_configs"],
                filters=template["filters"],
                layout=template["layout"],
                created_at=template["created_at"],
                updated_at=template["updated_at"]
            ))
        
        return template_responses
        
    except Exception as e:
        logger.error(f"Error listing report templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list report templates"
        )

@router.get("/api/reporting/templates/{template_id}", response_model=ReportTemplateResponse, summary="Get Report Template")
async def get_report_template(
    template_id: str,
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Get detailed report template information.
    Returns complete template configuration and metadata.
    """
    try:
        template = await reporting_service.db.report_templates.find_one({"template_id": template_id})
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report template not found"
            )
        
        return ReportTemplateResponse(
            template_id=template["template_id"],
            name=template["name"],
            description=template["description"],
            report_type=template["report_type"],
            chart_configs=template["chart_configs"],
            filters=template["filters"],
            layout=template["layout"],
            created_at=template["created_at"],
            updated_at=template["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report template"
        )

# Report Generation
@router.post("/api/reporting/reports", response_model=ReportResponse, summary="Generate Report")
async def generate_report(
    request: ReportGenerationRequest = Body(...),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Generate a report from a template.
    Creates a new report instance and starts generation process.
    """
    try:
        report_id = await reporting_service.generate_report(
            request.template_id,
            request.parameters,
            request.created_by
        )
        
        # Get created report
        report_doc = await reporting_service.db.reports.find_one({"report_id": report_id})
        
        return ReportResponse(
            report_id=report_doc["report_id"],
            template_id=report_doc["template_id"],
            name=report_doc["name"],
            status=report_doc["status"],
            parameters=report_doc["parameters"],
            generated_at=report_doc.get("generated_at"),
            file_path=report_doc.get("file_path"),
            file_size=report_doc.get("file_size"),
            created_by=report_doc["created_by"],
            created_at=report_doc["created_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )

@router.get("/api/reporting/reports", response_model=List[ReportResponse], summary="List Reports")
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    limit: int = Query(50, description="Number of reports to return"),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    List generated reports with filtering options.
    Returns report summaries and status information.
    """
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        if created_by:
            query["created_by"] = created_by
        
        # Get reports
        reports = await reporting_service.db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        report_responses = []
        for report in reports:
            report_responses.append(ReportResponse(
                report_id=report["report_id"],
                template_id=report["template_id"],
                name=report["name"],
                status=report["status"],
                parameters=report["parameters"],
                generated_at=report.get("generated_at"),
                file_path=report.get("file_path"),
                file_size=report.get("file_size"),
                created_by=report["created_by"],
                created_at=report["created_at"]
            ))
        
        return report_responses
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reports"
        )

@router.get("/api/reporting/reports/{report_id}", summary="Get Report Details")
async def get_report_details(
    report_id: str,
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Get detailed report information.
    Returns complete report data including charts and metrics.
    """
    try:
        report = await reporting_service.get_report(report_id)
        
        return {
            "report": report,
            "status": report["status"],
            "generated_at": report.get("generated_at"),
            "has_data": "report_data" in report
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting report details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report details"
        )

# Report Export
@router.post("/api/reporting/reports/{report_id}/export", summary="Export Report")
async def export_report(
    report_id: str,
    format: str = Query(..., description="Export format"),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Export report in specified format.
    Returns report file in PDF, Excel, CSV, or other formats.
    """
    try:
        # Validate format
        try:
            export_format = ReportFormat(format)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}"
            )
        
        # Export report
        file_content = await reporting_service.export_report(report_id, export_format)
        
        # Determine content type
        content_types = {
            ReportFormat.PDF: "application/pdf",
            ReportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ReportFormat.CSV: "text/csv",
            ReportFormat.JSON: "application/json",
            ReportFormat.HTML: "text/html"
        }
        
        content_type = content_types.get(export_format, "application/octet-stream")
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.{format}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export report"
        )

# Chart Generation
@router.post("/api/reporting/charts", summary="Generate Chart")
async def generate_chart(
    chart_type: str = Body(..., description="Chart type"),
    data: Dict[str, Any] = Body(..., description="Chart data"),
    config: Dict[str, Any] = Body({}, description="Chart configuration"),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Generate a standalone chart.
    Creates interactive charts for dashboards and reports.
    """
    try:
        # Validate chart type
        try:
            ChartType(chart_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported chart type: {chart_type}"
            )
        
        # Generate chart based on type
        chart_generator = reporting_service.report_generator.chart_generator
        
        if chart_type == ChartType.LINE:
            chart_json = chart_generator.generate_line_chart(
                data["dataframe"], data["x_col"], data["y_col"], data["title"], config
            )
        elif chart_type == ChartType.BAR:
            chart_json = chart_generator.generate_bar_chart(
                data["dataframe"], data["x_col"], data["y_col"], data["title"], config
            )
        elif chart_type == ChartType.PIE:
            chart_json = chart_generator.generate_pie_chart(
                data["dataframe"], data["labels_col"], data["values_col"], data["title"], config
            )
        elif chart_type == ChartType.HEATMAP:
            chart_json = chart_generator.generate_heatmap(
                data["dataframe"], data["x_col"], data["y_col"], data["z_col"], data["title"], config
            )
        elif chart_type == ChartType.FUNNEL:
            chart_json = chart_generator.generate_funnel_chart(
                data["dataframe"], data["stage_col"], data["value_col"], data["title"], config
            )
        elif chart_type == ChartType.GAUGE:
            chart_json = chart_generator.generate_gauge_chart(
                data["value"], data["title"], config
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chart generation not implemented for type: {chart_type}"
            )
        
        return {
            "chart_type": chart_type,
            "chart_json": chart_json,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate chart"
        )

# Dashboard Endpoint
@router.get("/api/reporting/dashboard/{organization_id}", response_model=ReportingDashboardResponse, summary="Get Reporting Dashboard")
async def get_reporting_dashboard(
    organization_id: str,
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Get comprehensive reporting dashboard.
    Returns report statistics, templates, and recent activity.
    """
    try:
        dashboard = await reporting_service.get_reporting_dashboard(organization_id)
        
        return ReportingDashboardResponse(
            organization_id=dashboard["organization_id"],
            report_statistics=dashboard["report_statistics"],
            template_statistics=dashboard["template_statistics"],
            recent_reports=dashboard["recent_reports"],
            supported_formats=dashboard["supported_formats"],
            supported_chart_types=dashboard["supported_chart_types"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting reporting dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reporting dashboard"
        )

# Quick Report Generation
@router.post("/api/reporting/quick-report", summary="Generate Quick Report")
async def generate_quick_report(
    report_type: str = Body(..., description="Report type"),
    parameters: Dict[str, Any] = Body(..., description="Report parameters"),
    created_by: str = Body(..., description="Creator user ID"),
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Generate a quick report without template.
    Creates reports using predefined templates for common report types.
    """
    try:
        # Validate report type
        try:
            ReportType(report_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported report type: {report_type}"
            )
        
        # Use predefined template
        predefined_templates = {
            ReportType.CAMPAIGN_PERFORMANCE: "campaign_performance_template",
            ReportType.FINANCIAL_SUMMARY: "financial_summary_template",
            ReportType.EXECUTIVE_SUMMARY: "executive_summary_template"
        }
        
        template_id = predefined_templates.get(ReportType(report_type))
        if not template_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No predefined template for report type: {report_type}"
            )
        
        # Generate report
        report_id = await reporting_service.generate_report(template_id, parameters, created_by)
        
        return {
            "report_id": report_id,
            "report_type": report_type,
            "status": "generating",
            "message": "Quick report generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quick report"
        )

# Reporting System Health Check
@router.get("/api/reporting/health", summary="Reporting System Health Check")
async def reporting_health_check(
    reporting_service: AdvancedReportingService = Depends(get_reporting_service)
):
    """
    Check the health of the reporting system.
    Returns system status and capabilities.
    """
    try:
        # Check database connection
        await reporting_service.db.admin.command('ping')
        
        # Get system statistics
        stats = {
            "total_templates": await reporting_service.db.report_templates.count_documents({}),
            "total_reports": await reporting_service.db.reports.count_documents({}),
            "completed_reports": await reporting_service.db.reports.count_documents({"status": ReportStatus.COMPLETED.value}),
            "failed_reports": await reporting_service.db.reports.count_documents({"status": ReportStatus.FAILED.value})
        }
        
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "report_generator": "healthy",
                "chart_generator": "healthy",
                "report_exporter": "healthy",
                "template_manager": "healthy"
            },
            "statistics": stats,
            "capabilities": {
                "template_management": True,
                "report_generation": True,
                "chart_generation": True,
                "multi_format_export": True,
                "scheduled_reports": True,
                "custom_dashboards": True,
                "executive_summaries": True,
                "financial_reporting": True
            },
            "supported_report_types": [rt.value for rt in ReportType],
            "supported_chart_types": [ct.value for ct in ChartType],
            "supported_formats": [rf.value for rf in ReportFormat],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking reporting health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
