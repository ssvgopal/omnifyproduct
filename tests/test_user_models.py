# tests/test_user_models.py
"""
User Models Tests
Tests for user, organization, subscription, and authentication models
"""

import pytest
from datetime import datetime, timedelta
from models.user_models import (
    User, UserCreate, UserLogin, UserUpdate, UserRole, SubscriptionTier,
    SubscriptionStatus, Organization, OrganizationCreate, Subscription,
    Token, TokenData, UserInvitation, UserInvitationCreate, Client,
    ClientCreate, Campaign, CampaignCreate, AnalyticsEntry, Asset
)


class TestUserModels:
    """Test suite for User Models"""

    def test_user_model_validation(self):
        """Test User model validation"""
        user_data = {
            "user_id": "test_user_id",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "full_name": "Test User",
            "organization_id": "test_org_id",
            "role": UserRole.MEMBER,
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user = User(**user_data)
        
        assert user.user_id == "test_user_id"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.MEMBER
        assert user.is_active is True

    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        user_create_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "organization_name": "New Organization"
        }
        
        user_create = UserCreate(**user_create_data)
        
        assert user_create.email == "newuser@example.com"
        assert user_create.password == "password123"
        assert user_create.full_name == "New User"
        assert user_create.organization_name == "New Organization"

    def test_user_login_validation(self):
        """Test UserLogin model validation"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        user_login = UserLogin(**login_data)
        
        assert user_login.email == "test@example.com"
        assert user_login.password == "password123"

    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.OWNER == "owner"
        assert UserRole.ADMIN == "admin"
        assert UserRole.MANAGER == "manager"
        assert UserRole.MEMBER == "member"
        assert UserRole.VIEWER == "viewer"

    def test_subscription_tier_enum(self):
        """Test SubscriptionTier enum values"""
        assert SubscriptionTier.STARTER == "starter"
        assert SubscriptionTier.PROFESSIONAL == "professional"
        assert SubscriptionTier.ENTERPRISE == "enterprise"

    def test_subscription_status_enum(self):
        """Test SubscriptionStatus enum values"""
        assert SubscriptionStatus.TRIAL == "trial"
        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.PAST_DUE == "past_due"
        assert SubscriptionStatus.CANCELLED == "cancelled"
        assert SubscriptionStatus.UNPAID == "unpaid"

    def test_organization_model_validation(self):
        """Test Organization model validation"""
        org_data = {
            "organization_id": "test_org_id",
            "name": "Test Organization",
            "slug": "test-org",
            "owner_id": "test_user_id",
            "subscription_tier": SubscriptionTier.STARTER,
            "max_users": 5,
            "max_campaigns": 50,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        organization = Organization(**org_data)
        
        assert organization.organization_id == "test_org_id"
        assert organization.name == "Test Organization"
        assert organization.slug == "test-org"
        assert organization.subscription_tier == SubscriptionTier.STARTER
        assert organization.max_users == 5
        assert organization.max_campaigns == 50

    def test_subscription_model_validation(self):
        """Test Subscription model validation"""
        subscription_data = {
            "subscription_id": "test_sub_id",
            "organization_id": "test_org_id",
            "tier": SubscriptionTier.PROFESSIONAL,
            "status": SubscriptionStatus.ACTIVE,
            "current_period_start": datetime.utcnow(),
            "current_period_end": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        subscription = Subscription(**subscription_data)
        
        assert subscription.subscription_id == "test_sub_id"
        assert subscription.organization_id == "test_org_id"
        assert subscription.tier == SubscriptionTier.PROFESSIONAL
        assert subscription.status == SubscriptionStatus.ACTIVE

    def test_token_model_validation(self):
        """Test Token model validation"""
        token_data = {
            "access_token": "jwt_token_string",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {"user_id": "test_user_id", "email": "test@example.com"},
            "organization": {"organization_id": "test_org_id", "name": "Test Org"}
        }
        
        token = Token(**token_data)
        
        assert token.access_token == "jwt_token_string"
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
        assert token.user["user_id"] == "test_user_id"
        assert token.organization["organization_id"] == "test_org_id"

    def test_user_invitation_model_validation(self):
        """Test UserInvitation model validation"""
        invitation_data = {
            "invitation_id": "test_invitation_id",
            "organization_id": "test_org_id",
            "email": "invite@example.com",
            "role": UserRole.MEMBER,
            "invited_by": "test_user_id",
            "token": "invitation_token",
            "expires_at": datetime.utcnow() + timedelta(days=7),
            "created_at": datetime.utcnow()
        }
        
        invitation = UserInvitation(**invitation_data)
        
        assert invitation.invitation_id == "test_invitation_id"
        assert invitation.organization_id == "test_org_id"
        assert invitation.email == "invite@example.com"
        assert invitation.role == UserRole.MEMBER
        assert invitation.token == "invitation_token"

    def test_client_model_validation(self):
        """Test Client model validation"""
        client_data = {
            "client_id": "test_client_id",
            "organization_id": "test_org_id",
            "email": "client@example.com",
            "full_name": "Test Client",
            "phone": "+1234567890",
            "company": "Test Company",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        client = Client(**client_data)
        
        assert client.client_id == "test_client_id"
        assert client.organization_id == "test_org_id"
        assert client.email == "client@example.com"
        assert client.full_name == "Test Client"
        assert client.phone == "+1234567890"
        assert client.company == "Test Company"

    def test_campaign_model_validation(self):
        """Test Campaign model validation"""
        campaign_data = {
            "campaign_id": "test_campaign_id",
            "organization_id": "test_org_id",
            "name": "Test Campaign",
            "status": "draft",
            "budget_total": 1000.0,
            "budget_spent": 0.0,
            "created_by": "test_user_id",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        campaign = Campaign(**campaign_data)
        
        assert campaign.campaign_id == "test_campaign_id"
        assert campaign.organization_id == "test_org_id"
        assert campaign.name == "Test Campaign"
        assert campaign.status == "draft"
        assert campaign.budget_total == 1000.0
        assert campaign.budget_spent == 0.0

    def test_analytics_entry_model_validation(self):
        """Test AnalyticsEntry model validation"""
        analytics_data = {
            "entry_id": "test_entry_id",
            "organization_id": "test_org_id",
            "campaign_id": "test_campaign_id",
            "date": datetime.utcnow(),
            "platform": "google_ads",
            "metrics": {"impressions": 1000, "clicks": 50, "conversions": 5},
            "created_at": datetime.utcnow()
        }
        
        analytics_entry = AnalyticsEntry(**analytics_data)
        
        assert analytics_entry.entry_id == "test_entry_id"
        assert analytics_entry.organization_id == "test_org_id"
        assert analytics_entry.campaign_id == "test_campaign_id"
        assert analytics_entry.platform == "google_ads"
        assert analytics_entry.metrics["impressions"] == 1000

    def test_asset_model_validation(self):
        """Test Asset model validation"""
        asset_data = {
            "asset_id": "test_asset_id",
            "organization_id": "test_org_id",
            "campaign_id": "test_campaign_id",
            "name": "Test Asset",
            "asset_type": "image",
            "file_url": "https://example.com/image.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "created_by": "test_user_id",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        asset = Asset(**asset_data)
        
        assert asset.asset_id == "test_asset_id"
        assert asset.organization_id == "test_org_id"
        assert asset.name == "Test Asset"
        assert asset.asset_type == "image"
        assert asset.file_url == "https://example.com/image.jpg"
        assert asset.file_size == 1024000
        assert asset.mime_type == "image/jpeg"

    def test_model_serialization(self):
        """Test model serialization to dict"""
        user_data = {
            "user_id": "test_user_id",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "full_name": "Test User",
            "organization_id": "test_org_id",
            "role": UserRole.MEMBER,
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user = User(**user_data)
        user_dict = user.dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict["user_id"] == "test_user_id"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "member"
        assert user_dict["is_active"] is True
