"""
Temporal Workflow Orchestration Service
Enterprise-grade workflow orchestration with durable, scalable, code-first workflows
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

from temporalio import workflow, activity
from temporalio.client import Client, WorkflowHandle
from temporalio.worker import Worker
from temporalio.common import RetryPolicy
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TERMINATED = "terminated"

class ActivityStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class WorkflowContext:
    """Context for workflow execution"""
    workflow_id: str
    organization_id: str
    user_id: str
    tenant_key: str
    started_at: datetime
    timeout: timedelta

class ClientOnboardingData(BaseModel):
    """Data for client onboarding workflow"""
    client_id: str
    organization_id: str
    user_id: str
    email: str
    plan_tier: str
    integrations: List[str]
    preferences: Dict[str, Any]

class PlatformSyncData(BaseModel):
    """Data for platform synchronization workflow"""
    organization_id: str
    platform: str
    sync_type: str  # full, incremental, delta
    last_sync: Optional[datetime]
    filters: Dict[str, Any]

class EyesRetrainData(BaseModel):
    """Data for EYES module retraining workflow"""
    organization_id: str
    model_type: str  # clustering, churn_prediction, segmentation
    training_data_size: int
    parameters: Dict[str, Any]

class RetentionCampaignData(BaseModel):
    """Data for retention campaign workflow"""
    organization_id: str
    campaign_id: str
    target_segments: List[str]
    channels: List[str]
    content_templates: List[str]

# ========== ACTIVITY FUNCTIONS ==========

@activity.defn
async def validate_client_data(data: ClientOnboardingData) -> Dict[str, Any]:
    """Validate client onboarding data"""
    try:
        logger.info(f"Validating client data for {data.client_id}")
        
        # Simulate validation logic
        await asyncio.sleep(1)
        
        validation_result = {
            "valid": True,
            "client_id": data.client_id,
            "organization_id": data.organization_id,
            "plan_tier": data.plan_tier,
            "integrations_count": len(data.integrations),
            "validated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Client data validation completed for {data.client_id}")
        return validation_result
        
    except Exception as e:
        logger.error(f"Client data validation failed: {str(e)}")
        raise

@activity.defn
async def setup_client_integrations(data: ClientOnboardingData) -> Dict[str, Any]:
    """Setup client integrations"""
    try:
        logger.info(f"Setting up integrations for client {data.client_id}")
        
        integration_results = {}
        
        for integration in data.integrations:
            logger.info(f"Setting up {integration} integration")
            await asyncio.sleep(2)  # Simulate integration setup
            
            integration_results[integration] = {
                "status": "configured",
                "configured_at": datetime.utcnow().isoformat()
            }
        
        result = {
            "client_id": data.client_id,
            "integrations": integration_results,
            "setup_completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Integration setup completed for client {data.client_id}")
        return result
        
    except Exception as e:
        logger.error(f"Integration setup failed: {str(e)}")
        raise

@activity.defn
async def create_client_dashboard(data: ClientOnboardingData) -> Dict[str, Any]:
    """Create client dashboard"""
    try:
        logger.info(f"Creating dashboard for client {data.client_id}")
        
        await asyncio.sleep(3)  # Simulate dashboard creation
        
        dashboard_result = {
            "client_id": data.client_id,
            "dashboard_id": f"dashboard_{data.client_id}",
            "widgets": ["overview", "campaigns", "analytics", "integrations"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Dashboard created for client {data.client_id}")
        return dashboard_result
        
    except Exception as e:
        logger.error(f"Dashboard creation failed: {str(e)}")
        raise

@activity.defn
async def sync_platform_data(data: PlatformSyncData) -> Dict[str, Any]:
    """Sync data from external platform"""
    try:
        logger.info(f"Syncing {data.platform} data for org {data.organization_id}")
        
        # Simulate platform sync
        await asyncio.sleep(5)
        
        sync_result = {
            "organization_id": data.organization_id,
            "platform": data.platform,
            "sync_type": data.sync_type,
            "records_synced": 1000,  # Mock data
            "sync_duration": 5.0,
            "synced_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Platform sync completed for {data.platform}")
        return sync_result
        
    except Exception as e:
        logger.error(f"Platform sync failed: {str(e)}")
        raise

@activity.defn
async def retrain_eyes_model(data: EyesRetrainData) -> Dict[str, Any]:
    """Retrain EYES module model"""
    try:
        logger.info(f"Retraining {data.model_type} model for org {data.organization_id}")
        
        # Simulate model training
        await asyncio.sleep(10)
        
        training_result = {
            "organization_id": data.organization_id,
            "model_type": data.model_type,
            "training_data_size": data.training_data_size,
            "model_accuracy": 0.85,  # Mock accuracy
            "training_duration": 10.0,
            "trained_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Model retraining completed for {data.model_type}")
        return training_result
        
    except Exception as e:
        logger.error(f"Model retraining failed: {str(e)}")
        raise

@activity.defn
async def create_retention_campaign(data: RetentionCampaignData) -> Dict[str, Any]:
    """Create retention campaign"""
    try:
        logger.info(f"Creating retention campaign {data.campaign_id}")
        
        # Simulate campaign creation
        await asyncio.sleep(3)
        
        campaign_result = {
            "organization_id": data.organization_id,
            "campaign_id": data.campaign_id,
            "target_segments": data.target_segments,
            "channels": data.channels,
            "content_templates": data.content_templates,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Retention campaign created: {data.campaign_id}")
        return campaign_result
        
    except Exception as e:
        logger.error(f"Retention campaign creation failed: {str(e)}")
        raise

# ========== WORKFLOW DEFINITIONS ==========

@workflow.defn
class ClientOnboardingWorkflow:
    """Client onboarding workflow"""
    
    @workflow.run
    async def run(self, data: ClientOnboardingData) -> Dict[str, Any]:
        """Execute client onboarding workflow"""
        try:
            logger.info(f"Starting client onboarding workflow for {data.client_id}")
            
            # Step 1: Validate client data
            validation_result = await workflow.execute_activity(
                validate_client_data,
                data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(max_attempts=3)
            )
            
            if not validation_result.get("valid", False):
                raise ValueError("Client data validation failed")
            
            # Step 2: Setup integrations
            integration_result = await workflow.execute_activity(
                setup_client_integrations,
                data,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(max_attempts=3)
            )
            
            # Step 3: Create dashboard
            dashboard_result = await workflow.execute_activity(
                create_client_dashboard,
                data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(max_attempts=3)
            )
            
            # Compile final result
            result = {
                "workflow_id": workflow.info().workflow_id,
                "client_id": data.client_id,
                "organization_id": data.organization_id,
                "status": "completed",
                "validation": validation_result,
                "integrations": integration_result,
                "dashboard": dashboard_result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Client onboarding workflow completed for {data.client_id}")
            return result
            
        except Exception as e:
            logger.error(f"Client onboarding workflow failed: {str(e)}")
            raise

@workflow.defn
class PlatformSyncWorkflow:
    """Platform synchronization workflow"""
    
    @workflow.run
    async def run(self, data: PlatformSyncData) -> Dict[str, Any]:
        """Execute platform sync workflow"""
        try:
            logger.info(f"Starting platform sync workflow for {data.platform}")
            
            # Execute platform sync
            sync_result = await workflow.execute_activity(
                sync_platform_data,
                data,
                start_to_close_timeout=timedelta(minutes=30),
                retry_policy=RetryPolicy(max_attempts=3)
            )
            
            result = {
                "workflow_id": workflow.info().workflow_id,
                "organization_id": data.organization_id,
                "platform": data.platform,
                "status": "completed",
                "sync_result": sync_result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Platform sync workflow completed for {data.platform}")
            return result
            
        except Exception as e:
            logger.error(f"Platform sync workflow failed: {str(e)}")
            raise

@workflow.defn
class EyesRetrainWorkflow:
    """EYES module retraining workflow"""
    
    @workflow.run
    async def run(self, data: EyesRetrainData) -> Dict[str, Any]:
        """Execute EYES retraining workflow"""
        try:
            logger.info(f"Starting EYES retraining workflow for {data.model_type}")
            
            # Execute model retraining
            training_result = await workflow.execute_activity(
                retrain_eyes_model,
                data,
                start_to_close_timeout=timedelta(minutes=60),
                retry_policy=RetryPolicy(max_attempts=2)
            )
            
            result = {
                "workflow_id": workflow.info().workflow_id,
                "organization_id": data.organization_id,
                "model_type": data.model_type,
                "status": "completed",
                "training_result": training_result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"EYES retraining workflow completed for {data.model_type}")
            return result
            
        except Exception as e:
            logger.error(f"EYES retraining workflow failed: {str(e)}")
            raise

@workflow.defn
class RetentionCampaignWorkflow:
    """Retention campaign workflow"""
    
    @workflow.run
    async def run(self, data: RetentionCampaignData) -> Dict[str, Any]:
        """Execute retention campaign workflow"""
        try:
            logger.info(f"Starting retention campaign workflow for {data.campaign_id}")
            
            # Execute campaign creation
            campaign_result = await workflow.execute_activity(
                create_retention_campaign,
                data,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(max_attempts=3)
            )
            
            result = {
                "workflow_id": workflow.info().workflow_id,
                "organization_id": data.organization_id,
                "campaign_id": data.campaign_id,
                "status": "completed",
                "campaign_result": campaign_result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retention campaign workflow completed for {data.campaign_id}")
            return result
            
        except Exception as e:
            logger.error(f"Retention campaign workflow failed: {str(e)}")
            raise

# ========== TEMPORAL CLIENT SERVICE ==========

class TemporalService:
    """
    Temporal Workflow Orchestration Service
    Manages workflow execution and monitoring
    """

    def __init__(self):
        self.enable_temporal = os.getenv("ENABLE_TEMPORAL", "false").lower() == "true"
        self.temporal_host = os.getenv("TEMPORAL_HOST", "temporal:7233")
        self.namespace = os.getenv("TEMPORAL_NAMESPACE", "omnify")
        self.task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "omnify-tasks")
        self.worker_timeout = int(os.getenv("TEMPORAL_WORKER_TIMEOUT", "300"))
        
        self.client: Optional[Client] = None
        self.worker: Optional[Worker] = None
        self.worker_task: Optional[asyncio.Task] = None

        logger.info(f"Temporal Service initialized", extra={
            "enabled": self.enable_temporal,
            "temporal_host": self.temporal_host,
            "namespace": self.namespace,
            "task_queue": self.task_queue
        })

    async def connect(self) -> bool:
        """Connect to Temporal server"""
        try:
            if not self.enable_temporal:
                logger.info("Temporal is disabled")
                return False

            self.client = await Client.connect(self.temporal_host)
            logger.info("Connected to Temporal server")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Temporal: {str(e)}")
            return False

    async def start_worker(self) -> bool:
        """Start Temporal worker"""
        try:
            if not self.client:
                logger.error("Temporal client not connected")
                return False

            self.worker = Worker(
                self.client,
                task_queue=self.task_queue,
                workflows=[
                    ClientOnboardingWorkflow,
                    PlatformSyncWorkflow,
                    EyesRetrainWorkflow,
                    RetentionCampaignWorkflow
                ],
                activities=[
                    validate_client_data,
                    setup_client_integrations,
                    create_client_dashboard,
                    sync_platform_data,
                    retrain_eyes_model,
                    create_retention_campaign
                ]
            )

            # Start worker in background
            self.worker_task = asyncio.create_task(self.worker.run())
            logger.info("Temporal worker started")
            return True

        except Exception as e:
            logger.error(f"Failed to start Temporal worker: {str(e)}")
            return False

    async def execute_client_onboarding(self, data: ClientOnboardingData) -> WorkflowHandle:
        """Execute client onboarding workflow"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            workflow_id = f"client-onboarding-{data.client_id}-{int(datetime.utcnow().timestamp())}"
            
            handle = await self.client.start_workflow(
                ClientOnboardingWorkflow.run,
                data,
                id=workflow_id,
                task_queue=self.task_queue
            )

            logger.info(f"Started client onboarding workflow: {workflow_id}")
            return handle

        except Exception as e:
            logger.error(f"Failed to start client onboarding workflow: {str(e)}")
            raise

    async def execute_platform_sync(self, data: PlatformSyncData) -> WorkflowHandle:
        """Execute platform sync workflow"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            workflow_id = f"platform-sync-{data.platform}-{data.organization_id}-{int(datetime.utcnow().timestamp())}"
            
            handle = await self.client.start_workflow(
                PlatformSyncWorkflow.run,
                data,
                id=workflow_id,
                task_queue=self.task_queue
            )

            logger.info(f"Started platform sync workflow: {workflow_id}")
            return handle

        except Exception as e:
            logger.error(f"Failed to start platform sync workflow: {str(e)}")
            raise

    async def execute_eyes_retrain(self, data: EyesRetrainData) -> WorkflowHandle:
        """Execute EYES retraining workflow"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            workflow_id = f"eyes-retrain-{data.model_type}-{data.organization_id}-{int(datetime.utcnow().timestamp())}"
            
            handle = await self.client.start_workflow(
                EyesRetrainWorkflow.run,
                data,
                id=workflow_id,
                task_queue=self.task_queue
            )

            logger.info(f"Started EYES retraining workflow: {workflow_id}")
            return handle

        except Exception as e:
            logger.error(f"Failed to start EYES retraining workflow: {str(e)}")
            raise

    async def execute_retention_campaign(self, data: RetentionCampaignData) -> WorkflowHandle:
        """Execute retention campaign workflow"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            workflow_id = f"retention-campaign-{data.campaign_id}-{int(datetime.utcnow().timestamp())}"
            
            handle = await self.client.start_workflow(
                RetentionCampaignWorkflow.run,
                data,
                id=workflow_id,
                task_queue=self.task_queue
            )

            logger.info(f"Started retention campaign workflow: {workflow_id}")
            return handle

        except Exception as e:
            logger.error(f"Failed to start retention campaign workflow: {str(e)}")
            raise

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            handle = self.client.get_workflow_handle(workflow_id)
            status = await handle.describe()
            
            return {
                "workflow_id": workflow_id,
                "status": status.status.name.lower(),
                "execution_time": status.execution_time.isoformat() if status.execution_time else None,
                "start_time": status.start_time.isoformat() if status.start_time else None,
                "close_time": status.close_time.isoformat() if status.close_time else None,
                "run_id": status.run_id
            }

        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            raise

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        try:
            if not self.client:
                raise RuntimeError("Temporal client not connected")

            handle = self.client.get_workflow_handle(workflow_id)
            await handle.cancel()
            
            logger.info(f"Canceled workflow: {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel workflow: {str(e)}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Health check for Temporal service"""
        try:
            if not self.enable_temporal:
                return {
                    "status": "disabled",
                    "temporal_enabled": False,
                    "timestamp": datetime.utcnow().isoformat()
                }

            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Temporal client not connected",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Test connection
            await self.client.list_workflows()
            
            return {
                "status": "healthy",
                "temporal_enabled": self.enable_temporal,
                "connected": True,
                "worker_running": self.worker_task is not None and not self.worker_task.done(),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Temporal health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close Temporal connections"""
        try:
            if self.worker_task:
                self.worker_task.cancel()
                try:
                    await self.worker_task
                except asyncio.CancelledError:
                    pass

            if self.client:
                await self.client.close()

            logger.info("Temporal service closed")

        except Exception as e:
            logger.error(f"Error closing Temporal service: {str(e)}")

# Global instance
temporal_service = TemporalService()
