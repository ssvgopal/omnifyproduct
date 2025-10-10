"""
AgentKit API Routes for Omnify Cloud Connect
Provides REST API endpoints for AgentKit agent and workflow management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models.agentkit_models import (
    AgentConfig, AgentExecutionRequest, AgentExecutionResponse,
    WorkflowDefinition, WorkflowExecution, AgentType,
    CreativeIntelligenceInput, MarketingAutomationInput,
    ClientManagementInput, AnalyticsInput
)
from services.agentkit_service import AgentKitService
from core.auth import get_current_user, get_current_organization

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agentkit", tags=["AgentKit"])


# ========== AGENT MANAGEMENT ENDPOINTS ==========

@router.post("/agents", response_model=Dict[str, Any])
async def create_agent(
    agent_config: AgentConfig,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Create a new AgentKit agent"""
    try:
        # Verify organization access
        if agent_config.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied to organization")
        
        result = await agentkit_service.create_agent(agent_config)
        return result
    
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[AgentConfig])
async def list_agents(
    agent_type: Optional[AgentType] = None,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """List all agents for current organization"""
    try:
        organization_id = current_user.get("organization_id")
        agents = await agentkit_service.list_agents(
            organization_id=organization_id,
            agent_type=agent_type
        )
        return agents
    
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=AgentConfig)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Get agent configuration"""
    try:
        agent = await agentkit_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Verify organization access
        if agent.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}", response_model=Dict[str, Any])
async def update_agent(
    agent_id: str,
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Update agent configuration"""
    try:
        # Verify agent exists and user has access
        agent = await agentkit_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Don't allow changing organization_id or agent_id
        updates.pop("organization_id", None)
        updates.pop("agent_id", None)
        
        success = await agentkit_service.update_agent(agent_id, updates)
        return {"success": success, "agent_id": agent_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}", response_model=Dict[str, Any])
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Delete (deactivate) an agent"""
    try:
        # Verify agent exists and user has access
        agent = await agentkit_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await agentkit_service.delete_agent(agent_id)
        return {"success": success, "agent_id": agent_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== AGENT EXECUTION ENDPOINTS ==========

@router.post("/agents/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    agent_id: str,
    input_data: Dict[str, Any],
    request: Request,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute an AgentKit agent"""
    try:
        # Verify agent exists and user has access
        agent = await agentkit_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create execution request
        execution_request = AgentExecutionRequest(
            agent_id=agent_id,
            input_data=input_data,
            user_id=current_user.get("user_id"),
            organization_id=current_user.get("organization_id"),
            context={
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Execute agent
        response = await agentkit_service.execute_agent(execution_request)
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}", response_model=AgentExecutionResponse)
async def get_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Get agent execution details"""
    try:
        execution = await agentkit_service.db.agentkit_executions.find_one(
            {"execution_id": execution_id}
        )
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Verify organization access
        if execution.get("organization_id") != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return AgentExecutionResponse(**execution)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/executions", response_model=List[AgentExecutionResponse])
async def list_agent_executions(
    agent_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """List recent executions for an agent"""
    try:
        # Verify agent exists and user has access
        agent = await agentkit_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get executions
        executions = []
        cursor = agentkit_service.db.agentkit_executions.find(
            {"agent_id": agent_id}
        ).sort("started_at", -1).skip(offset).limit(limit)
        
        async for execution in cursor:
            executions.append(AgentExecutionResponse(**execution))
        
        return executions
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== WORKFLOW ENDPOINTS ==========

@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(
    workflow: WorkflowDefinition,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Create a new AgentKit workflow"""
    try:
        # Verify organization access
        if workflow.organization_id != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied to organization")
        
        result = await agentkit_service.create_workflow(workflow)
        return result
    
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute an AgentKit workflow"""
    try:
        # Verify workflow exists and user has access
        workflow_data = await agentkit_service.db.agentkit_workflows.find_one(
            {"workflow_id": workflow_id}
        )
        
        if not workflow_data:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if workflow_data.get("organization_id") != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Execute workflow
        execution = await agentkit_service.execute_workflow(
            workflow_id=workflow_id,
            input_data=input_data,
            user_id=current_user.get("user_id"),
            organization_id=current_user.get("organization_id")
        )
        
        return execution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/executions/{execution_id}", response_model=WorkflowExecution)
async def get_workflow_execution(
    workflow_id: str,
    execution_id: str,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Get workflow execution details"""
    try:
        execution = await agentkit_service.db.agentkit_workflow_executions.find_one(
            {"execution_id": execution_id, "workflow_id": workflow_id}
        )
        
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        
        # Verify organization access
        if execution.get("organization_id") != current_user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return WorkflowExecution(**execution)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== COMPLIANCE & AUDIT ENDPOINTS ==========

@router.post("/compliance/check", response_model=Dict[str, Any])
async def run_compliance_check(
    check_type: str = "soc2",
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Run compliance check for organization"""
    try:
        organization_id = current_user.get("organization_id")
        
        compliance_check = await agentkit_service.run_compliance_check(
            organization_id=organization_id,
            check_type=check_type
        )
        
        return compliance_check.dict()
    
    except Exception as e:
        logger.error(f"Error running compliance check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs", response_model=List[Dict[str, Any]])
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Get audit logs for organization (SOC 2 compliance)"""
    try:
        organization_id = current_user.get("organization_id")
        
        # Build query
        query = {"organization_id": organization_id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        if action:
            query["action"] = action
        
        # Get audit logs
        logs = []
        cursor = agentkit_service.db.audit_logs.find(query).sort(
            "timestamp", -1
        ).skip(offset).limit(limit)
        
        async for log in cursor:
            # Remove _id for JSON serialization
            log.pop("_id", None)
            logs.append(log)
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ANALYTICS ENDPOINTS ==========

@router.get("/metrics", response_model=Dict[str, Any])
async def get_agent_metrics(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Get agent execution metrics for organization"""
    try:
        organization_id = current_user.get("organization_id")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        metrics = await agentkit_service.get_agent_metrics(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "organization_id": organization_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Error getting agent metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== SPECIALIZED AGENT ENDPOINTS ==========

@router.post("/creative-intelligence/analyze", response_model=Dict[str, Any])
async def analyze_creative(
    input_data: CreativeIntelligenceInput,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute Creative Intelligence Agent"""
    try:
        organization_id = current_user.get("organization_id")
        agent_id = f"{organization_id}_creative_intelligence"
        
        execution_request = AgentExecutionRequest(
            agent_id=agent_id,
            input_data=input_data.dict(),
            user_id=current_user.get("user_id"),
            organization_id=organization_id
        )
        
        response = await agentkit_service.execute_agent(execution_request)
        return response.dict()
    
    except Exception as e:
        logger.error(f"Error analyzing creative: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketing-automation/execute", response_model=Dict[str, Any])
async def execute_marketing_automation(
    input_data: MarketingAutomationInput,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute Marketing Automation Agent"""
    try:
        organization_id = current_user.get("organization_id")
        agent_id = f"{organization_id}_marketing_automation"
        
        execution_request = AgentExecutionRequest(
            agent_id=agent_id,
            input_data=input_data.dict(),
            user_id=current_user.get("user_id"),
            organization_id=organization_id
        )
        
        response = await agentkit_service.execute_agent(execution_request)
        return response.dict()
    
    except Exception as e:
        logger.error(f"Error executing marketing automation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/client-management/execute", response_model=Dict[str, Any])
async def execute_client_management(
    input_data: ClientManagementInput,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute Client Management Agent"""
    try:
        organization_id = current_user.get("organization_id")
        agent_id = f"{organization_id}_client_management"
        
        execution_request = AgentExecutionRequest(
            agent_id=agent_id,
            input_data=input_data.dict(),
            user_id=current_user.get("user_id"),
            organization_id=organization_id
        )
        
        response = await agentkit_service.execute_agent(execution_request)
        return response.dict()
    
    except Exception as e:
        logger.error(f"Error executing client management: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/analyze", response_model=Dict[str, Any])
async def analyze_analytics(
    input_data: AnalyticsInput,
    current_user: dict = Depends(get_current_user),
    agentkit_service: AgentKitService = Depends()
):
    """Execute Analytics Agent"""
    try:
        organization_id = current_user.get("organization_id")
        agent_id = f"{organization_id}_analytics"
        
        # Ensure organization_id matches
        input_data.organization_id = organization_id
        
        execution_request = AgentExecutionRequest(
            agent_id=agent_id,
            input_data=input_data.dict(),
            user_id=current_user.get("user_id"),
            organization_id=organization_id
        )
        
        response = await agentkit_service.execute_agent(execution_request)
        return response.dict()
    
    except Exception as e:
        logger.error(f"Error analyzing analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
