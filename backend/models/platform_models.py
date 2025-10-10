from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Platform Configuration Models
class PlatformConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_type: str  # agentkit, gohighlevel, custom
    name: str
    api_key: Optional[str] = None
    settings: Dict[str, Any] = {}
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PlatformConfigCreate(BaseModel):
    platform_type: str
    name: str
    api_key: Optional[str] = None
    settings: Dict[str, Any] = {}

# Agent Models (for AgentKit)
class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # creative, marketing, client, analytics
    capabilities: List[str] = []
    platform: str = 'agentkit'
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentCreate(BaseModel):
    name: str
    type: str
    capabilities: List[str] = []

class AgentExecution(BaseModel):
    agent_id: str
    input_data: Dict[str, Any]

# Workflow Models
class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    platform: str  # agentkit, gohighlevel, custom
    trigger: str = 'manual'
    steps: List[Dict[str, Any]] = []
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowCreate(BaseModel):
    name: str
    platform: str
    trigger: str = 'manual'
    steps: List[Dict[str, Any]] = []

class WorkflowExecution(BaseModel):
    workflow_id: str
    data: Dict[str, Any] = {}

# Client Models (for GoHighLevel)
class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    platform: str = 'gohighlevel'
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

# Campaign Models
class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # email, sms, social
    target_audience: List[str] = []
    platform: str = 'gohighlevel'
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignCreate(BaseModel):
    name: str
    type: str
    target_audience: List[str] = []

# Microservice Models (for Custom Platform)
class Microservice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # api, worker, processor
    replicas: int = 1
    resources: Dict[str, Any] = {}
    platform: str = 'custom'
    status: str = 'running'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MicroserviceCreate(BaseModel):
    name: str
    type: str
    replicas: int = 1
    resources: Dict[str, Any] = {}

class ServiceScale(BaseModel):
    service_id: str
    replicas: int