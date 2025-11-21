"""
Advanced Automation Workflows API Routes
Workflow creation, execution, monitoring, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from core.auth import get_current_user
from database.connection_manager import get_database
from services.advanced_automation_service import (
    AdvancedAutomationService,
    get_advanced_automation_service,
    WorkflowStatus,
    ActionType,
    TriggerType
)
import redis
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow"""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    triggers: Optional[List[Dict[str, Any]]] = Field([], description="Workflow triggers")
    organization_id: str = Field(..., description="Organization ID")


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating a workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None


class WorkflowExecutionRequest(BaseModel):
    """Request model for executing a workflow"""
    workflow_id: str
    trigger_data: Optional[Dict[str, Any]] = None


class TriggerCreateRequest(BaseModel):
    """Request model for creating a trigger"""
    workflow_id: str
    trigger_type: str = Field(..., description="Trigger type")
    trigger_config: Dict[str, Any] = Field(..., description="Trigger configuration")
    organization_id: str = Field(..., description="Organization ID")


def get_redis_client():
    """Get Redis client"""
    try:
        import redis as redis_lib
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        return redis_lib.from_url(redis_url, decode_responses=True)
    except Exception:
        return None


def get_celery_app():
    """Get Celery app"""
    try:
        from celery import Celery
        celery_app = Celery('omnify')
        celery_app.config_from_object('celeryconfig')
        return celery_app
    except Exception:
        return None


@router.post("", summary="Create Workflow")
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new automation workflow"""
    try:
        redis_client = get_redis_client()
        celery_app = get_celery_app()
        
        if not redis_client or not celery_app:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Workflow service requires Redis and Celery"
            )
        
        automation_service = get_advanced_automation_service(db, redis_client, celery_app)
        
        workflow_data = {
            'name': request.name,
            'description': request.description,
            'steps': request.steps,
            'triggers': request.triggers,
            'organization_id': request.organization_id,
            'created_by': current_user.get('user_id'),
            'status': WorkflowStatus.DRAFT.value
        }
        
        workflow_id = await automation_service.create_workflow(workflow_data)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/{workflow_id}/execute", summary="Execute Workflow")
async def execute_workflow(
    workflow_id: str,
    request: Optional[WorkflowExecutionRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Execute a workflow"""
    try:
        redis_client = get_redis_client()
        celery_app = get_celery_app()
        
        if not redis_client or not celery_app:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Workflow service requires Redis and Celery"
            )
        
        automation_service = get_advanced_automation_service(db, redis_client, celery_app)
        
        trigger_data = request.trigger_data if request else None
        execution_id = await automation_service.execute_workflow(workflow_id, trigger_data)
        
        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Workflow execution started"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


@router.get("/{workflow_id}/executions", summary="Get Workflow Executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = Query(50, description="Number of executions to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get workflow execution history"""
    try:
        redis_client = get_redis_client()
        celery_app = get_celery_app()
        
        if not redis_client or not celery_app:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Workflow service requires Redis and Celery"
            )
        
        automation_service = get_advanced_automation_service(db, redis_client, celery_app)
        executions = await automation_service.get_workflow_executions(workflow_id, limit)
        
        return {
            "success": True,
            "executions": executions,
            "count": len(executions)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve executions: {str(e)}"
        )


@router.get("/{workflow_id}/executions/{execution_id}", summary="Get Execution Details")
async def get_execution_details(
    workflow_id: str,
    execution_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed execution information"""
    try:
        redis_client = get_redis_client()
        celery_app = get_celery_app()
        
        if not redis_client or not celery_app:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Workflow service requires Redis and Celery"
            )
        
        automation_service = get_advanced_automation_service(db, redis_client, celery_app)
        execution = await automation_service.get_execution_details(execution_id)
        
        return {
            "success": True,
            "execution": execution
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve execution details: {str(e)}"
        )


@router.post("/triggers", summary="Create Trigger")
async def create_trigger(
    request: TriggerCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a workflow trigger"""
    try:
        redis_client = get_redis_client()
        celery_app = get_celery_app()
        
        if not redis_client or not celery_app:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Workflow service requires Redis and Celery"
            )
        
        automation_service = get_advanced_automation_service(db, redis_client, celery_app)
        
        trigger_data = {
            'workflow_id': request.workflow_id,
            'trigger_type': request.trigger_type,
            'trigger_config': request.trigger_config,
            'organization_id': request.organization_id,
            'created_by': current_user.get('user_id')
        }
        
        trigger_id = await automation_service.create_trigger(trigger_data)
        
        return {
            "success": True,
            "trigger_id": trigger_id,
            "message": "Trigger created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trigger: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trigger: {str(e)}"
        )


@router.get("", summary="List Workflows")
async def list_workflows(
    organization_id: str = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all workflows for an organization"""
    try:
        query = {'organization_id': organization_id}
        if status_filter:
            query['status'] = status_filter
        
        workflows = await db.workflows.find(query).sort('created_at', -1).limit(100).to_list(length=100)
        
        return {
            "success": True,
            "workflows": workflows,
            "count": len(workflows)
        }
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get("/{workflow_id}", summary="Get Workflow")
async def get_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get workflow details"""
    try:
        workflow = await db.workflows.find_one({'workflow_id': workflow_id})
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return {
            "success": True,
            "workflow": workflow
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workflow: {str(e)}"
        )


@router.put("/{workflow_id}", summary="Update Workflow")
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update workflow configuration"""
    try:
        updates = {}
        if request.name:
            updates['name'] = request.name
        if request.description:
            updates['description'] = request.description
        if request.steps:
            updates['steps'] = request.steps
        if request.status:
            updates['status'] = request.status
        
        updates['updated_at'] = datetime.utcnow().isoformat()
        updates['updated_by'] = current_user.get('user_id')
        
        result = await db.workflows.update_one(
            {'workflow_id': workflow_id},
            {'$set': updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return {
            "success": True,
            "message": "Workflow updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )


@router.delete("/{workflow_id}", summary="Delete Workflow")
async def delete_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a workflow"""
    try:
        result = await db.workflows.update_one(
            {'workflow_id': workflow_id},
            {'$set': {'status': WorkflowStatus.CANCELLED.value, 'deleted_at': datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workflow: {str(e)}"
        )

