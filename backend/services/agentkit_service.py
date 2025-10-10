"""
AgentKit Service Layer for Omnify Cloud Connect
Handles AgentKit agent creation, execution, and workflow orchestration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import hashlib
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.agentkit_sdk_client_simulation import AgentKitSDKClient

from models.agentkit_models import (
    AgentConfig, AgentExecutionRequest, AgentExecutionResponse,
    WorkflowDefinition, WorkflowExecution, AgentStatus, WorkflowStatus,
    ComplianceCheck
)

logger = logging.getLogger(__name__)


class AgentKitService:
    """Service for managing AgentKit agents and workflows"""
    
    def __init__(self, db: AsyncIOMotorDatabase, agentkit_api_key: str):
        self.db = db
        self.agentkit_api_key = agentkit_api_key
        # Initialize AgentKit SDK client
        self.agentkit_client = AgentKitSDKClient(api_key=agentkit_api_key)
    
    # ========== AGENT MANAGEMENT ==========
    
    async def create_agent(self, agent_config: AgentConfig) -> Dict[str, Any]:
        """Create a new AgentKit agent"""
        try:
            # Create agent in AgentKit platform
            agentkit_response = await self.agentkit_client.create_agent(
                name=agent_config.name,
                agent_type=agent_config.agent_type,
                config=agent_config.config,
                description=agent_config.description,
                metadata={"organization_id": agent_config.organization_id}
            )
            agent_config.agentkit_agent_id = agentkit_response["agent_id"]

            # Store agent configuration in MongoDB
            agent_dict = agent_config.dict()
            await self.db.agentkit_agents.insert_one(agent_dict)

            logger.info(f"Created agent {agent_config.agent_id} for organization {agent_config.organization_id}")

            return {
                "agent_id": agent_config.agent_id,
                "status": "created",
                "agentkit_agent_id": agent_config.agentkit_agent_id
            }

        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Get agent configuration"""
        agent_data = await self.db.agentkit_agents.find_one({"agent_id": agent_id})
        if agent_data:
            return AgentConfig(**agent_data)
        return None
    
    async def list_agents(self, organization_id: str, agent_type: Optional[str] = None) -> List[AgentConfig]:
        """List all agents for an organization"""
        query = {"organization_id": organization_id, "is_active": True}
        if agent_type:
            query["agent_type"] = agent_type
        
        agents = []
        async for agent_data in self.db.agentkit_agents.find(query):
            agents.append(AgentConfig(**agent_data))
        
        return agents
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Update agent configuration"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.db.agentkit_agents.update_one(
            {"agent_id": agent_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Soft delete an agent"""
        return await self.update_agent(agent_id, {"is_active": False})
    
    # ========== AGENT EXECUTION ==========
    
    async def execute_agent(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        """Execute an AgentKit agent"""
        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        try:
            # Get agent configuration
            agent = await self.get_agent(request.agent_id)
            if not agent:
                raise ValueError(f"Agent {request.agent_id} not found")
            
            # Create audit log
            await self._create_audit_log(
                organization_id=request.organization_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                execution_id=execution_id,
                action="execute_agent",
                input_data=request.input_data
            )
            
            # Execute agent in AgentKit platform
            agentkit_response = await self.agentkit_client.execute_agent(
                agent_id=agent.agentkit_agent_id,
                input_data=request.input_data,
                context=request.context
            )

            output_data = agentkit_response["output_data"]
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()
            
            # Store execution record
            execution_record = {
                "execution_id": execution_id,
                "agent_id": request.agent_id,
                "organization_id": request.organization_id,
                "user_id": request.user_id,
                "status": AgentStatus.COMPLETED,
                "input_data": request.input_data,
                "output_data": output_data,
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_seconds": duration
            }
            await self.db.agentkit_executions.insert_one(execution_record)
            
            response = AgentExecutionResponse(
                execution_id=execution_id,
                agent_id=request.agent_id,
                status=AgentStatus.COMPLETED,
                output_data=output_data,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration
            )
            
            logger.info(f"Agent {request.agent_id} executed successfully in {duration}s")
            return response
        
        except Exception as e:
            logger.error(f"Error executing agent {request.agent_id}: {str(e)}")
            
            # Store failed execution
            execution_record = {
                "execution_id": execution_id,
                "agent_id": request.agent_id,
                "organization_id": request.organization_id,
                "user_id": request.user_id,
                "status": AgentStatus.FAILED,
                "input_data": request.input_data,
                "error": str(e),
                "started_at": started_at,
                "completed_at": datetime.utcnow()
            }
            await self.db.agentkit_executions.insert_one(execution_record)
            return AgentExecutionResponse(
                execution_id=execution_id,
                agent_id=request.agent_id,
                status=AgentStatus.FAILED,
                error=str(e)
            )
    
    # ========== WORKFLOW MANAGEMENT ==========
    
    async def create_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Create a new AgentKit workflow"""
        try:
            # Create workflow in AgentKit platform
            agentkit_response = await self.agentkit_client.create_workflow(
                name=workflow.name,
                description=workflow.description,
                steps=workflow.steps,
                config=workflow.config
            )
            workflow.agentkit_workflow_id = agentkit_response["workflow_id"]

            # Store workflow in MongoDB
            workflow_dict = workflow.dict()
            await self.db.agentkit_workflows.insert_one(workflow_dict)

            logger.info(f"Created workflow {workflow.workflow_id} for organization {workflow.organization_id}")

            return {
                "workflow_id": workflow.workflow_id,
                "status": "created",
                "agentkit_workflow_id": workflow.agentkit_workflow_id
            }

        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        user_id: str,
        organization_id: str
    ) -> WorkflowExecution:
        """Execute an AgentKit workflow"""
        execution_id = str(uuid.uuid4())
        
        try:
            # Get workflow definition
            workflow_data = await self.db.agentkit_workflows.find_one({"workflow_id": workflow_id})
            if not workflow_data:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = WorkflowDefinition(**workflow_data)
            
            # Create workflow execution record
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                organization_id=organization_id,
                user_id=user_id,
                status=WorkflowStatus.IN_PROGRESS,
                input_data=input_data
            )
            
            await self.db.agentkit_workflow_executions.insert_one(execution.dict())
            
            # Execute workflow in AgentKit platform
            agentkit_response = await self.agentkit_client.execute_workflow(
                workflow_id=workflow.agentkit_workflow_id,
                input_data=input_data
            )

            # Update execution status from SDK response
            execution.status = WorkflowStatus.COMPLETED
            execution.output_data = agentkit_response["output_data"]
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = agentkit_response["duration_seconds"]

            # Update execution record
            await self.db.agentkit_workflow_executions.update_one(
                {"execution_id": execution_id},
                {"$set": execution.dict()}
            )

            logger.info(f"Workflow {workflow_id} executed successfully in {execution.duration_seconds}s")
            return execution
        
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            
            # Update execution as failed
            await self.db.agentkit_workflow_executions.update_one(
                {"execution_id": execution_id},
                {"$set": {
                    "status": WorkflowStatus.FAILED,
                    "error": str(e),
                    "completed_at": datetime.utcnow()
                }}
            )
            
            raise
    
    # ========== AUDIT & COMPLIANCE ==========
    
    async def _create_audit_log(
        self,
        organization_id: str,
        user_id: str,
        agent_id: str,
        execution_id: str,
        action: str,
        input_data: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Create audit log for SOC 2 compliance"""
        
        # Hash sensitive data
        input_hash = hashlib.sha256(str(input_data).encode()).hexdigest()
        
        # Calculate retention date (7 years for SOC 2)
        retention_until = datetime.utcnow() + timedelta(days=365 * 7)
        
        audit_log = {
            "log_id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "execution_id": execution_id,
            "action": action,
            "input_data_hash": input_hash,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow(),
            "retention_until": retention_until
        }
        
        await self.db.audit_logs.insert_one(audit_log)
    
    async def run_compliance_check(
        self,
        organization_id: str,
        check_type: str = "soc2"
    ) -> ComplianceCheck:
        """Run compliance check for organization"""
        
        check_id = str(uuid.uuid4())
        findings = []
        recommendations = []
        
        # Check audit logs coverage
        audit_count = await self.db.audit_logs.count_documents({"organization_id": organization_id})
        if audit_count == 0:
            findings.append({
                "severity": "warning",
                "message": "No audit logs found",
                "category": "audit_logging"
            })
            recommendations.append("Ensure all agent executions are being logged")
        
        # Check data retention policies
        expired_logs = await self.db.audit_logs.count_documents({
            "organization_id": organization_id,
            "retention_until": {"$lt": datetime.utcnow()}
        })
        if expired_logs > 0:
            findings.append({
                "severity": "info",
                "message": f"{expired_logs} audit logs ready for archival",
                "category": "data_retention"
            })
        
        # Check agent security configurations
        insecure_agents = await self.db.agentkit_agents.count_documents({
            "organization_id": organization_id,
            "config.encryption_enabled": {"$ne": True}
        })
        if insecure_agents > 0:
            findings.append({
                "severity": "high",
                "message": f"{insecure_agents} agents without encryption enabled",
                "category": "security"
            })
            recommendations.append("Enable encryption for all agent configurations")
        
        # Determine overall status
        high_severity = any(f["severity"] == "high" for f in findings)
        status = "failed" if high_severity else "passed" if not findings else "warning"
        
        compliance_check = ComplianceCheck(
            check_id=check_id,
            organization_id=organization_id,
            check_type=check_type,
            status=status,
            findings=findings,
            recommendations=recommendations,
            checked_at=datetime.utcnow(),
            next_check_at=datetime.utcnow() + timedelta(days=30)  # Monthly checks
        )
        
        # Store compliance check
        await self.db.agentkit_compliance.insert_one(compliance_check.dict())
        
        logger.info(f"Compliance check {check_id} completed with status {status}")
        return compliance_check
    
    # ========== ANALYTICS & MONITORING ==========
    
    async def get_agent_metrics(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get agent execution metrics"""
        
        pipeline = [
            {
                "$match": {
                    "organization_id": organization_id,
                    "started_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$agent_id",
                    "total_executions": {"$sum": 1},
                    "successful_executions": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "failed_executions": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "avg_duration": {"$avg": "$duration_seconds"},
                    "total_duration": {"$sum": "$duration_seconds"}
                }
            }
        ]
        
        metrics = {}
        async for result in self.db.agentkit_executions.aggregate(pipeline):
            agent_id = result["_id"]
            metrics[agent_id] = {
                "total_executions": result["total_executions"],
                "successful_executions": result["successful_executions"],
                "failed_executions": result["failed_executions"],
                "success_rate": result["successful_executions"] / result["total_executions"] if result["total_executions"] > 0 else 0,
                "avg_duration_seconds": result["avg_duration"],
                "total_duration_seconds": result["total_duration"]
            }
        
        return metrics
