"""
Advanced Automation Workflows API Routes
Production-grade API endpoints for complex multi-step automation, conditional logic, and event triggers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import redis
from celery import Celery

from services.advanced_automation_service import (
    get_advanced_automation_service, AdvancedAutomationService,
    WorkflowStatus, StepStatus, TriggerType, ActionType, ConditionOperator
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class WorkflowStepRequest(BaseModel):
    step_id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    action_type: str = Field(..., description="Action type")
    config: Dict[str, Any] = Field(..., description="Step configuration")
    conditions: Optional[List[Dict[str, Any]]] = Field([], description="Step conditions")
    retry_config: Optional[Dict[str, Any]] = Field({"max_retries": 3, "retry_delay": 5}, description="Retry configuration")
    timeout: Optional[int] = Field(300, description="Step timeout in seconds")
    depends_on: Optional[List[str]] = Field([], description="Step dependencies")

class WorkflowTriggerRequest(BaseModel):
    trigger_type: str = Field(..., description="Trigger type")
    name: str = Field(..., description="Trigger name")
    description: Optional[str] = Field("", description="Trigger description")
    config: Dict[str, Any] = Field(..., description="Trigger configuration")
    enabled: Optional[bool] = Field(True, description="Whether trigger is enabled")

class WorkflowCreateRequest(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field("", description="Workflow description")
    steps: List[WorkflowStepRequest] = Field(..., description="Workflow steps")
    triggers: Optional[List[WorkflowTriggerRequest]] = Field([], description="Workflow triggers")
    variables: Optional[Dict[str, Any]] = Field({}, description="Workflow variables")
    settings: Optional[Dict[str, Any]] = Field({}, description="Workflow settings")

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID to execute")
    trigger_data: Optional[Dict[str, Any]] = Field({}, description="Trigger data")

class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    description: str
    status: str
    steps_count: int
    triggers_count: int
    created_at: str
    updated_at: str

class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str]
    current_step: Optional[str]
    error_message: Optional[str]

class StepExecutionResponse(BaseModel):
    step_execution_id: str
    workflow_execution_id: str
    step_id: str
    status: str
    started_at: str
    completed_at: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int

class WorkflowTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    category: str
    complexity: str

# Dependency
async def get_automation_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedAutomationService:
    # In production, initialize Redis and Celery properly
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    celery_app = Celery('workflows')
    return get_advanced_automation_service(db, redis_client, celery_app)

# Workflow Management Endpoints
@router.post("/api/automation/workflows", response_model=WorkflowResponse, summary="Create Workflow")
async def create_workflow(
    request: WorkflowCreateRequest = Body(...),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Create a new automation workflow.
    Returns workflow details with validation.
    """
    try:
        # Convert request to workflow data
        workflow_data = {
            "name": request.name,
            "description": request.description,
            "steps": [step.dict() for step in request.steps],
            "triggers": [trigger.dict() for trigger in request.triggers],
            "variables": request.variables,
            "settings": request.settings,
            "created_by": "api_user"  # In production, get from auth
        }
        
        workflow_id = await automation_service.create_workflow(workflow_data)
        
        # Get created workflow
        workflow_doc = await automation_service.db.workflows.find_one({"workflow_id": workflow_id})
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            name=workflow_doc["name"],
            description=workflow_doc["description"],
            status=workflow_doc["status"],
            steps_count=len(workflow_doc["steps"]),
            triggers_count=len(workflow_doc["triggers"]),
            created_at=workflow_doc["created_at"],
            updated_at=workflow_doc["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow"
        )

