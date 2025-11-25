"""
Metabase Business Intelligence Routes
API endpoints for dashboard management and embedding
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.services.metabase_bi import metabase_service, DashboardType, ChartType

router = APIRouter(prefix="/api/metabase", tags=["metabase"])

class DashboardCreateRequest(BaseModel):
    template_name: str
    organization_id: str
    custom_name: Optional[str] = None
    custom_description: Optional[str] = None

class EmbeddingTokenRequest(BaseModel):
    dashboard_id: int
    organization_id: str
    user_id: str
    expires_hours: Optional[int] = 24

class ChartCreateRequest(BaseModel):
    dashboard_id: int
    name: str
    chart_type: ChartType
    query: str
    position_x: int
    position_y: int
    width: int
    height: int
    visualization_settings: Optional[Dict[str, Any]] = {}

@router.post("/database/connect")
async def create_database_connection(organization_id: str = Query(..., description="Organization ID")):
    """Create database connection for organization"""
    try:
        result = await metabase_service.create_database_connection(organization_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Database connection created",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.post("/dashboard/create")
async def create_dashboard(request: DashboardCreateRequest):
    """Create dashboard from template"""
    try:
        result = await metabase_service.create_dashboard(
            request.template_name,
            request.organization_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Dashboard created successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")

@router.post("/dashboard/face")
async def create_face_dashboard(organization_id: str = Query(..., description="Organization ID")):
    """Create complete FACE module dashboard suite"""
    try:
        result = await metabase_service.create_face_dashboard(organization_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "success",
            "message": "FACE dashboard suite created",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FACE dashboard creation failed: {str(e)}")

@router.post("/embedding/token")
async def generate_embedding_token(request: EmbeddingTokenRequest):
    """Generate embedding token for dashboard"""
    try:
        expires_at = datetime.utcnow() + timedelta(hours=request.expires_hours)
        
        token = await metabase_service.generate_embedding_token(
            request.dashboard_id,
            request.organization_id,
            request.user_id,
            expires_at
        )
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expires_at.isoformat(),
            "dashboard_id": request.dashboard_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")

@router.get("/embedding/url")
async def get_dashboard_embed_url(
    dashboard_id: int = Query(..., description="Dashboard ID"),
    organization_id: str = Query(..., description="Organization ID"),
    user_id: str = Query(..., description="User ID")
):
    """Get embedded dashboard URL"""
    try:
        embed_url = await metabase_service.get_dashboard_embed_url(
            dashboard_id, organization_id, user_id
        )
        
        return {
            "status": "success",
            "embed_url": embed_url,
            "dashboard_id": dashboard_id,
            "organization_id": organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embed URL generation failed: {str(e)}")

@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: int):
    """Get dashboard data and metadata"""
    try:
        result = await metabase_service.get_dashboard_data(dashboard_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard retrieval failed: {str(e)}")

@router.post("/chart/create")
async def create_chart(request: ChartCreateRequest):
    """Create chart in dashboard"""
    try:
        # This would integrate with Metabase's card creation API
        # For now, return a placeholder response
        return {
            "status": "success",
            "message": "Chart creation endpoint ready",
            "chart_id": f"chart_{request.dashboard_id}_{datetime.utcnow().timestamp()}",
            "dashboard_id": request.dashboard_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart creation failed: {str(e)}")

@router.get("/templates")
async def get_dashboard_templates():
    """Get available dashboard templates"""
    try:
        templates = {}
        for name, template in metabase_service.dashboard_templates.items():
            templates[name] = {
                "name": template["name"],
                "description": template["description"],
                "dashboard_type": template["dashboard_type"].value,
                "chart_count": len(template["charts"])
            }
        
        return {
            "status": "success",
            "templates": templates,
            "total_templates": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template retrieval failed: {str(e)}")

@router.get("/health")
async def metabase_health():
    """Metabase service health check"""
    try:
        health_data = await metabase_service.health_check()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/status")
async def metabase_status():
    """Get Metabase service status"""
    try:
        return {
            "status": "success",
            "metabase_enabled": metabase_service.enable_metabase,
            "metabase_url": metabase_service.metabase_url,
            "site_url": metabase_service.site_url,
            "admin_email": metabase_service.admin_email,
            "templates_available": len(metabase_service.dashboard_templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
