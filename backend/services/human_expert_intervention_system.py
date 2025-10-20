"""
Human Expert Intervention Workflows
Creates human expert intervention system for critical decisions and hand-holding
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class InterventionType(Enum):
    """Types of human expert interventions"""
    APPROVAL_REQUIRED = "approval_required"  # AI needs human approval
    EXPERT_CONSULTATION = "expert_consultation"  # Expert consultation needed
    CRITICAL_DECISION = "critical_decision"  # Critical decision requiring expert input
    ESCALATION = "escalation"  # Escalation to senior expert
    EMERGENCY = "emergency"  # Emergency intervention
    TRAINING = "training"  # Training/guidance session
    REVIEW = "review"  # Expert review of AI decisions

class InterventionStatus(Enum):
    """Status of intervention requests"""
    PENDING = "pending"  # Awaiting expert response
    IN_PROGRESS = "in_progress"  # Expert is handling
    APPROVED = "approved"  # Expert approved
    REJECTED = "rejected"  # Expert rejected
    ESCALATED = "escalated"  # Escalated to higher level
    COMPLETED = "completed"  # Intervention completed
    EXPIRED = "expired"  # Request expired

class ExpertLevel(Enum):
    """Expert levels for intervention"""
    JUNIOR = "junior"  # Junior expert
    SENIOR = "senior"  # Senior expert
    LEAD = "lead"  # Lead expert
    PRINCIPAL = "principal"  # Principal expert
    DIRECTOR = "director"  # Director level

class DecisionComplexity(Enum):
    """Complexity levels for decisions"""
    LOW = "low"  # Simple decision
    MEDIUM = "medium"  # Moderate complexity
    HIGH = "high"  # High complexity
    CRITICAL = "critical"  # Critical decision
    EMERGENCY = "emergency"  # Emergency situation

@dataclass
class ExpertProfile:
    """Profile of human expert"""
    expert_id: str
    name: str
    email: str
    level: ExpertLevel
    specialties: List[str]  # Areas of expertise
    availability: Dict[str, Any]  # Availability schedule
    current_load: int  # Current number of active interventions
    max_load: int  # Maximum interventions they can handle
    success_rate: float  # Success rate of their interventions
    response_time_avg: float  # Average response time in minutes
    is_available: bool  # Currently available for new interventions

@dataclass
class InterventionRequest:
    """Request for human expert intervention"""
    request_id: str
    client_id: str
    intervention_type: InterventionType
    status: InterventionStatus
    priority: int  # 1-10, higher is more urgent
    complexity: DecisionComplexity
    title: str
    description: str
    context: Dict[str, Any]  # Context data
    ai_recommendation: Optional[str]  # AI's recommendation
    ai_confidence: float  # AI's confidence level
    required_expert_level: ExpertLevel  # Minimum expert level required
    assigned_expert: Optional[str]  # Assigned expert ID
    created_at: datetime
    updated_at: datetime
    deadline: Optional[datetime]  # Deadline for response
    escalation_history: List[Dict[str, Any]]  # History of escalations
    attachments: List[str]  # File attachments
    tags: List[str]  # Tags for categorization

@dataclass
class ExpertDecision:
    """Decision made by human expert"""
    decision_id: str
    request_id: str
    expert_id: str
    decision: str  # The decision made
    reasoning: str  # Reasoning behind decision
    confidence: float  # Expert's confidence in decision
    alternatives_considered: List[str]  # Alternatives that were considered
    risk_assessment: str  # Risk assessment
    follow_up_actions: List[str]  # Actions to take
    learning_points: List[str]  # Learning points for AI
    created_at: datetime

@dataclass
class InterventionWorkflow:
    """Workflow for handling interventions"""
    workflow_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]  # Workflow steps
    escalation_rules: List[Dict[str, Any]]  # Escalation rules
    sla_minutes: int  # Service level agreement in minutes
    is_active: bool

class HumanExpertInterventionSystem:
    """Core system for human expert interventions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.expert_profiles: Dict[str, ExpertProfile] = {}
        self.active_interventions: Dict[str, InterventionRequest] = {}
        self.intervention_workflows: Dict[str, InterventionWorkflow] = {}
        self.expert_decisions: Dict[str, ExpertDecision] = {}
        
        # Configuration
        self.default_sla_minutes = 240  # 4 hours default SLA
        self.escalation_timeout_minutes = 60  # Escalate after 1 hour
        self.max_retries = 3  # Maximum retries before escalation
        
        # Expert availability tracking
        self.expert_availability = {}
        self.expert_load_balancing = True
        
        # Notification settings
        self.notification_channels = ['email', 'slack', 'dashboard']
        self.urgent_notification_channels = ['email', 'phone', 'slack']

    async def initialize_system(self):
        """Initialize the human expert intervention system"""
        try:
            # Load expert profiles
            await self._load_expert_profiles()
            
            # Load intervention workflows
            await self._load_intervention_workflows()
            
            # Load active interventions
            await self._load_active_interventions()
            
            # Start background tasks
            asyncio.create_task(self._monitor_interventions())
            asyncio.create_task(self._update_expert_availability())
            
            logger.info("✅ Human Expert Intervention System initialized", extra={
                "expert_count": len(self.expert_profiles),
                "active_interventions": len(self.active_interventions),
                "workflows": len(self.intervention_workflows)
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Human Expert Intervention System: {e}")
            raise

    async def _load_expert_profiles(self):
        """Load expert profiles from database"""
        try:
            experts_collection = self.db.expert_profiles
            async for expert_doc in experts_collection.find():
                expert = ExpertProfile(
                    expert_id=expert_doc['expert_id'],
                    name=expert_doc['name'],
                    email=expert_doc['email'],
                    level=ExpertLevel(expert_doc['level']),
                    specialties=expert_doc['specialties'],
                    availability=expert_doc['availability'],
                    current_load=expert_doc.get('current_load', 0),
                    max_load=expert_doc.get('max_load', 10),
                    success_rate=expert_doc.get('success_rate', 0.8),
                    response_time_avg=expert_doc.get('response_time_avg', 120),
                    is_available=expert_doc.get('is_available', True)
                )
                self.expert_profiles[expert.expert_id] = expert
                
        except Exception as e:
            logger.error(f"Error loading expert profiles: {e}")

    async def _load_intervention_workflows(self):
        """Load intervention workflows from database"""
        try:
            workflows_collection = self.db.intervention_workflows
            async for workflow_doc in workflows_collection.find():
                workflow = InterventionWorkflow(
                    workflow_id=workflow_doc['workflow_id'],
                    name=workflow_doc['name'],
                    description=workflow_doc['description'],
                    steps=workflow_doc['steps'],
                    escalation_rules=workflow_doc['escalation_rules'],
                    sla_minutes=workflow_doc.get('sla_minutes', self.default_sla_minutes),
                    is_active=workflow_doc.get('is_active', True)
                )
                self.intervention_workflows[workflow.workflow_id] = workflow
                
        except Exception as e:
            logger.error(f"Error loading intervention workflows: {e}")

    async def _load_active_interventions(self):
        """Load active interventions from database"""
        try:
            interventions_collection = self.db.intervention_requests
            async for intervention_doc in interventions_collection.find():
                intervention = InterventionRequest(
                    request_id=intervention_doc['request_id'],
                    client_id=intervention_doc['client_id'],
                    intervention_type=InterventionType(intervention_doc['intervention_type']),
                    status=InterventionStatus(intervention_doc['status']),
                    priority=intervention_doc['priority'],
                    complexity=DecisionComplexity(intervention_doc['complexity']),
                    title=intervention_doc['title'],
                    description=intervention_doc['description'],
                    context=intervention_doc['context'],
                    ai_recommendation=intervention_doc.get('ai_recommendation'),
                    ai_confidence=intervention_doc.get('ai_confidence', 0.5),
                    required_expert_level=ExpertLevel(intervention_doc['required_expert_level']),
                    assigned_expert=intervention_doc.get('assigned_expert'),
                    created_at=intervention_doc['created_at'],
                    updated_at=intervention_doc['updated_at'],
                    deadline=intervention_doc.get('deadline'),
                    escalation_history=intervention_doc.get('escalation_history', []),
                    attachments=intervention_doc.get('attachments', []),
                    tags=intervention_doc.get('tags', [])
                )
                self.active_interventions[intervention.request_id] = intervention
                
        except Exception as e:
            logger.error(f"Error loading active interventions: {e}")

    async def request_intervention(self, client_id: str, intervention_type: InterventionType,
                                 title: str, description: str, context: Dict[str, Any],
                                 ai_recommendation: Optional[str] = None,
                                 ai_confidence: float = 0.5,
                                 priority: int = 5,
                                 complexity: DecisionComplexity = DecisionComplexity.MEDIUM,
                                 deadline_minutes: Optional[int] = None) -> str:
        """Request human expert intervention"""
        try:
            request_id = str(uuid.uuid4())
            
            # Determine required expert level based on complexity and priority
            required_level = await self._determine_required_expert_level(complexity, priority)
            
            # Calculate deadline
            deadline = None
            if deadline_minutes:
                deadline = datetime.utcnow() + timedelta(minutes=deadline_minutes)
            elif intervention_type == InterventionType.EMERGENCY:
                deadline = datetime.utcnow() + timedelta(minutes=30)
            else:
                deadline = datetime.utcnow() + timedelta(minutes=self.default_sla_minutes)
            
            # Create intervention request
            intervention = InterventionRequest(
                request_id=request_id,
                client_id=client_id,
                intervention_type=intervention_type,
                status=InterventionStatus.PENDING,
                priority=priority,
                complexity=complexity,
                title=title,
                description=description,
                context=context,
                ai_recommendation=ai_recommendation,
                ai_confidence=ai_confidence,
                required_expert_level=required_level,
                assigned_expert=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deadline=deadline,
                escalation_history=[],
                attachments=[],
                tags=[]
            )
            
            # Assign expert
            assigned_expert = await self._assign_expert(intervention)
            if assigned_expert:
                intervention.assigned_expert = assigned_expert
                intervention.status = InterventStatus.IN_PROGRESS
            
            # Save to database
            await self._save_intervention_request(intervention)
            
            # Add to active interventions
            self.active_interventions[request_id] = intervention
            
            # Send notifications
            await self._send_intervention_notifications(intervention)
            
            logger.info(f"Created intervention request {request_id}", extra={
                "client_id": client_id,
                "intervention_type": intervention_type.value,
                "priority": priority,
                "assigned_expert": assigned_expert
            })
            
            return request_id
            
        except Exception as e:
            logger.error(f"Error requesting intervention: {e}")
            raise

    async def _determine_required_expert_level(self, complexity: DecisionComplexity, 
                                            priority: int) -> ExpertLevel:
        """Determine required expert level based on complexity and priority"""
        if complexity == DecisionComplexity.EMERGENCY or priority >= 9:
            return ExpertLevel.DIRECTOR
        elif complexity == DecisionComplexity.CRITICAL or priority >= 7:
            return ExpertLevel.PRINCIPAL
        elif complexity == DecisionComplexity.HIGH or priority >= 5:
            return ExpertLevel.LEAD
        elif complexity == DecisionComplexity.MEDIUM or priority >= 3:
            return ExpertLevel.SENIOR
        else:
            return ExpertLevel.JUNIOR

    async def _assign_expert(self, intervention: InterventionRequest) -> Optional[str]:
        """Assign expert to intervention request"""
        try:
            # Find available experts with required level or higher
            available_experts = []
            
            for expert_id, expert in self.expert_profiles.items():
                if (expert.is_available and 
                    expert.current_load < expert.max_load and
                    self._expert_level_sufficient(expert.level, intervention.required_expert_level)):
                    available_experts.append((expert_id, expert))
            
            if not available_experts:
                return None
            
            # Sort by load and response time
            available_experts.sort(key=lambda x: (x[1].current_load, x[1].response_time_avg))
            
            # Assign to best expert
            assigned_expert_id, assigned_expert = available_experts[0]
            
            # Update expert load
            assigned_expert.current_load += 1
            
            return assigned_expert_id
            
        except Exception as e:
            logger.error(f"Error assigning expert: {e}")
            return None

    def _expert_level_sufficient(self, expert_level: ExpertLevel, 
                                required_level: ExpertLevel) -> bool:
        """Check if expert level is sufficient for required level"""
        level_hierarchy = {
            ExpertLevel.JUNIOR: 1,
            ExpertLevel.SENIOR: 2,
            ExpertLevel.LEAD: 3,
            ExpertLevel.PRINCIPAL: 4,
            ExpertLevel.DIRECTOR: 5
        }
        
        return level_hierarchy[expert_level] >= level_hierarchy[required_level]

    async def submit_expert_decision(self, request_id: str, expert_id: str,
                                   decision: str, reasoning: str,
                                   confidence: float = 0.8,
                                   alternatives_considered: Optional[List[str]] = None,
                                   risk_assessment: Optional[str] = None,
                                   follow_up_actions: Optional[List[str]] = None,
                                   learning_points: Optional[List[str]] = None) -> str:
        """Submit expert decision for intervention request"""
        try:
            if request_id not in self.active_interventions:
                raise ValueError(f"Intervention request {request_id} not found")
            
            intervention = self.active_interventions[request_id]
            
            # Verify expert assignment
            if intervention.assigned_expert != expert_id:
                raise ValueError(f"Expert {expert_id} not assigned to request {request_id}")
            
            # Create expert decision
            decision_id = str(uuid.uuid4())
            expert_decision = ExpertDecision(
                decision_id=decision_id,
                request_id=request_id,
                expert_id=expert_id,
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                alternatives_considered=alternatives_considered or [],
                risk_assessment=risk_assessment or "Standard risk assessment",
                follow_up_actions=follow_up_actions or [],
                learning_points=learning_points or [],
                created_at=datetime.utcnow()
            )
            
            # Save decision
            await self._save_expert_decision(expert_decision)
            self.expert_decisions[decision_id] = expert_decision
            
            # Update intervention status
            intervention.status = InterventStatus.COMPLETED
            intervention.updated_at = datetime.utcnow()
            
            # Update expert load
            if expert_id in self.expert_profiles:
                self.expert_profiles[expert_id].current_load = max(0, 
                    self.expert_profiles[expert_id].current_load - 1)
            
            # Save updated intervention
            await self._save_intervention_request(intervention)
            
            # Send completion notifications
            await self._send_completion_notifications(intervention, expert_decision)
            
            logger.info(f"Expert decision submitted for request {request_id}", extra={
                "expert_id": expert_id,
                "decision_id": decision_id,
                "confidence": confidence
            })
            
            return decision_id
            
        except Exception as e:
            logger.error(f"Error submitting expert decision: {e}")
            raise

    async def escalate_intervention(self, request_id: str, reason: str,
                                  escalate_to_level: Optional[ExpertLevel] = None) -> bool:
        """Escalate intervention to higher level expert"""
        try:
            if request_id not in self.active_interventions:
                return False
            
            intervention = self.active_interventions[request_id]
            
            # Determine escalation level
            if not escalate_to_level:
                escalate_to_level = await self._get_next_expert_level(intervention.required_expert_level)
            
            # Record escalation
            escalation_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason,
                "from_level": intervention.required_expert_level.value,
                "to_level": escalate_to_level.value,
                "escalated_by": "system"
            }
            
            intervention.escalation_history.append(escalation_record)
            intervention.required_expert_level = escalate_to_level
            intervention.status = InterventStatus.ESCALATED
            intervention.updated_at = datetime.utcnow()
            
            # Reassign expert
            old_expert = intervention.assigned_expert
            if old_expert and old_expert in self.expert_profiles:
                self.expert_profiles[old_expert].current_load = max(0,
                    self.expert_profiles[old_expert].current_load - 1)
            
            new_expert = await self._assign_expert(intervention)
            if new_expert:
                intervention.assigned_expert = new_expert
                intervention.status = InterventStatus.IN_PROGRESS
            
            # Save updated intervention
            await self._save_intervention_request(intervention)
            
            # Send escalation notifications
            await self._send_escalation_notifications(intervention, escalation_record)
            
            logger.info(f"Escalated intervention {request_id}", extra={
                "reason": reason,
                "new_level": escalate_to_level.value,
                "new_expert": new_expert
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error escalating intervention: {e}")
            return False

    async def _get_next_expert_level(self, current_level: ExpertLevel) -> ExpertLevel:
        """Get next higher expert level"""
        level_hierarchy = [
            ExpertLevel.JUNIOR,
            ExpertLevel.SENIOR,
            ExpertLevel.LEAD,
            ExpertLevel.PRINCIPAL,
            ExpertLevel.DIRECTOR
        ]
        
        current_index = level_hierarchy.index(current_level)
        if current_index < len(level_hierarchy) - 1:
            return level_hierarchy[current_index + 1]
        else:
            return ExpertLevel.DIRECTOR  # Already at highest level

    async def get_intervention_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of intervention request"""
        try:
            if request_id not in self.active_interventions:
                return None
            
            intervention = self.active_interventions[request_id]
            
            return {
                "request_id": intervention.request_id,
                "client_id": intervention.client_id,
                "status": intervention.status.value,
                "priority": intervention.priority,
                "complexity": intervention.complexity.value,
                "title": intervention.title,
                "assigned_expert": intervention.assigned_expert,
                "created_at": intervention.created_at.isoformat(),
                "updated_at": intervention.updated_at.isoformat(),
                "deadline": intervention.deadline.isoformat() if intervention.deadline else None,
                "escalation_count": len(intervention.escalation_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting intervention status: {e}")
            return None

    async def get_expert_workload(self, expert_id: str) -> Dict[str, Any]:
        """Get expert workload information"""
        try:
            if expert_id not in self.expert_profiles:
                return {"error": "Expert not found"}
            
            expert = self.expert_profiles[expert_id]
            
            # Count active interventions for this expert
            active_count = sum(1 for intervention in self.active_interventions.values()
                             if intervention.assigned_expert == expert_id and
                             intervention.status in [InterventStatus.PENDING, InterventStatus.IN_PROGRESS])
            
            return {
                "expert_id": expert_id,
                "name": expert.name,
                "level": expert.level.value,
                "current_load": expert.current_load,
                "max_load": expert.max_load,
                "active_interventions": active_count,
                "is_available": expert.is_available,
                "success_rate": expert.success_rate,
                "response_time_avg": expert.response_time_avg
            }
            
        except Exception as e:
            logger.error(f"Error getting expert workload: {e}")
            return {"error": str(e)}

    async def _monitor_interventions(self):
        """Background task to monitor interventions"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                
                for request_id, intervention in self.active_interventions.items():
                    # Check for expired interventions
                    if (intervention.deadline and 
                        current_time > intervention.deadline and
                        intervention.status in [InterventStatus.PENDING, InterventStatus.IN_PROGRESS]):
                        
                        await self.escalate_intervention(
                            request_id, 
                            "Deadline exceeded - automatic escalation"
                        )
                    
                    # Check for stale interventions
                    elif (intervention.status == InterventStatus.IN_PROGRESS and
                          current_time - intervention.updated_at > timedelta(minutes=self.escalation_timeout_minutes)):
                        
                        await self.escalate_intervention(
                            request_id,
                            "No response within timeout - automatic escalation"
                        )
                
            except Exception as e:
                logger.error(f"Error in intervention monitoring: {e}")

    async def _update_expert_availability(self):
        """Background task to update expert availability"""
        while True:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                
                # Update availability based on current load
                for expert_id, expert in self.expert_profiles.items():
                    expert.is_available = expert.current_load < expert.max_load
                
                # Save updated profiles
                for expert in self.expert_profiles.values():
                    await self._save_expert_profile(expert)
                
            except Exception as e:
                logger.error(f"Error updating expert availability: {e}")

    async def _send_intervention_notifications(self, intervention: InterventionRequest):
        """Send notifications for new intervention request"""
        try:
            # This would integrate with actual notification systems
            logger.info(f"Sending intervention notifications for {intervention.request_id}")
            
        except Exception as e:
            logger.error(f"Error sending intervention notifications: {e}")

    async def _send_completion_notifications(self, intervention: InterventionRequest, 
                                           decision: ExpertDecision):
        """Send notifications for completed intervention"""
        try:
            logger.info(f"Sending completion notifications for {intervention.request_id}")
            
        except Exception as e:
            logger.error(f"Error sending completion notifications: {e}")

    async def _send_escalation_notifications(self, intervention: InterventionRequest, 
                                           escalation_record: Dict[str, Any]):
        """Send notifications for escalated intervention"""
        try:
            logger.info(f"Sending escalation notifications for {intervention.request_id}")
            
        except Exception as e:
            logger.error(f"Error sending escalation notifications: {e}")

    async def _save_intervention_request(self, intervention: InterventionRequest):
        """Save intervention request to database"""
        try:
            interventions_collection = self.db.intervention_requests
            await interventions_collection.replace_one(
                {'request_id': intervention.request_id},
                asdict(intervention),
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving intervention request: {e}")

    async def _save_expert_decision(self, decision: ExpertDecision):
        """Save expert decision to database"""
        try:
            decisions_collection = self.db.expert_decisions
            await decisions_collection.insert_one(asdict(decision))
        except Exception as e:
            logger.error(f"Error saving expert decision: {e}")

    async def _save_expert_profile(self, expert: ExpertProfile):
        """Save expert profile to database"""
        try:
            experts_collection = self.db.expert_profiles
            await experts_collection.replace_one(
                {'expert_id': expert.expert_id},
                asdict(expert),
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving expert profile: {e}")

    async def close(self):
        """Close the human expert intervention system"""
        try:
            # Save any pending data
            for intervention in self.active_interventions.values():
                await self._save_intervention_request(intervention)
            
            for expert in self.expert_profiles.values():
                await self._save_expert_profile(expert)
            
            logger.info("✅ Human Expert Intervention System closed")
            
        except Exception as e:
            logger.error(f"Error closing Human Expert Intervention System: {e}")

# Global instance
_human_expert_system = None

async def get_human_expert_system(db: AsyncIOMotorDatabase) -> HumanExpertInterventionSystem:
    """Get or create human expert intervention system instance"""
    global _human_expert_system
    if _human_expert_system is None:
        _human_expert_system = HumanExpertInterventionSystem(db)
        await _human_expert_system.initialize_system()
    return _human_expert_system