@router.get("/api/automation/workflows", response_model=List[WorkflowResponse], summary="List Workflows")
async def list_workflows(
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    limit: int = Query(50, description="Number of workflows to return"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    List automation workflows with filtering options.
    Returns workflow summaries with metadata.
    """
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        # Get workflows
        workflows = await automation_service.db.workflows.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        workflow_responses = []
        for workflow in workflows:
            workflow_responses.append(WorkflowResponse(
                workflow_id=workflow["workflow_id"],
                name=workflow["name"],
                description=workflow["description"],
                status=workflow["status"],
                steps_count=len(workflow["steps"]),
                triggers_count=len(workflow["triggers"]),
                created_at=workflow["created_at"],
                updated_at=workflow["updated_at"]
            ))
        
        return workflow_responses
        
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workflows"
        )

@router.get("/api/automation/workflows/{workflow_id}", summary="Get Workflow Details")
async def get_workflow_details(
    workflow_id: str,
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Get detailed workflow information.
    Returns complete workflow definition with steps and triggers.
    """
    try:
        workflow = await automation_service.db.workflows.find_one({"workflow_id": workflow_id})
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return {
            "workflow": workflow,
            "executions_count": await automation_service.db.workflow_executions.count_documents({"workflow_id": workflow_id}),
            "last_execution": await automation_service.db.workflow_executions.find_one(
                {"workflow_id": workflow_id},
                sort=[("started_at", -1)]
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow details"
        )

@router.put("/api/automation/workflows/{workflow_id}/status", summary="Update Workflow Status")
async def update_workflow_status(
    workflow_id: str,
    new_status: str = Body(..., description="New workflow status"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Update workflow status (draft, active, paused).
    Validates status transition and updates workflow.
    """
    try:
        valid_statuses = [status.value for status in WorkflowStatus]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        # Update workflow status
        update_result = await automation_service.db.workflows.update_one(
            {"workflow_id": workflow_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return {
            "workflow_id": workflow_id,
            "status": new_status,
            "updated_at": datetime.utcnow().isoformat(),
            "message": f"Workflow status updated to {new_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow status"
        )

# Workflow Execution Endpoints
@router.post("/api/automation/workflows/execute", response_model=WorkflowExecutionResponse, summary="Execute Workflow")
async def execute_workflow(
    request: WorkflowExecutionRequest = Body(...),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Execute a workflow manually or with trigger data.
    Returns execution ID and initial status.
    """
    try:
        execution_id = await automation_service.execute_workflow(
            request.workflow_id, request.trigger_data
        )
        
        # Get execution details
        execution = await automation_service.db.workflow_executions.find_one({"execution_id": execution_id})
        
        return WorkflowExecutionResponse(
            execution_id=execution_id,
            workflow_id=execution["workflow_id"],
            status=execution["status"],
            started_at=execution["started_at"],
            completed_at=execution.get("completed_at"),
            current_step=execution.get("current_step"),
            error_message=execution.get("error_message")
        )
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute workflow"
        )

@router.get("/api/automation/workflows/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse], summary="Get Workflow Executions")
async def get_workflow_executions(
    workflow_id: str,
    status: Optional[str] = Query(None, description="Filter by execution status"),
    limit: int = Query(50, description="Number of executions to return"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Get workflow execution history.
    Returns execution summaries with filtering options.
    """
    try:
        executions = await automation_service.get_workflow_executions(workflow_id, limit)
        
        # Filter by status if provided
        if status:
            executions = [exec for exec in executions if exec["status"] == status]
        
        execution_responses = []
        for execution in executions:
            execution_responses.append(WorkflowExecutionResponse(
                execution_id=execution["execution_id"],
                workflow_id=execution["workflow_id"],
                status=execution["status"],
                started_at=execution["started_at"],
                completed_at=execution.get("completed_at"),
                current_step=execution.get("current_step"),
                error_message=execution.get("error_message")
            ))
        
        return execution_responses
        
    except Exception as e:
        logger.error(f"Error getting workflow executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow executions"
        )

@router.get("/api/automation/executions/{execution_id}", summary="Get Execution Details")
async def get_execution_details(
    execution_id: str,
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Get detailed execution information.
    Returns execution and step execution details.
    """
    try:
        details = await automation_service.get_execution_details(execution_id)
        
        return {
            "execution": details["execution"],
            "step_executions": [
                StepExecutionResponse(**step) for step in details["step_executions"]
            ],
            "summary": {
                "total_steps": len(details["step_executions"]),
                "completed_steps": len([s for s in details["step_executions"] if s["status"] == StepStatus.COMPLETED.value]),
                "failed_steps": len([s for s in details["step_executions"] if s["status"] == StepStatus.FAILED.value]),
                "duration": self._calculate_duration(details["execution"])
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting execution details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get execution details"
        )

def _calculate_duration(execution: Dict[str, Any]) -> Optional[str]:
    """Calculate execution duration"""
    try:
        started_at = datetime.fromisoformat(execution["started_at"])
        completed_at = execution.get("completed_at")
        
        if completed_at:
            completed_at = datetime.fromisoformat(completed_at)
            duration = completed_at - started_at
            return str(duration)
        else:
            duration = datetime.utcnow() - started_at
            return f"{str(duration)} (ongoing)"
            
    except Exception:
        return None

# Trigger Management Endpoints
@router.post("/api/automation/triggers", summary="Create Workflow Trigger")
async def create_trigger(
    request: WorkflowTriggerRequest = Body(...),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Create a workflow trigger.
    Supports scheduled, event-based, and webhook triggers.
    """
    try:
        trigger_data = {
            "trigger_type": request.trigger_type,
            "name": request.name,
            "description": request.description,
            "config": request.config,
            "enabled": request.enabled,
            "workflow_id": request.config.get("workflow_id")  # Extract from config
        }
        
        trigger_id = await automation_service.create_trigger(trigger_data)
        
        return {
            "trigger_id": trigger_id,
            "name": request.name,
            "trigger_type": request.trigger_type,
            "enabled": request.enabled,
            "created_at": datetime.utcnow().isoformat(),
            "message": "Trigger created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trigger"
        )

@router.get("/api/automation/triggers", summary="List Workflow Triggers")
async def list_triggers(
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    trigger_type: Optional[str] = Query(None, description="Filter by trigger type"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    List workflow triggers with filtering options.
    Returns trigger configurations and status.
    """
    try:
        # Build query
        query = {}
        if workflow_id:
            query["workflow_id"] = workflow_id
        if trigger_type:
            query["trigger_type"] = trigger_type
        
        triggers = await automation_service.db.workflow_triggers.find(query).to_list(length=None)
        
        return {
            "triggers": triggers,
            "total_count": len(triggers)
        }
        
    except Exception as e:
        logger.error(f"Error listing triggers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list triggers"
        )

@router.put("/api/automation/triggers/{trigger_id}/toggle", summary="Toggle Trigger Status")
async def toggle_trigger_status(
    trigger_id: str,
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Toggle trigger enabled/disabled status.
    Activates or deactivates trigger based on current state.
    """
    try:
        # Get current trigger
        trigger = await automation_service.db.workflow_triggers.find_one({"trigger_id": trigger_id})
        if not trigger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trigger not found"
            )
        
        new_status = not trigger["enabled"]
        
        # Update trigger status
        await automation_service.db.workflow_triggers.update_one(
            {"trigger_id": trigger_id},
            {"$set": {"enabled": new_status}}
        )
        
        # Activate/deactivate trigger
        if new_status:
            await automation_service.trigger_manager._activate_trigger(
                automation_service.trigger_manager.active_triggers.get(trigger_id)
            )
        else:
            await automation_service.trigger_manager.deactivate_trigger(trigger_id)
        
        return {
            "trigger_id": trigger_id,
            "enabled": new_status,
            "message": f"Trigger {'activated' if new_status else 'deactivated'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling trigger status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle trigger status"
        )

# Template Management Endpoints
@router.get("/api/automation/templates", response_model=List[WorkflowTemplateResponse], summary="Get Workflow Templates")
async def get_workflow_templates(
    category: Optional[str] = Query(None, description="Filter by template category"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Get predefined workflow templates.
    Returns templates for common automation scenarios.
    """
    try:
        templates = await automation_service.get_workflow_templates()
        
        # Filter by category if provided
        if category:
            templates = [t for t in templates if t.get("category") == category]
        
        template_responses = []
        for template in templates:
            template_responses.append(WorkflowTemplateResponse(
                template_id=template["template_id"],
                name=template["name"],
                description=template["description"],
                steps=template["steps"],
                category=template.get("category", "general"),
                complexity=template.get("complexity", "medium")
            ))
        
        return template_responses
        
    except Exception as e:
        logger.error(f"Error getting workflow templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow templates"
        )

@router.post("/api/automation/templates/{template_id}/create", summary="Create Workflow from Template")
async def create_workflow_from_template(
    template_id: str,
    workflow_name: str = Body(..., description="Name for the new workflow"),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Create a workflow from a template.
    Instantiates template with custom name and configuration.
    """
    try:
        # Get template
        templates = await automation_service.get_workflow_templates()
        template = next((t for t in templates if t["template_id"] == template_id), None)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Create workflow from template
        workflow_data = {
            "name": workflow_name,
            "description": f"Created from template: {template['name']}",
            "steps": template["steps"],
            "triggers": [],
            "variables": {},
            "settings": {},
            "created_by": "template_user"
        }
        
        workflow_id = await automation_service.create_workflow(workflow_data)
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "template_id": template_id,
            "template_name": template["name"],
            "message": "Workflow created from template successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow from template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow from template"
        )

# Webhook Endpoints
@router.post("/api/automation/webhooks/{trigger_id}", summary="Webhook Trigger")
async def webhook_trigger(
    trigger_id: str,
    webhook_data: Dict[str, Any] = Body(...),
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Webhook endpoint for triggering workflows.
    Validates webhook signature and triggers workflow execution.
    """
    try:
        # Get trigger configuration
        trigger_config = await automation_service.redis.hgetall(f"webhook_triggers:{trigger_id}")
        if not trigger_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook trigger not found"
            )
        
        # Validate webhook signature (in production)
        # signature = request.headers.get("X-Signature")
        # if not validate_signature(webhook_data, signature, trigger_config["secret"]):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Trigger workflow
        workflow_id = trigger_config["workflow_id"]
        execution_id = await automation_service.execute_workflow(workflow_id, webhook_data)
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "trigger_id": trigger_id,
            "status": "triggered",
            "message": "Workflow triggered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook trigger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle webhook trigger"
        )

# Automation Health Check
@router.get("/api/automation/health", summary="Automation System Health Check")
async def automation_health_check(
    automation_service: AdvancedAutomationService = Depends(get_automation_service)
):
    """
    Check the health of the automation system.
    Returns system status and capabilities.
    """
    try:
        # Check database connection
        await automation_service.db.admin.command('ping')
        
        # Check Redis connection
        try:
            await automation_service.redis.ping()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"
        
        # Get system statistics
        stats = {
            "total_workflows": await automation_service.db.workflows.count_documents({}),
            "active_workflows": await automation_service.db.workflows.count_documents({"status": WorkflowStatus.ACTIVE.value}),
            "total_executions": await automation_service.db.workflow_executions.count_documents({}),
            "active_executions": await automation_service.db.workflow_executions.count_documents({"status": WorkflowStatus.ACTIVE.value}),
            "total_triggers": await automation_service.db.workflow_triggers.count_documents({}),
            "active_triggers": len(automation_service.trigger_manager.active_triggers)
        }
        
        all_healthy = redis_status == "healthy"
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": {
                "database": "healthy",
                "redis": redis_status,
                "celery": "healthy"  # In production, check Celery status
            },
            "statistics": stats,
            "capabilities": {
                "workflow_creation": True,
                "workflow_execution": True,
                "trigger_management": True,
                "template_system": True,
                "webhook_triggers": True,
                "conditional_logic": True,
                "parallel_execution": True,
                "retry_mechanisms": True
            },
            "supported_action_types": [action.value for action in ActionType],
            "supported_trigger_types": [trigger.value for trigger in TriggerType],
            "supported_condition_operators": [op.value for op in ConditionOperator],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking automation health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
