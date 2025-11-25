"""
Advanced Automation Workflows System
Production-grade automation with complex multi-step workflows, conditional logic, and event triggers
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
# Phase 1 deprecated - MongoDB archived (MVP uses Supabase)
# from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
from celery import Celery
from celery.result import AsyncResult
import redis
import yaml

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(str, Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class TriggerType(str, Enum):
    """Workflow trigger types"""
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    MANUAL = "manual"
    API_CALL = "api_call"
    WEBHOOK = "webhook"
    CONDITIONAL = "conditional"

class ActionType(str, Enum):
    """Workflow action types"""
    SEND_EMAIL = "send_email"
    CREATE_CAMPAIGN = "create_campaign"
    UPDATE_BUDGET = "update_budget"
    PAUSE_CAMPAIGN = "pause_campaign"
    RESUME_CAMPAIGN = "resume_campaign"
    SEND_NOTIFICATION = "send_notification"
    UPDATE_TARGETING = "update_targeting"
    GENERATE_REPORT = "generate_report"
    CALL_API = "call_api"
    WAIT = "wait"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"

class ConditionOperator(str, Enum):
    """Condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""
    trigger_id: str
    trigger_type: TriggerType
    name: str
    description: str
    config: Dict[str, Any]
    enabled: bool
    created_at: datetime

@dataclass
class WorkflowStep:
    """Workflow step definition"""
    step_id: str
    name: str
    action_type: ActionType
    config: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    retry_config: Dict[str, Any]
    timeout: int
    depends_on: List[str]

@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    current_step: Optional[str]
    context: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int

@dataclass
class StepExecution:
    """Step execution instance"""
    step_execution_id: str
    workflow_execution_id: str
    step_id: str
    status: StepStatus
    started_at: datetime
    completed_at: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int

