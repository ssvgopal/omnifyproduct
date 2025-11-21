"""
Client Onboarding Models for OmnifyProduct
Handles client/user onboarding with file storage, credentials, and platform connections
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class OnboardingStatus(str, Enum):
    """Onboarding status stages"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    CREDENTIALS_PENDING = "credentials_pending"
    PLATFORMS_CONNECTING = "platforms_connecting"
    PLATFORMS_CONNECTED = "platforms_connected"
    READY = "ready"
    COMPLETED = "completed"


class FileCategory(str, Enum):
    """File categories for client assets"""
    LOGO = "logo"
    CREATIVE = "creative"
    ANALYSIS_DOCUMENT = "analysis_document"
    CAMPAIGN_IDEA = "campaign_idea"
    BRAND_GUIDE = "brand_guide"
    OTHER = "other"


class PlatformConnectionStatus(str, Enum):
    """Platform connection status"""
    NOT_CONNECTED = "not_connected"
    PENDING = "pending"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    EXPIRED = "expired"


# ========== CLIENT PROFILE MODELS ==========

class ClientProfile(BaseModel):
    """Client profile model for onboarding"""
    client_id: str
    organization_id: str
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    # Contact information
    primary_contact_name: str
    primary_contact_email: EmailStr
    primary_contact_phone: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    brand_colors: List[str] = Field(default_factory=list)
    brand_fonts: List[str] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    
    # Onboarding status
    onboarding_status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    onboarding_progress: float = 0.0  # 0.0 to 1.0
    
    # Platform connections
    platform_connections: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Files and assets
    uploaded_files: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Campaign ideas and notes
    campaign_ideas: List[Dict[str, Any]] = Field(default_factory=list)
    analysis_notes: Optional[str] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ClientProfileCreate(BaseModel):
    """Client profile creation request"""
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    primary_contact_name: str
    primary_contact_email: EmailStr
    primary_contact_phone: Optional[str] = None


class ClientProfileUpdate(BaseModel):
    """Client profile update request"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = None
    brand_colors: Optional[List[str]] = None
    brand_fonts: Optional[List[str]] = None
    brand_voice: Optional[str] = None
    analysis_notes: Optional[str] = None


# ========== FILE UPLOAD MODELS ==========

class UploadedFile(BaseModel):
    """Uploaded file metadata"""
    file_id: str
    client_id: str
    file_name: str
    file_category: FileCategory
    file_url: str
    file_size: int
    mime_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str
    file_name: str
    file_url: str
    file_size: int
    file_category: str
    uploaded_at: str


# ========== CREDENTIALS MODELS ==========

class PlatformCredential(BaseModel):
    """Platform credential model"""
    platform: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    account_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    additional_config: Dict[str, Any] = Field(default_factory=dict)
    connection_status: PlatformConnectionStatus = PlatformConnectionStatus.NOT_CONNECTED
    last_verified: Optional[datetime] = None
    error_message: Optional[str] = None


class CredentialStoreRequest(BaseModel):
    """Request to store platform credentials"""
    platform: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    account_id: Optional[str] = None
    expires_at: Optional[str] = None
    additional_config: Dict[str, Any] = Field(default_factory=dict)


class CredentialTestRequest(BaseModel):
    """Request to test platform credentials"""
    platform: str


# ========== CAMPAIGN IDEAS MODELS ==========

class CampaignIdea(BaseModel):
    """Campaign idea model"""
    idea_id: str
    client_id: str
    title: str
    description: str
    target_audience: Optional[str] = None
    platforms: List[str] = Field(default_factory=list)
    budget_estimate: Optional[float] = None
    timeline: Optional[str] = None
    status: str = "draft"  # draft, approved, in_progress, completed
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CampaignIdeaCreate(BaseModel):
    """Campaign idea creation request"""
    title: str
    description: str
    target_audience: Optional[str] = None
    platforms: List[str] = Field(default_factory=list)
    budget_estimate: Optional[float] = None
    timeline: Optional[str] = None


# ========== ONBOARDING STATUS MODELS ==========

class OnboardingStatusResponse(BaseModel):
    """Onboarding status response"""
    client_id: str
    onboarding_status: str
    onboarding_progress: float
    completed_steps: List[str]
    pending_steps: List[str]
    platform_connections: Dict[str, Dict[str, Any]]
    next_steps: List[str]
    estimated_completion_time: Optional[str] = None


class NextStepsResponse(BaseModel):
    """Next steps response"""
    client_id: str
    current_stage: str
    next_steps: List[Dict[str, Any]]
    recommendations: List[str]
    blockers: List[str] = Field(default_factory=list)

