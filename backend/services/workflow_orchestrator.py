"""
Advanced Workflow Orchestration System for OmnifyProduct
Handles complex multi-step workflows with dependencies, error handling, and parallel execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.agentkit_service import AgentKitService
from services.validation_service import ValidationService, ValidationError
from models.agentkit_models import (
    WorkflowDefinition, WorkflowExecution, AgentExecutionRequest,
    AgentStatus, WorkflowStatus
)

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Workflow execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class StepStatus(Enum):
    """Individual step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStepExecution:
    """Individual step execution tracking"""
    step_id: str
    agent_type: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    depends_on: List[str] = field(default_factory=list)


@dataclass
class WorkflowContext:
    """Workflow execution context"""
    workflow_id: str
    execution_id: str
    organization_id: str
    user_id: str
    start_time: datetime
    max_execution_time: int = 300  # 5 minutes default
    current_data: Dict[str, Any] = field(default_factory=dict)
    step_executions: Dict[str, WorkflowStepExecution] = field(default_factory=dict)
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)


class WorkflowOrchestrator:
    """
    Advanced workflow orchestration system
    Handles complex workflows with proper dependency management, error handling, and parallel execution
    """

    def __init__(self, agentkit_service: AgentKitService):
        self.agentkit_service = agentkit_service
        self.active_workflows: Dict[str, WorkflowContext] = {}

    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        input_data: Dict[str, Any],
        user_id: str,
        organization_id: str,
        execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    ) -> WorkflowExecution:
        """
        Execute a workflow with advanced orchestration

        Args:
            workflow: Workflow definition
            input_data: Initial input data
            user_id: User executing the workflow
            organization_id: Organization context
            execution_mode: Execution strategy

        Returns:
            WorkflowExecution result
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow.workflow_id,
            execution_id=execution_id,
            organization_id=organization_id,
            user_id=user_id,
            start_time=start_time,
            current_data=input_data.copy()
        )

        # Initialize step executions
        for step in workflow.steps:
            step_exec = WorkflowStepExecution(
                step_id=step.step_id,
                agent_type=step.agent_type,
                depends_on=step.depends_on or [],
                max_retries=step.max_retries if hasattr(step, 'max_retries') else 3
            )
            context.step_executions[step.step_id] = step_exec

        # Track active workflow
        self.active_workflows[execution_id] = context

        try:
            # Execute based on mode
            if execution_mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(context, workflow)
            elif execution_mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(context, workflow)
            elif execution_mode == ExecutionMode.CONDITIONAL:
                await self._execute_conditional(context, workflow)
            else:
                raise ValidationError(f"Unsupported execution mode: {execution_mode}")

            # Determine final status
            if context.failed_steps:
                final_status = WorkflowStatus.FAILED
            elif len(context.completed_steps) == len(workflow.steps):
                final_status = WorkflowStatus.COMPLETED
            else:
                final_status = WorkflowStatus.PARTIALLY_COMPLETED

            # Calculate total duration
            end_time = datetime.utcnow()
            total_duration = (end_time - start_time).total_seconds()

            # Create execution result
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow.workflow_id,
                organization_id=organization_id,
                user_id=user_id,
                status=final_status,
                input_data=input_data,
                output_data=context.current_data,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=total_duration,
                completed_steps=list(context.completed_steps),
                failed_steps=list(context.failed_steps)
            )

            return execution

        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} execution failed: {str(e)}")

            # Update context with failure
            end_time = datetime.utcnow()
            context.current_data["error"] = str(e)

            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow.workflow_id,
                organization_id=organization_id,
                user_id=user_id,
                status=WorkflowStatus.FAILED,
                input_data=input_data,
                output_data=context.current_data,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                completed_steps=list(context.completed_steps),
                failed_steps=list(context.failed_steps),
                error=str(e)
            )

            return execution

        finally:
            # Clean up active workflow tracking
            self.active_workflows.pop(execution_id, None)

    async def _execute_sequential(self, context: WorkflowContext, workflow: WorkflowDefinition):
        """Execute workflow steps sequentially"""
        for step in workflow.steps:
            if context.execution_id not in self.active_workflows:
                break  # Workflow was cancelled

            step_exec = context.step_executions[step.step_id]

            # Check if dependencies are satisfied
            if not await self._check_dependencies_satisfied(step_exec, context):
                step_exec.status = StepStatus.SKIPPED
                continue

            # Execute the step
            await self._execute_workflow_step(step_exec, step, context)

            if step_exec.status == StepStatus.FAILED:
                context.failed_steps.add(step.step_id)
                break  # Stop on first failure in sequential mode

    async def _execute_parallel(self, context: WorkflowContext, workflow: WorkflowDefinition):
        """Execute workflow steps in parallel where possible"""
        # Group steps by dependency level
        dependency_levels = await self._build_dependency_levels(workflow.steps)

        for level in dependency_levels:
            if context.execution_id not in self.active_workflows:
                break  # Workflow was cancelled

            # Execute all steps in this level in parallel
            parallel_tasks = []
            for step in level:
                step_exec = context.step_executions[step.step_id]

                if await self._check_dependencies_satisfied(step_exec, context):
                    task = self._execute_workflow_step_async(step_exec, step, context)
                    parallel_tasks.append(task)

            if parallel_tasks:
                # Wait for all steps in this level to complete
                await asyncio.gather(*parallel_tasks, return_exceptions=True)

                # Check for failures
                for step in level:
                    step_exec = context.step_executions[step.step_id]
                    if step_exec.status == StepStatus.FAILED:
                        context.failed_steps.add(step.step_id)
                        # In parallel mode, continue with other steps

    async def _execute_conditional(self, context: WorkflowContext, workflow: WorkflowDefinition):
        """Execute workflow with conditional logic based on step results"""
        # Start with sequential execution but allow branching
        await self._execute_sequential(context, workflow)

        # Additional conditional logic can be implemented here
        # For example, branching based on step outputs

    async def _execute_workflow_step(
        self,
        step_exec: WorkflowStepExecution,
        step: Any,
        context: WorkflowContext
    ):
        """Execute a single workflow step with retry logic"""
        step_exec.status = StepStatus.RUNNING
        step_exec.started_at = datetime.utcnow()

        max_retries = step_exec.max_retries

        for attempt in range(max_retries + 1):
            try:
                # Prepare step input data
                step_input = self._prepare_step_input(step_exec, step, context)

                # Create agent execution request
                agent_request = AgentExecutionRequest(
                    agent_id=f"{context.organization_id}_{step_exec.agent_type}",
                    input_data=step_input,
                    user_id=context.user_id,
                    organization_id=context.organization_id,
                    context={"workflow_id": context.workflow_id, "step_id": step_exec.step_id}
                )

                # Execute the agent
                agent_response = await self.agentkit_service.execute_agent(agent_request)

                if agent_response.status == AgentStatus.COMPLETED:
                    # Success - update step execution
                    step_exec.status = StepStatus.COMPLETED
                    step_exec.output_data = agent_response.output_data or {}
                    step_exec.completed_at = datetime.utcnow()
                    step_exec.duration_seconds = agent_response.duration_seconds

                    # Update workflow context data
                    self._update_workflow_context_data(step_exec, step, context)

                    context.completed_steps.add(step_exec.step_id)
                    break

                else:
                    # Agent execution failed
                    step_exec.error = agent_response.error or "Agent execution failed"
                    step_exec.retry_count += 1

                    if attempt < max_retries:
                        logger.warning(f"Step {step_exec.step_id} failed, retrying ({attempt + 1}/{max_retries})")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        step_exec.status = StepStatus.FAILED
                        logger.error(f"Step {step_exec.step_id} failed after {max_retries} retries")

            except Exception as e:
                step_exec.error = str(e)
                step_exec.retry_count += 1

                if attempt < max_retries:
                    logger.warning(f"Step {step_exec.step_id} error, retrying ({attempt + 1}/{max_retries}): {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    step_exec.status = StepStatus.FAILED
                    logger.error(f"Step {step_exec.step_id} failed after {max_retries} retries: {str(e)}")

        if step_exec.status != StepStatus.COMPLETED:
            step_exec.status = StepStatus.FAILED

    async def _execute_workflow_step_async(
        self,
        step_exec: WorkflowStepExecution,
        step: Any,
        context: WorkflowContext
    ):
        """Execute a workflow step asynchronously (for parallel execution)"""
        try:
            await self._execute_workflow_step(step_exec, step, context)
        except Exception as e:
            logger.error(f"Async step execution failed for {step_exec.step_id}: {str(e)}")
            step_exec.status = StepStatus.FAILED
            step_exec.error = str(e)

    async def _check_dependencies_satisfied(
        self,
        step_exec: WorkflowStepExecution,
        context: WorkflowContext
    ) -> bool:
        """Check if all dependencies for a step are satisfied"""
        for dep_step_id in step_exec.depends_on:
            if dep_step_id not in context.completed_steps:
                return False
            # Also check that dependency didn't fail
            if dep_step_id in context.failed_steps:
                return False
        return True

    def _prepare_step_input(
        self,
        step_exec: WorkflowStepExecution,
        step: Any,
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """Prepare input data for a workflow step"""
        step_input = {}

        # Map input data based on step configuration
        if hasattr(step, 'input_mapping') and step.input_mapping:
            for input_key, source_key in step.input_mapping.items():
                if source_key in context.current_data:
                    step_input[input_key] = context.current_data[source_key]
                elif source_key.startswith('workflow.'):
                    # Handle workflow-level data
                    workflow_key = source_key.replace('workflow.', '')
                    if workflow_key in context.current_data:
                        step_input[input_key] = context.current_data[workflow_key]

        # Add workflow context
        step_input['_workflow_context'] = {
            'workflow_id': context.workflow_id,
            'execution_id': context.execution_id,
            'step_id': step_exec.step_id,
            'organization_id': context.organization_id,
            'user_id': context.user_id
        }

        return step_input

    def _update_workflow_context_data(
        self,
        step_exec: WorkflowStepExecution,
        step: Any,
        context: WorkflowContext
    ):
        """Update workflow context data with step output"""
        if hasattr(step, 'output_mapping') and step.output_mapping:
            for source_key, target_key in step.output_mapping.items():
                if source_key in step_exec.output_data:
                    context.current_data[target_key] = step_exec.output_data[source_key]

    async def _build_dependency_levels(self, steps: List[Any]) -> List[List[Any]]:
        """Build dependency levels for parallel execution"""
        # Simple topological sort for dependency ordering
        step_map = {step.step_id: step for step in steps}
        in_degree = {step.step_id: 0 for step in steps}
        levels = []

        # Calculate in-degrees
        for step in steps:
            if hasattr(step, 'depends_on') and step.depends_on:
                for dep in step.depends_on:
                    if dep in in_degree:
                        in_degree[step.step_id] += 1

        # Build levels
        while step_map:
            # Find steps with no dependencies
            current_level = [
                step for step_id, step in step_map.items()
                if in_degree[step_id] == 0
            ]

            if not current_level:
                # Handle circular dependencies or missing dependencies
                logger.warning("Circular dependency or missing dependency detected in workflow")
                break

            levels.append(current_level)

            # Remove current level from step_map and update in_degrees
            for step in current_level:
                step_id = step.step_id
                del step_map[step_id]

                # Update in-degrees for dependent steps
                for other_step in steps:
                    if (hasattr(other_step, 'depends_on') and
                        other_step.step_id in step_map and
                        step_id in (other_step.depends_on or [])):
                        in_degree[other_step.step_id] -= 1

        return levels

    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        if execution_id in self.active_workflows:
            del self.active_workflows[execution_id]
            logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
        return False

    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a running workflow"""
        context = self.active_workflows.get(execution_id)
        if not context:
            return None

        return {
            'execution_id': execution_id,
            'workflow_id': context.workflow_id,
            'status': 'running',
            'start_time': context.start_time.isoformat(),
            'completed_steps': len(context.completed_steps),
            'failed_steps': len(context.failed_steps),
            'total_steps': len(context.step_executions),
            'progress_percentage': (len(context.completed_steps) / len(context.step_executions)) * 100
        }


