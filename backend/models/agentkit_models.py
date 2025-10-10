"""
AgentKit Integration Models for Omnify Cloud Connect
Defines data models for AgentKit agent management and execution
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of AgentKit agents"""
    CREATIVE_INTELLIGENCE = "creative_intelligence"
    MARKETING_AUTOMATION = "marketing_automation"
    CLIENT_MANAGEMENT = "client_management"
    ANALYTICS = "analytics"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    COMPLIANCE = "compliance"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ========== AGENT CONFIGURATION MODELS ==========

class AgentConfig(BaseModel):
    """AgentKit agent configuration"""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    organization_id: str
    agentkit_agent_id: Optional[str] = None  # AgentKit platform agent ID
    config: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionRequest(BaseModel):
    """Request to execute an agent"""
    agent_id: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    user_id: str
    organization_id: str


class AgentExecutionResponse(BaseModel):
    """Response from agent execution"""
    execution_id: str
    agent_id: str
    status: AgentStatus
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


# ========== WORKFLOW MODELS ==========

class WorkflowStep(BaseModel):
    """Individual step in a workflow"""
    step_id: str
    agent_type: AgentType
    input_mapping: Dict[str, str]  # Maps workflow data to agent inputs
    output_mapping: Dict[str, str]  # Maps agent outputs to workflow data
    depends_on: List[str] = Field(default_factory=list)  # Step IDs this depends on
    retry_config: Optional[Dict[str, Any]] = None


class WorkflowDefinition(BaseModel):
    """AgentKit workflow definition"""
    workflow_id: str
    name: str
    description: str
    organization_id: str
    agentkit_workflow_id: Optional[str] = None  # AgentKit platform workflow ID
    steps: List[WorkflowStep]
    triggers: List[str] = Field(default_factory=list)  # Event triggers
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowExecution(BaseModel):
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    organization_id: str
    user_id: str
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    current_step: Optional[str] = None
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


# ========== AGENT-SPECIFIC INPUT/OUTPUT MODELS ==========

class CreativeIntelligenceInput(BaseModel):
    """Input for Creative Intelligence Agent"""
    asset_url: str
    asset_type: str  # image, video, text
    analysis_type: str  # aida, brand_compliance, performance_prediction
    brand_guidelines: Optional[Dict[str, Any]] = None
    target_platforms: List[str] = Field(default_factory=list)


class CreativeIntelligenceOutput(BaseModel):
    """Output from Creative Intelligence Agent"""
    analysis_results: Dict[str, Any]
    aida_scores: Optional[Dict[str, float]] = None  # Attention, Interest, Desire, Action
    compliance_score: Optional[float] = None
    performance_prediction: Optional[Dict[str, float]] = None
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MarketingAutomationInput(BaseModel):
    """Input for Marketing Automation Agent"""
    campaign_id: str
    action: str  # create, deploy, pause, resume, optimize
    platforms: List[str]  # google_ads, meta_ads, linkedin_ads
    campaign_config: Dict[str, Any]
    budget: Optional[float] = None
    target_audience: Optional[Dict[str, Any]] = None


class MarketingAutomationOutput(BaseModel):
    """Output from Marketing Automation Agent"""
    campaign_id: str
    platform_campaign_ids: Dict[str, str]  # platform -> campaign_id
    status: str
    deployment_results: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    next_actions: List[str] = Field(default_factory=list)


class ClientManagementInput(BaseModel):
    """Input for Client Management Agent"""
    client_id: str
    action: str  # onboard, update_subscription, track_success, send_report
    client_data: Optional[Dict[str, Any]] = None
    subscription_tier: Optional[str] = None
    billing_config: Optional[Dict[str, Any]] = None


class ClientManagementOutput(BaseModel):
    """Output from Client Management Agent"""
    client_id: str
    action_result: str
    subscription_status: Optional[str] = None
    billing_status: Optional[str] = None
    success_metrics: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)


class AnalyticsInput(BaseModel):
    """Input for Analytics Agent"""
    organization_id: str
    analysis_type: str  # real_time, predictive, roi, cohort
    date_range: Dict[str, str]  # start_date, end_date
    campaigns: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    metrics: Optional[List[str]] = None


class AnalyticsOutput(BaseModel):
    """Output from Analytics Agent"""
    analysis_type: str
    metrics: Dict[str, Any]
    insights: List[str] = Field(default_factory=list)
    predictions: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    charts: Optional[Dict[str, Any]] = None  # Chart data for visualization
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== AUDIT & COMPLIANCE MODELS ==========

class AgentAuditLog(BaseModel):
    """Audit log for agent executions (SOC 2 compliance)"""
    log_id: str
    organization_id: str
    user_id: str
    agent_id: str
    execution_id: str
    action: str
    input_data_hash: str  # SHA256 hash for privacy
    output_data_hash: Optional[str] = None
    status: str
    error: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retention_until: Optional[datetime] = None  # Data retention policy


class ComplianceCheck(BaseModel):
    """Compliance check result"""
    check_id: str
    organization_id: str
    check_type: str  # soc2, iso27001, gdpr, ccpa
    status: str  # passed, failed, warning
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    next_check_at: Optional[datetime] = None
