from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Creative Intelligence Models
class ContentAnalysis(BaseModel):
    content: str
    context: Optional[Dict[str, Any]] = None

class ContentRepurposing(BaseModel):
    content: str
    target_format: str  # social_post, blog_article, email_campaign, video_script
    brand_id: Optional[str] = None

class BrandCompliance(BaseModel):
    content: str
    brand_id: str

class PerformanceOptimization(BaseModel):
    content: str
    platform: str  # instagram, linkedin, facebook, twitter
    objective: str  # engagement, reach, conversion

class BrandProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tone: str = 'professional'
    values: List[str] = []
    visual_guidelines: Dict[str, Any] = {}
    messaging_guidelines: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BrandProfileCreate(BaseModel):
    name: str
    tone: str = 'professional'
    values: List[str] = []
    visual_guidelines: Dict[str, Any] = {}
    messaging_guidelines: Dict[str, Any] = {}

# Market Intelligence Models
class VerticalAnalysis(BaseModel):
    vertical: str  # ecommerce, saas, healthcare, finance, education
    data: Optional[Dict[str, Any]] = None

class TrendPrediction(BaseModel):
    vertical: str
    timeframe: str = '12_months'

class CompetitorAnalysis(BaseModel):
    competitor_name: str
    vertical: str

class OpportunityIdentification(BaseModel):
    vertical: str
    client_profile: Dict[str, Any]

# Client Intelligence Models
class BehaviorAnalysis(BaseModel):
    client_id: str
    behavior_data: Dict[str, Any]

class SuccessPrediction(BaseModel):
    client_id: str

class ChurnRiskAnalysis(BaseModel):
    client_id: str

class SatisfactionTracking(BaseModel):
    client_id: str
    feedback_data: Dict[str, Any]

class ClientProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: str = 'general'
    size: str = 'medium'
    goals: List[str] = []
    preferences: Dict[str, Any] = {}
    success_metrics: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientProfileCreate(BaseModel):
    name: str
    industry: str = 'general'
    size: str = 'medium'
    goals: List[str] = []
    preferences: Dict[str, Any] = {}
    success_metrics: List[str] = []

# Customization Models
class CustomConfiguration(BaseModel):
    name: str
    vertical: str
    client_id: Optional[str] = None
    platform: str = 'custom'
    settings: Dict[str, Any] = {}

class VerticalTemplate(BaseModel):
    vertical: str
    client_id: str

class BrandCustomization(BaseModel):
    client_id: Optional[str] = None
    brand_name: str
    primary_color: str = '#0066cc'
    secondary_color: str = '#00cc66'
    accent_color: str = '#cc0066'
    logo_url: Optional[str] = None
    primary_font: str = 'Arial'
    secondary_font: str = 'Helvetica'
    tone: str = 'professional'
    messaging_guidelines: Dict[str, Any] = {}

class CustomWorkflow(BaseModel):
    name: str
    vertical: str = 'general'
    trigger: str = 'manual'
    steps: List[Dict[str, Any]] = []
    conditions: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    schedule: str = 'on_demand'

class IntegrationConfiguration(BaseModel):
    name: str
    type: str
    provider: str
    endpoints: List[str] = []
    sync_frequency: str = 'hourly'
    data_mapping: Dict[str, Any] = {}