"""
User and Organization Models for Omnify Cloud Connect
Handles multi-tenant user management with JWT authentication
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles within an organization"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    STARTER = "starter"          # $99/month - Basic features
    PROFESSIONAL = "professional"  # $299/month - Full features
    ENTERPRISE = "enterprise"     # $599/month - Advanced features


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"


# ========== USER MANAGEMENT MODELS ==========

class User(BaseModel):
    """User model"""
    user_id: str
    email: EmailStr
    password_hash: str
    full_name: str
    organization_id: str
    role: UserRole = UserRole.MEMBER
    agentkit_user_id: Optional[str] = None
    gohighlevel_user_id: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    subscription_id: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    """User creation request"""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    organization_name: Optional[str] = None
    invitation_code: Optional[str] = None


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update request"""
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    password: Optional[str] = Field(None, min_length=8)


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8)


# ========== ORGANIZATION MODELS ==========

class Organization(BaseModel):
    """Organization model"""
    organization_id: str
    name: str
    slug: str  # URL-friendly identifier
    owner_id: str
    agentkit_tenant_id: Optional[str] = None
    gohighlevel_location_id: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "branding": {
            "logo_url": None,
            "primary_color": "#2563eb",
            "secondary_color": "#64748b"
        },
        "integrations": {
            "google_ads": {"enabled": False, "account_id": None},
            "meta_ads": {"enabled": False, "account_id": None},
            "linkedin_ads": {"enabled": False, "account_id": None}
        }
    })
    subscription_tier: SubscriptionTier = SubscriptionTier.STARTER
    max_users: int = 5
    max_campaigns: int = 50
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrganizationCreate(BaseModel):
    """Organization creation request"""
    name: str
    slug: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Organization update request"""
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


# ========== SUBSCRIPTION MODELS ==========

class Subscription(BaseModel):
    """Subscription model"""
    subscription_id: str
    organization_id: str
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    tier: SubscriptionTier
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    usage: Dict[str, int] = Field(default_factory=lambda: {
        "users": 0,
        "campaigns": 0,
        "api_calls": 0,
        "storage_gb": 0
    })
    limits: Dict[str, int] = Field(default_factory=lambda: {
        "users": 5,
        "campaigns": 50,
        "api_calls": 10000,
        "storage_gb": 5
    })
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionCreate(BaseModel):
    """Subscription creation request"""
    organization_id: str
    tier: SubscriptionTier
    trial_days: int = 14


# ========== AUTHENTICATION MODELS ==========

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    organization: Dict[str, Any]


class TokenData(BaseModel):
    """JWT token payload"""
    user_id: str
    organization_id: str
    role: UserRole
    exp: datetime


class UserInvitation(BaseModel):
    """User invitation model"""
    invitation_id: str
    organization_id: str
    email: EmailStr
    role: UserRole
    invited_by: str
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserInvitationCreate(BaseModel):
    """User invitation creation"""
    email: EmailStr
    role: UserRole


class UserInvitationAccept(BaseModel):
    """User invitation acceptance"""
    token: str
    password: str = Field(min_length=8)
    full_name: str


# ========== CLIENT MANAGEMENT MODELS ==========

class Client(BaseModel):
    """Client model (CRM contacts)"""
    client_id: str
    organization_id: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    gohighlevel_contact_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active, inactive, archived
    subscription_value: Optional[float] = None
    last_contact: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ClientCreate(BaseModel):
    """Client creation request"""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ClientUpdate(BaseModel):
    """Client update request"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    subscription_value: Optional[float] = None


# ========== CAMPAIGN MODELS ==========

class Campaign(BaseModel):
    """Campaign model"""
    campaign_id: str
    organization_id: str
    name: str
    status: str = "draft"  # draft, active, paused, completed
    agentkit_workflow_id: Optional[str] = None
    gohighlevel_campaign_id: Optional[str] = None
    platforms: List[Dict[str, Any]] = Field(default_factory=list)
    brief: Dict[str, Any] = Field(default_factory=dict)
    budget_total: Optional[float] = None
    budget_spent: float = 0.0
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CampaignCreate(BaseModel):
    """Campaign creation request"""
    name: str
    brief: Dict[str, Any] = Field(default_factory=dict)
    budget_total: Optional[float] = None
    platforms: List[str] = Field(default_factory=list)


# ========== ANALYTICS MODELS ==========

class AnalyticsEntry(BaseModel):
    """Analytics entry model"""
    entry_id: str
    organization_id: str
    campaign_id: Optional[str] = None
    date: datetime
    platform: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsSummary(BaseModel):
    """Analytics summary model"""
    organization_id: str
    period_start: datetime
    period_end: datetime
    total_metrics: Dict[str, Any] = Field(default_factory=dict)
    platform_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    campaign_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== ASSET MODELS ==========

class Asset(BaseModel):
    """Asset model (creative files)"""
    asset_id: str
    organization_id: str
    campaign_id: Optional[str] = None
    name: str
    asset_type: str  # image, video, document, text
    file_url: str
    file_size: int
    mime_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