class WorkflowEngine:
    """Core workflow execution engine"""
    
    def __init__(self, db=None, redis_client: redis.Redis=None, celery_app=None):
        # Phase 1/3 deprecated - MongoDB and Celery archived for MVP
        self.db = None  # Phase 1: MongoDB archived
        self.redis = redis_client
        self.celery = None  # Phase 3: Celery archived
        self.action_handlers = self._initialize_action_handlers()
        self.condition_evaluators = self._initialize_condition_evaluators()
    
    def _initialize_action_handlers(self) -> Dict[ActionType, Callable]:
        """Initialize action handlers for different action types"""
        return {
            ActionType.SEND_EMAIL: self._handle_send_email,
            ActionType.CREATE_CAMPAIGN: self._handle_create_campaign,
            ActionType.UPDATE_BUDGET: self._handle_update_budget,
            ActionType.PAUSE_CAMPAIGN: self._handle_pause_campaign,
            ActionType.RESUME_CAMPAIGN: self._handle_resume_campaign,
            ActionType.SEND_NOTIFICATION: self._handle_send_notification,
            ActionType.UPDATE_TARGETING: self._handle_update_targeting,
            ActionType.GENERATE_REPORT: self._handle_generate_report,
            ActionType.CALL_API: self._handle_call_api,
            ActionType.WAIT: self._handle_wait,
            ActionType.CONDITION: self._handle_condition,
            ActionType.LOOP: self._handle_loop,
            ActionType.PARALLEL: self._handle_parallel
        }
    
    def _initialize_condition_evaluators(self) -> Dict[ConditionOperator, Callable]:
        """Initialize condition evaluators"""
        return {
            ConditionOperator.EQUALS: lambda a, b: a == b,
            ConditionOperator.NOT_EQUALS: lambda a, b: a != b,
            ConditionOperator.GREATER_THAN: lambda a, b: a > b,
            ConditionOperator.LESS_THAN: lambda a, b: a < b,
            ConditionOperator.GREATER_EQUAL: lambda a, b: a >= b,
            ConditionOperator.LESS_EQUAL: lambda a, b: a <= b,
            ConditionOperator.CONTAINS: lambda a, b: b in a if isinstance(a, str) else False,
            ConditionOperator.NOT_CONTAINS: lambda a, b: b not in a if isinstance(a, str) else True,
            ConditionOperator.IN: lambda a, b: a in b if isinstance(b, (list, tuple)) else False,
            ConditionOperator.NOT_IN: lambda a, b: a not in b if isinstance(b, (list, tuple)) else True
        }
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Validate workflow structure
            await self._validate_workflow(workflow_data)
            
            # Create workflow document
            workflow_doc = {
                "workflow_id": workflow_id,
                "name": workflow_data["name"],
                "description": workflow_data.get("description", ""),
                "status": WorkflowStatus.DRAFT.value,
                "triggers": [trigger.__dict__ for trigger in workflow_data.get("triggers", [])],
                "steps": [step.__dict__ for step in workflow_data.get("steps", [])],
                "variables": workflow_data.get("variables", {}),
                "settings": workflow_data.get("settings", {}),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "created_by": workflow_data.get("created_by", "system")
            }
            
            await self.db.workflows.insert_one(workflow_doc)
            
            logger.info(f"Created workflow {workflow_id}: {workflow_data['name']}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Optional[Dict[str, Any]] = None) -> str:
        """Execute a workflow"""
        try:
            # Get workflow definition
            workflow_doc = await self.db.workflows.find_one({"workflow_id": workflow_id})
            if not workflow_doc:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow_doc["status"] != WorkflowStatus.ACTIVE.value:
                raise ValueError(f"Workflow {workflow_id} is not active")
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.ACTIVE,
                started_at=datetime.utcnow(),
                completed_at=None,
                current_step=None,
                context=trigger_data or {},
                error_message=None,
                retry_count=0
            )
            
            # Save execution to database
            await self._save_execution(execution)
            
            # Start workflow execution asynchronously
            await self._execute_workflow_async(execution)
            
            logger.info(f"Started workflow execution {execution_id} for workflow {workflow_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise
    
    async def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        try:
            # Get workflow definition
            workflow_doc = await self.db.workflows.find_one({"workflow_id": execution.workflow_id})
            steps = workflow_doc["steps"]
            
            # Execute steps in order
            for step_data in steps:
                step = WorkflowStep(**step_data)
                
                # Check if step should be executed based on dependencies
                if not await self._check_step_dependencies(execution.execution_id, step.depends_on):
                    continue
                
                # Execute step
                await self._execute_step(execution, step)
                
                # Check if workflow should continue
                if execution.status in [WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                    break
            
            # Mark workflow as completed
            if execution.status == WorkflowStatus.ACTIVE:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
            
            await self._save_execution(execution)
            
        except Exception as e:
            logger.error(f"Error in async workflow execution: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await self._save_execution(execution)
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep):
        """Execute a single workflow step"""
        try:
            # Create step execution
            step_execution = StepExecution(
                step_execution_id=str(uuid.uuid4()),
                workflow_execution_id=execution.execution_id,
                step_id=step.step_id,
                status=StepStatus.RUNNING,
                started_at=datetime.utcnow(),
                completed_at=None,
                input_data=execution.context,
                output_data={},
                error_message=None,
                retry_count=0
            )
            
            # Save step execution
            await self._save_step_execution(step_execution)
            
            # Check conditions
            if not await self._evaluate_conditions(step.conditions, execution.context):
                step_execution.status = StepStatus.SKIPPED
                step_execution.completed_at = datetime.utcnow()
                await self._save_step_execution(step_execution)
                return
            
            # Execute action
            action_handler = self.action_handlers.get(step.action_type)
            if not action_handler:
                raise ValueError(f"No handler for action type {step.action_type}")
            
            # Execute with retry logic
            max_retries = step.retry_config.get("max_retries", 3)
            retry_delay = step.retry_config.get("retry_delay", 5)
            
            for attempt in range(max_retries + 1):
                try:
                    result = await action_handler(step.config, execution.context)
                    step_execution.output_data = result
                    step_execution.status = StepStatus.COMPLETED
                    step_execution.completed_at = datetime.utcnow()
                    break
                    
                except Exception as e:
                    if attempt < max_retries:
                        step_execution.retry_count += 1
                        step_execution.status = StepStatus.RETRYING
                        await self._save_step_execution(step_execution)
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        step_execution.status = StepStatus.FAILED
                        step_execution.error_message = str(e)
                        step_execution.completed_at = datetime.utcnow()
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = str(e)
                        break
            
            # Update execution context with step output
            execution.context.update(step_execution.output_data)
            
            # Save step execution
            await self._save_step_execution(step_execution)
            
        except Exception as e:
            logger.error(f"Error executing step {step.step_id}: {e}")
            raise
    
    async def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Evaluate step conditions"""
        try:
            if not conditions:
                return True
            
            for condition in conditions:
                field = condition.get("field")
                operator = condition.get("operator")
                value = condition.get("value")
                
                if not all([field, operator, value]):
                    continue
                
                # Get field value from context
                field_value = self._get_nested_value(context, field)
                
                # Evaluate condition
                evaluator = self.condition_evaluators.get(ConditionOperator(operator))
                if not evaluator:
                    continue
                
                if not evaluator(field_value, value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        try:
            keys = field_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting nested value for {field_path}: {e}")
            return None
    
    async def _check_step_dependencies(self, execution_id: str, depends_on: List[str]) -> bool:
        """Check if step dependencies are satisfied"""
        try:
            if not depends_on:
                return True
            
            # Get completed steps for this execution
            completed_steps = await self.db.step_executions.find({
                "workflow_execution_id": execution_id,
                "status": StepStatus.COMPLETED.value
            }).to_list(length=None)
            
            completed_step_ids = [step["step_id"] for step in completed_steps]
            
            # Check if all dependencies are completed
            return all(dep in completed_step_ids for dep in depends_on)
            
        except Exception as e:
            logger.error(f"Error checking step dependencies: {e}")
            return False
    
    # Action Handlers
    async def _handle_send_email(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send email action"""
        try:
            # Mock email sending - in production, integrate with email service
            email_data = {
                "to": config.get("to", ""),
                "subject": config.get("subject", ""),
                "body": config.get("body", ""),
                "template": config.get("template"),
                "variables": config.get("variables", {})
            }
            
            # Replace variables in email content
            if email_data["template"]:
                # In production, use template engine
                email_data["body"] = f"Template: {email_data['template']}"
            
            logger.info(f"Sending email to {email_data['to']}: {email_data['subject']}")
            
            return {
                "email_sent": True,
                "email_id": str(uuid.uuid4()),
                "recipient": email_data["to"],
                "subject": email_data["subject"]
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    async def _handle_create_campaign(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create campaign action"""
        try:
            # Mock campaign creation - in production, integrate with platform APIs
            campaign_data = {
                "name": config.get("name", ""),
                "platform": config.get("platform", "google_ads"),
                "budget": config.get("budget", 1000),
                "targeting": config.get("targeting", {}),
                "creative": config.get("creative", {})
            }
            
            logger.info(f"Creating campaign: {campaign_data['name']}")
            
            return {
                "campaign_created": True,
                "campaign_id": str(uuid.uuid4()),
                "campaign_name": campaign_data["name"],
                "platform": campaign_data["platform"],
                "budget": campaign_data["budget"]
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise
    
    async def _handle_update_budget(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update budget action"""
        try:
            campaign_id = config.get("campaign_id")
            new_budget = config.get("budget")
            operation = config.get("operation", "set")  # set, increase, decrease
            
            if not campaign_id or not new_budget:
                raise ValueError("Campaign ID and budget are required")
            
            # Mock budget update - in production, integrate with platform APIs
            logger.info(f"Updating budget for campaign {campaign_id}: {operation} to {new_budget}")
            
            return {
                "budget_updated": True,
                "campaign_id": campaign_id,
                "new_budget": new_budget,
                "operation": operation
            }
            
        except Exception as e:
            logger.error(f"Error updating budget: {e}")
            raise
    
    async def _handle_pause_campaign(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause campaign action"""
        try:
            campaign_id = config.get("campaign_id")
            
            if not campaign_id:
                raise ValueError("Campaign ID is required")
            
            # Mock campaign pause - in production, integrate with platform APIs
            logger.info(f"Pausing campaign {campaign_id}")
            
            return {
                "campaign_paused": True,
                "campaign_id": campaign_id,
                "paused_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            raise
    
    async def _handle_resume_campaign(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resume campaign action"""
        try:
            campaign_id = config.get("campaign_id")
            
            if not campaign_id:
                raise ValueError("Campaign ID is required")
            
            # Mock campaign resume - in production, integrate with platform APIs
            logger.info(f"Resuming campaign {campaign_id}")
            
            return {
                "campaign_resumed": True,
                "campaign_id": campaign_id,
                "resumed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            raise
    
    async def _handle_send_notification(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send notification action"""
        try:
            notification_data = {
                "type": config.get("type", "info"),
                "title": config.get("title", ""),
                "message": config.get("message", ""),
                "recipients": config.get("recipients", []),
                "channels": config.get("channels", ["email"])
            }
            
            # Mock notification sending - in production, integrate with notification service
            logger.info(f"Sending notification: {notification_data['title']}")
            
            return {
                "notification_sent": True,
                "notification_id": str(uuid.uuid4()),
                "type": notification_data["type"],
                "title": notification_data["title"],
                "recipients": notification_data["recipients"]
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
    
    async def _handle_update_targeting(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update targeting action"""
        try:
            campaign_id = config.get("campaign_id")
            targeting_updates = config.get("targeting", {})
            
            if not campaign_id:
                raise ValueError("Campaign ID is required")
            
            # Mock targeting update - in production, integrate with platform APIs
            logger.info(f"Updating targeting for campaign {campaign_id}")
            
            return {
                "targeting_updated": True,
                "campaign_id": campaign_id,
                "updates": targeting_updates,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating targeting: {e}")
            raise
    
    async def _handle_generate_report(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate report action"""
        try:
            report_config = {
                "report_type": config.get("report_type", "performance"),
                "date_range": config.get("date_range", "last_30_days"),
                "campaigns": config.get("campaigns", []),
                "metrics": config.get("metrics", []),
                "format": config.get("format", "pdf")
            }
            
            # Mock report generation - in production, integrate with reporting service
            logger.info(f"Generating {report_config['report_type']} report")
            
            return {
                "report_generated": True,
                "report_id": str(uuid.uuid4()),
                "report_type": report_config["report_type"],
                "format": report_config["format"],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _handle_call_api(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call API action"""
        try:
            api_config = {
                "url": config.get("url"),
                "method": config.get("method", "GET"),
                "headers": config.get("headers", {}),
                "data": config.get("data", {}),
                "timeout": config.get("timeout", 30)
            }
            
            if not api_config["url"]:
                raise ValueError("API URL is required")
            
            # Mock API call - in production, make actual HTTP request
            logger.info(f"Calling API: {api_config['method']} {api_config['url']}")
            
            return {
                "api_called": True,
                "url": api_config["url"],
                "method": api_config["method"],
                "status_code": 200,
                "response": {"message": "API call successful"}
            }
            
        except Exception as e:
            logger.error(f"Error calling API: {e}")
            raise
    
    async def _handle_wait(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle wait action"""
        try:
            wait_time = config.get("duration", 60)  # seconds
            
            logger.info(f"Waiting for {wait_time} seconds")
            await asyncio.sleep(wait_time)
            
            return {
                "waited": True,
                "duration": wait_time,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in wait action: {e}")
            raise
    
    async def _handle_condition(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle condition action"""
        try:
            conditions = config.get("conditions", [])
            true_branch = config.get("true_branch", [])
            false_branch = config.get("false_branch", [])
            
            # Evaluate conditions
            condition_result = await self._evaluate_conditions(conditions, context)
            
            # Execute appropriate branch
            branch_to_execute = true_branch if condition_result else false_branch
            
            results = []
            for step_config in branch_to_execute:
                # Recursively execute steps in branch
                result = await self._execute_branch_step(step_config, context)
                results.append(result)
            
            return {
                "condition_evaluated": True,
                "result": condition_result,
                "branch_executed": "true" if condition_result else "false",
                "branch_results": results
            }
            
        except Exception as e:
            logger.error(f"Error in condition action: {e}")
            raise
    
    async def _handle_loop(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle loop action"""
        try:
            loop_config = config.get("loop", {})
            max_iterations = loop_config.get("max_iterations", 10)
            condition = loop_config.get("condition")
            steps = loop_config.get("steps", [])
            
            results = []
            iteration = 0
            
            while iteration < max_iterations:
                # Check loop condition
                if condition:
                    condition_result = await self._evaluate_conditions([condition], context)
                    if not condition_result:
                        break
                
                # Execute loop steps
                iteration_results = []
                for step_config in steps:
                    result = await self._execute_branch_step(step_config, context)
                    iteration_results.append(result)
                
                results.append({
                    "iteration": iteration + 1,
                    "results": iteration_results
                })
                
                iteration += 1
            
            return {
                "loop_completed": True,
                "iterations": iteration,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in loop action: {e}")
            raise
    
    async def _handle_parallel(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parallel execution action"""
        try:
            steps = config.get("steps", [])
            
            # Execute steps in parallel
            tasks = []
            for step_config in steps:
                task = asyncio.create_task(self._execute_branch_step(step_config, context))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "parallel_completed": True,
                "steps_executed": len(steps),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in parallel action: {e}")
            raise
    
    async def _execute_branch_step(self, step_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a step in a branch (condition/loop/parallel)"""
        try:
            action_type = ActionType(step_config.get("action_type"))
            config = step_config.get("config", {})
            
            handler = self.action_handlers.get(action_type)
            if not handler:
                raise ValueError(f"No handler for action type {action_type}")
            
            return await handler(config, context)
            
        except Exception as e:
            logger.error(f"Error executing branch step: {e}")
            raise
    
    async def _validate_workflow(self, workflow_data: Dict[str, Any]):
        """Validate workflow structure"""
        try:
            required_fields = ["name", "steps"]
            for field in required_fields:
                if field not in workflow_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate steps
            steps = workflow_data.get("steps", [])
            if not steps:
                raise ValueError("Workflow must have at least one step")
            
            step_ids = set()
            for step in steps:
                if "step_id" not in step:
                    raise ValueError("Step must have step_id")
                
                if step["step_id"] in step_ids:
                    raise ValueError(f"Duplicate step_id: {step['step_id']}")
                
                step_ids.add(step["step_id"])
            
            # Validate dependencies
            for step in steps:
                depends_on = step.get("depends_on", [])
                for dep in depends_on:
                    if dep not in step_ids:
                        raise ValueError(f"Step {step['step_id']} depends on non-existent step {dep}")
            
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            raise
    
    async def _save_execution(self, execution: WorkflowExecution):
        """Save workflow execution to database"""
        try:
            execution_doc = {
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "current_step": execution.current_step,
                "context": execution.context,
                "error_message": execution.error_message,
                "retry_count": execution.retry_count,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.db.workflow_executions.replace_one(
                {"execution_id": execution.execution_id},
                execution_doc,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving execution: {e}")
            raise
    
    async def _save_step_execution(self, step_execution: StepExecution):
        """Save step execution to database"""
        try:
            step_execution_doc = {
                "step_execution_id": step_execution.step_execution_id,
                "workflow_execution_id": step_execution.workflow_execution_id,
                "step_id": step_execution.step_id,
                "status": step_execution.status.value,
                "started_at": step_execution.started_at.isoformat(),
                "completed_at": step_execution.completed_at.isoformat() if step_execution.completed_at else None,
                "input_data": step_execution.input_data,
                "output_data": step_execution.output_data,
                "error_message": step_execution.error_message,
                "retry_count": step_execution.retry_count,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.db.step_executions.replace_one(
                {"step_execution_id": step_execution.step_execution_id},
                step_execution_doc,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving step execution: {e}")
            raise

class WorkflowTriggerManager:
    """Manages workflow triggers and scheduling"""
    
    def __init__(self, db=None, redis_client: redis.Redis=None, celery_app=None):
        # Phase 1/3 deprecated - MongoDB and Celery archived for MVP
        self.db = None  # Phase 1: MongoDB archived
        self.redis = redis_client
        self.celery = None  # Phase 3: Celery archived
        self.active_triggers = {}
    
    async def create_trigger(self, trigger_data: Dict[str, Any]) -> str:
        """Create a new workflow trigger"""
        try:
            trigger_id = str(uuid.uuid4())
            
            trigger = WorkflowTrigger(
                trigger_id=trigger_id,
                trigger_type=TriggerType(trigger_data["trigger_type"]),
                name=trigger_data["name"],
                description=trigger_data.get("description", ""),
                config=trigger_data.get("config", {}),
                enabled=trigger_data.get("enabled", True),
                created_at=datetime.utcnow()
            )
            
            # Save trigger to database
            trigger_doc = {
                "trigger_id": trigger_id,
                "workflow_id": trigger_data["workflow_id"],
                "trigger_type": trigger.trigger_type.value,
                "name": trigger.name,
                "description": trigger.description,
                "config": trigger.config,
                "enabled": trigger.enabled,
                "created_at": trigger.created_at.isoformat()
            }
            
            await self.db.workflow_triggers.insert_one(trigger_doc)
            
            # Activate trigger if enabled
            if trigger.enabled:
                await self._activate_trigger(trigger)
            
            logger.info(f"Created trigger {trigger_id}: {trigger.name}")
            return trigger_id
            
        except Exception as e:
            logger.error(f"Error creating trigger: {e}")
            raise
    
    async def _activate_trigger(self, trigger: WorkflowTrigger):
        """Activate a workflow trigger"""
        try:
            if trigger.trigger_type == TriggerType.SCHEDULED:
                await self._activate_scheduled_trigger(trigger)
            elif trigger.trigger_type == TriggerType.EVENT_BASED:
                await self._activate_event_trigger(trigger)
            elif trigger.trigger_type == TriggerType.WEBHOOK:
                await self._activate_webhook_trigger(trigger)
            
            self.active_triggers[trigger.trigger_id] = trigger
            
        except Exception as e:
            logger.error(f"Error activating trigger {trigger.trigger_id}: {e}")
            raise
    
    async def _activate_scheduled_trigger(self, trigger: WorkflowTrigger):
        """Activate scheduled trigger"""
        try:
            schedule_config = trigger.config
            cron_expression = schedule_config.get("cron")
            interval = schedule_config.get("interval")  # seconds
            
            if cron_expression:
                # Schedule with Celery Beat
                # Phase 3 deprecated - Celery archived (MVP uses Vercel Cron)
                # self.celery.conf.beat_schedule[f"trigger_{trigger.trigger_id}"] = {
                logger.warning("Celery deprecated - trigger not scheduled (MVP uses Vercel Cron)")
                # self.celery.conf.beat_schedule[f"trigger_{trigger.trigger_id}"] = {
                    "task": "workflow_engine.execute_scheduled_workflow",
                    "schedule": cron_expression,
                    "args": (trigger.trigger_id,)
                }
            elif interval:
                # Schedule with interval
                # Phase 3 deprecated - Celery archived (MVP uses Vercel Cron)
                # self.celery.conf.beat_schedule[f"trigger_{trigger.trigger_id}"] = {
                logger.warning("Celery deprecated - trigger not scheduled (MVP uses Vercel Cron)")
                # self.celery.conf.beat_schedule[f"trigger_{trigger.trigger_id}"] = {
                    "task": "workflow_engine.execute_scheduled_workflow",
                    "schedule": interval,
                    "args": (trigger.trigger_id,)
                }
            
        except Exception as e:
            logger.error(f"Error activating scheduled trigger: {e}")
            raise
    
    async def _activate_event_trigger(self, trigger: WorkflowTrigger):
        """Activate event-based trigger"""
        try:
            event_config = trigger.config
            event_type = event_config.get("event_type")
            
            # Subscribe to Redis events
            if event_type:
                await self.redis.subscribe(f"workflow_events:{event_type}")
                
                # Start event listener task
                asyncio.create_task(self._listen_for_events(trigger))
            
        except Exception as e:
            logger.error(f"Error activating event trigger: {e}")
            raise
    
    async def _activate_webhook_trigger(self, trigger: WorkflowTrigger):
        """Activate webhook trigger"""
        try:
            webhook_config = trigger.config
            webhook_url = webhook_config.get("webhook_url")
            secret = webhook_config.get("secret")
            
            # Store webhook configuration for API endpoint
            await self.redis.hset(
                f"webhook_triggers:{trigger.trigger_id}",
                mapping={
                    "url": webhook_url,
                    "secret": secret or "",
                    "workflow_id": trigger.config.get("workflow_id")
                }
            )
            
        except Exception as e:
            logger.error(f"Error activating webhook trigger: {e}")
            raise
    
    async def _listen_for_events(self, trigger: WorkflowTrigger):
        """Listen for events and trigger workflows"""
        try:
            event_config = trigger.config
            event_type = event_config.get("event_type")
            
            while True:
                message = await self.redis.blpop(f"workflow_events:{event_type}", timeout=1)
                if message:
                    event_data = json.loads(message[1])
                    await self._trigger_workflow(trigger, event_data)
                
        except Exception as e:
            logger.error(f"Error listening for events: {e}")
    
    async def _trigger_workflow(self, trigger: WorkflowTrigger, event_data: Dict[str, Any]):
        """Trigger workflow execution"""
        try:
            workflow_id = trigger.config.get("workflow_id")
            if not workflow_id:
                return
            
            # Execute workflow with event data
            workflow_engine = WorkflowEngine(self.db, self.redis, self.celery)
            await workflow_engine.execute_workflow(workflow_id, event_data)
            
        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
    
    async def deactivate_trigger(self, trigger_id: str):
        """Deactivate a workflow trigger"""
        try:
            if trigger_id in self.active_triggers:
                trigger = self.active_triggers[trigger_id]
                
                if trigger.trigger_type == TriggerType.SCHEDULED:
                    # Remove from Celery Beat schedule
                    if f"trigger_{trigger_id}" in self.celery.conf.beat_schedule:
                        del self.celery.conf.beat_schedule[f"trigger_{trigger_id}"]
                
                del self.active_triggers[trigger_id]
            
            # Update database
            await self.db.workflow_triggers.update_one(
                {"trigger_id": trigger_id},
                {"$set": {"enabled": False}}
            )
            
        except Exception as e:
            logger.error(f"Error deactivating trigger {trigger_id}: {e}")
            raise

class AdvancedAutomationService:
    """Main service for advanced automation workflows"""
    
    def __init__(self, db=None, redis_client: redis.Redis=None, celery_app=None):
        # Phase 1/3 deprecated - MongoDB and Celery archived for MVP
        self.db = None  # Phase 1: MongoDB archived
        self.redis = redis_client
        self.celery = None  # Phase 3: Celery archived
        self.workflow_engine = WorkflowEngine(db, redis_client, celery_app)
        self.trigger_manager = WorkflowTriggerManager(db, redis_client, celery_app)
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow"""
        return await self.workflow_engine.create_workflow(workflow_data)
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Optional[Dict[str, Any]] = None) -> str:
        """Execute a workflow"""
        return await self.workflow_engine.execute_workflow(workflow_id, trigger_data)
    
    async def create_trigger(self, trigger_data: Dict[str, Any]) -> str:
        """Create a workflow trigger"""
        return await self.trigger_manager.create_trigger(trigger_data)
    
    async def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workflow executions"""
        try:
            executions = await self.db.workflow_executions.find(
                {"workflow_id": workflow_id}
            ).sort("started_at", -1).limit(limit).to_list(length=None)
            
            return executions
            
        except Exception as e:
            logger.error(f"Error getting workflow executions: {e}")
            raise
    
    async def get_execution_details(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed execution information"""
        try:
            # Get execution
            execution = await self.db.workflow_executions.find_one({"execution_id": execution_id})
            if not execution:
                raise ValueError(f"Execution {execution_id} not found")
            
            # Get step executions
            step_executions = await self.db.step_executions.find(
                {"workflow_execution_id": execution_id}
            ).sort("started_at", 1).to_list(length=None)
            
            return {
                "execution": execution,
                "step_executions": step_executions
            }
            
        except Exception as e:
            logger.error(f"Error getting execution details: {e}")
            raise
    
    async def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get predefined workflow templates"""
        try:
            templates = [
                {
                    "template_id": "campaign_optimization",
                    "name": "Campaign Optimization Workflow",
                    "description": "Automatically optimize campaigns based on performance metrics",
                    "steps": [
                        {
                            "step_id": "check_performance",
                            "name": "Check Performance",
                            "action_type": "call_api",
                            "config": {"url": "/api/campaigns/metrics"}
                        },
                        {
                            "step_id": "evaluate_performance",
                            "name": "Evaluate Performance",
                            "action_type": "condition",
                            "config": {
                                "conditions": [{"field": "roas", "operator": "less_than", "value": 2.0}],
                                "true_branch": [
                                    {
                                        "action_type": "pause_campaign",
                                        "config": {"campaign_id": "{{campaign_id}}"}
                                    }
                                ],
                                "false_branch": [
                                    {
                                        "action_type": "increase_budget",
                                        "config": {"campaign_id": "{{campaign_id}}", "budget": 1000}
                                    }
                                ]
                            }
                        }
                    ]
                },
                {
                    "template_id": "lead_nurturing",
                    "name": "Lead Nurturing Workflow",
                    "description": "Automated lead nurturing sequence",
                    "steps": [
                        {
                            "step_id": "send_welcome_email",
                            "name": "Send Welcome Email",
                            "action_type": "send_email",
                            "config": {"template": "welcome", "to": "{{lead_email}}"}
                        },
                        {
                            "step_id": "wait_3_days",
                            "name": "Wait 3 Days",
                            "action_type": "wait",
                            "config": {"duration": 259200}  # 3 days in seconds
                        },
                        {
                            "step_id": "send_follow_up",
                            "name": "Send Follow-up",
                            "action_type": "send_email",
                            "config": {"template": "follow_up", "to": "{{lead_email}}"}
                        }
                    ]
                },
                {
                    "template_id": "report_generation",
                    "name": "Automated Report Generation",
                    "description": "Generate and send reports on schedule",
                    "steps": [
                        {
                            "step_id": "generate_report",
                            "name": "Generate Report",
                            "action_type": "generate_report",
                            "config": {"report_type": "performance", "format": "pdf"}
                        },
                        {
                            "step_id": "send_report",
                            "name": "Send Report",
                            "action_type": "send_email",
                            "config": {"template": "report", "attachment": "{{report_id}}"}
                        }
                    ]
                }
            ]
            
            return templates
            
        except Exception as e:
            logger.error(f"Error getting workflow templates: {e}")
            raise

# Global instance
advanced_automation_service = None

def get_advanced_automation_service(db=None, redis_client: redis.Redis=None, celery_app=None) -> AdvancedAutomationService:
    # Phase 1/3 deprecated - MongoDB and Celery archived for MVP
    """Get advanced automation service instance"""
    global advanced_automation_service
    if advanced_automation_service is None:
        advanced_automation_service = AdvancedAutomationService(db, redis_client, celery_app)
    return advanced_automation_service