class WorkflowScheduler:
    """Workflow scheduling and management system"""

    def __init__(self, orchestrator: WorkflowOrchestrator, db: AsyncIOMotorDatabase):
        self.orchestrator = orchestrator
        self.db = db
        self.scheduled_workflows: Dict[str, Dict[str, Any]] = {}

    async def schedule_workflow(
        self,
        workflow_id: str,
        schedule_time: datetime,
        input_data: Dict[str, Any],
        user_id: str,
        organization_id: str,
        recurring: bool = False,
        recurrence_pattern: Optional[str] = None
    ) -> str:
        """Schedule a workflow for future execution"""
        schedule_id = str(uuid.uuid4())

        schedule_data = {
            'schedule_id': schedule_id,
            'workflow_id': workflow_id,
            'schedule_time': schedule_time,
            'input_data': input_data,
            'user_id': user_id,
            'organization_id': organization_id,
            'recurring': recurring,
            'recurrence_pattern': recurrence_pattern,
            'status': 'scheduled',
            'created_at': datetime.utcnow()
        }

        self.scheduled_workflows[schedule_id] = schedule_data

        # Store in database
        await self.db.scheduled_workflows.insert_one(schedule_data)

        logger.info(f"Scheduled workflow {workflow_id} for execution at {schedule_time}")
        return schedule_id

    async def process_scheduled_workflows(self):
        """Process and execute scheduled workflows"""
        now = datetime.utcnow()

        # Find workflows ready for execution
        ready_workflows = [
            schedule for schedule in self.scheduled_workflows.values()
            if schedule['schedule_time'] <= now and schedule['status'] == 'scheduled'
        ]

        for schedule in ready_workflows:
            try:
                # Get workflow definition
                workflow_data = await self.db.agentkit_workflows.find_one({
                    'workflow_id': schedule['workflow_id']
                })

                if not workflow_data:
                    logger.error(f"Scheduled workflow {schedule['workflow_id']} not found")
                    continue

                workflow = WorkflowDefinition(**workflow_data)

                # Execute workflow
                await self.orchestrator.execute_workflow(
                    workflow=workflow,
                    input_data=schedule['input_data'],
                    user_id=schedule['user_id'],
                    organization_id=schedule['organization_id']
                )

                # Update schedule status
                schedule['status'] = 'completed'
                schedule['executed_at'] = datetime.utcnow()

                # Handle recurring workflows
                if schedule['recurring'] and schedule['recurrence_pattern']:
                    await self._schedule_next_recurrence(schedule)

            except Exception as e:
                logger.error(f"Failed to execute scheduled workflow {schedule['workflow_id']}: {str(e)}")
                schedule['status'] = 'failed'
                schedule['error'] = str(e)

    async def _schedule_next_recurrence(self, schedule: Dict[str, Any]):
        """Schedule next recurrence for recurring workflows"""
        # Simple implementation - can be extended with cron-like patterns
        if schedule['recurrence_pattern'] == 'daily':
            next_time = schedule['schedule_time'] + timedelta(days=1)
        elif schedule['recurrence_pattern'] == 'weekly':
            next_time = schedule['schedule_time'] + timedelta(weeks=1)
        elif schedule['recurrence_pattern'] == 'monthly':
            next_time = schedule['schedule_time'] + timedelta(days=30)
        else:
            return  # Unknown pattern

        await self.schedule_workflow(
            workflow_id=schedule['workflow_id'],
            schedule_time=next_time,
            input_data=schedule['input_data'],
            user_id=schedule['user_id'],
            organization_id=schedule['organization_id'],
            recurring=True,
            recurrence_pattern=schedule['recurrence_pattern']
        )
