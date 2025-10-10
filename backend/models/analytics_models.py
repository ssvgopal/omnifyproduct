from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Analytics Models
class MetricsCollection(BaseModel):
    platform: str  # agentkit, gohighlevel, custom
    metrics: Dict[str, Any]

class CrossPlatformAnalytics(BaseModel):
    timeframe: str = '30_days'

class Dashboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    widgets: List[Dict[str, Any]] = []
    filters: Dict[str, Any] = {}
    refresh_rate: str = 'real_time'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardCreate(BaseModel):
    name: str
    widgets: List[Dict[str, Any]] = []
    filters: Dict[str, Any] = {}
    refresh_rate: str = 'real_time'

class ReportGeneration(BaseModel):
    name: str
    type: str = 'summary'  # summary, detailed, custom
    timeframe: str = '30_days'

class PerformanceTracking(BaseModel):
    entity_type: str  # agent, workflow, campaign, service
    entity_id: str
    metrics: Dict[str, Any]

# Integration Models
class IntegrationRegistration(BaseModel):
    name: str
    type: str  # social_media, ai_service, analytics, communication
    provider: str
    auth_type: str = 'api_key'

class IntegrationCredentials(BaseModel):
    integration_id: str
    credentials: Dict[str, Any]

class IntegrationExecution(BaseModel):
    integration_id: str
    action: str
    data: Dict[str, Any] = {}

class DataSync(BaseModel):
    integration_id: str
    sync_config: Optional[Dict[str, Any]] = None

# API Gateway Models
class RouteRequest(BaseModel):
    platform: str  # agentkit, gohighlevel, custom
    operation: str
    data: Dict[str, Any] = {}

class AggregateResponses(BaseModel):
    responses: List[Dict[str, Any]]