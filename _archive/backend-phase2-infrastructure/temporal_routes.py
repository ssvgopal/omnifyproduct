"""
Temporal Workflow Management Routes
API endpoints for managing Temporal workflows and monitoring execution
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel

from services.temporal_orchestration import (
    temporal_service, ClientOnboardingData, PlatformSyncData, 
    EyesRetrainData, RetentionCampaignData
)
from services.oidc_auth import get_current_user, TokenValidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/temporal", tags=["Temporal Workflow Management"])

# Request/Response Models
class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    workflow_type: str
    data: Dict[str, Any]

class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""
    workflow_id: str
    status: str
    execution_time: Optional[str] = None
    start_time: Optional[str] = None
    close_time: Optional[str] = None
    run_id: str

class WorkflowListResponse(BaseModel):
    """List of workflows response"""
    workflows: List[WorkflowStatusResponse]
    total: int
    page: int
    page_size: int

class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response"""
    workflow_id: str
    status: str
    message: str
    started_at: str

# ========== WORKFLOW MANAGEMENT ROUTES ==========

@router.get("/health")
async def temporal_health_check():
    """Check Temporal service health"""
    try:
        return await temporal_service.health_check()
    except Exception as e:
        logger.error(f"Temporal health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Temporal health check failed: {str(e)}"
        )

@router.post("/workflows/client-onboarding", response_model=WorkflowExecutionResponse)
async def execute_client_onboarding(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Execute client onboarding workflow"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled. Set ENABLE_TEMPORAL=true to enable."
            )

        # Validate workflow data
        try:
            onboarding_data = ClientOnboardingData(**request.data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid client onboarding data: {str(e)}"
            )

        # Execute workflow
        handle = await temporal_service.execute_client_onboarding(onboarding_data)
        
        logger.info("Client onboarding workflow started", extra={
            "workflow_id": handle.id,
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id
        })

        return WorkflowExecutionResponse(
            workflow_id=handle.id,
            status="started",
            message="Client onboarding workflow started successfully",
            started_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start client onboarding workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.post("/workflows/platform-sync", response_model=WorkflowExecutionResponse)
async def execute_platform_sync(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Execute platform synchronization workflow"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled. Set ENABLE_TEMPORAL=true to enable."
            )

        # Validate workflow data
        try:
            sync_data = PlatformSyncData(**request.data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform sync data: {str(e)}"
            )

        # Execute workflow
        handle = await temporal_service.execute_platform_sync(sync_data)
        
        logger.info("Platform sync workflow started", extra={
            "workflow_id": handle.id,
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id,
            "platform": sync_data.platform
        })

        return WorkflowExecutionResponse(
            workflow_id=handle.id,
            status="started",
            message=f"Platform sync workflow started for {sync_data.platform}",
            started_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start platform sync workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.post("/workflows/eyes-retrain", response_model=WorkflowExecutionResponse)
async def execute_eyes_retrain(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Execute EYES module retraining workflow"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled. Set ENABLE_TEMPORAL=true to enable."
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required for model retraining"
            )

        # Validate workflow data
        try:
            retrain_data = EyesRetrainData(**request.data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid EYES retraining data: {str(e)}"
            )

        # Execute workflow
        handle = await temporal_service.execute_eyes_retrain(retrain_data)
        
        logger.info("EYES retraining workflow started", extra={
            "workflow_id": handle.id,
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id,
            "model_type": retrain_data.model_type
        })

        return WorkflowExecutionResponse(
            workflow_id=handle.id,
            status="started",
            message=f"EYES retraining workflow started for {retrain_data.model_type}",
            started_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start EYES retraining workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.post("/workflows/retention-campaign", response_model=WorkflowExecutionResponse)
async def execute_retention_campaign(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Execute retention campaign workflow"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled. Set ENABLE_TEMPORAL=true to enable."
            )

        # Validate workflow data
        try:
            campaign_data = RetentionCampaignData(**request.data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid retention campaign data: {str(e)}"
            )

        # Execute workflow
        handle = await temporal_service.execute_retention_campaign(campaign_data)
        
        logger.info("Retention campaign workflow started", extra={
            "workflow_id": handle.id,
            "user_id": current_user.user_id,
            "organization_id": current_user.organization_id,
            "campaign_id": campaign_data.campaign_id
        })

        return WorkflowExecutionResponse(
            workflow_id=handle.id,
            status="started",
            message=f"Retention campaign workflow started for {campaign_data.campaign_id}",
            started_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start retention campaign workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.get("/workflows/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get workflow status"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled"
            )

        status_info = await temporal_service.get_workflow_status(workflow_id)
        
        return WorkflowStatusResponse(**status_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Cancel a workflow"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required to cancel workflows"
            )

        success = await temporal_service.cancel_workflow(workflow_id)
        
        if success:
            logger.info("Workflow canceled", extra={
                "workflow_id": workflow_id,
                "user_id": current_user.user_id
            })
            
            return {
                "status": "success",
                "message": f"Workflow {workflow_id} canceled successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel workflow"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )

@router.get("/workflows", response_model=WorkflowListResponse)
async def list_workflows(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """List workflows (mock implementation)"""
    try:
        if not temporal_service.enable_temporal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporal is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required to list workflows"
            )

        # Mock implementation - in production, query Temporal for actual workflows
        mock_workflows = [
            WorkflowStatusResponse(
                workflow_id=f"workflow-{i}",
                status="completed" if i % 2 == 0 else "running",
                execution_time="00:05:30" if i % 2 == 0 else None,
                start_time=datetime.utcnow().isoformat(),
                close_time=datetime.utcnow().isoformat() if i % 2 == 0 else None,
                run_id=f"run-{i}"
            )
            for i in range(1, 6)
        ]

        # Apply status filter
        if status_filter:
            mock_workflows = [w for w in mock_workflows if w.status == status_filter]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_workflows = mock_workflows[start_idx:end_idx]

        return WorkflowListResponse(
            workflows=paginated_workflows,
            total=len(mock_workflows),
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )

@router.get("/configuration")
async def get_temporal_configuration(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get Temporal service configuration"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        return {
            "temporal_enabled": temporal_service.enable_temporal,
            "temporal_host": temporal_service.temporal_host,
            "namespace": temporal_service.namespace,
            "task_queue": temporal_service.task_queue,
            "worker_timeout": temporal_service.worker_timeout,
            "connected": temporal_service.client is not None,
            "worker_running": temporal_service.worker_task is not None and not temporal_service.worker_task.done(),
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Temporal configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )
