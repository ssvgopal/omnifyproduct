"""
Multi-Tenancy & User Management System
Production-grade multi-tenant architecture with team collaboration and subscription management
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import stripe
import bcrypt
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import aiohttp

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class SubscriptionPlan(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"

class InvitationStatus(str, Enum):
    """Team invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

@dataclass
class User:
    """User model"""
    user_id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    organization_id: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    preferences: Dict[str, Any] = None
    permissions: List[str] = None

@dataclass
class Organization:
    """Organization model"""
    organization_id: str
    name: str
    domain: str
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    max_users: int
    max_campaigns: int
    max_storage_gb: int
    features: List[str]
    billing_info: Dict[str, Any]
    created_at: datetime = None
    updated_at: datetime = None
    settings: Dict[str, Any] = None

@dataclass
class TeamInvitation:
    """Team invitation model"""
    invitation_id: str
    organization_id: str
    email: str
    role: UserRole
    invited_by: str
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime = None
    accepted_at: Optional[datetime] = None

@dataclass
class UsageQuota:
    """Usage quota tracking"""
    organization_id: str
    quota_type: str
    current_usage: int
    limit: int
    reset_period: str
    last_reset: datetime
    created_at: datetime = None
    updated_at: datetime = None

class UserManager:
    """Manages users and authentication"""
    
    def __init__(self, db: AsyncIOMotorClient, jwt_secret: str):
        self.db = db
        self.jwt_secret = jwt_secret
        self.password_manager = PasswordManager()
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        try:
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = self.password_manager.hash_password(user_data["password"])
            
            # Create user document
            user_doc = {
                "user_id": user_id,
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "password_hash": hashed_password,
                "role": user_data["role"].value if isinstance(user_data["role"], UserRole) else user_data["role"],
                "organization_id": user_data["organization_id"],
                "is_active": True,
                "is_verified": False,
                "last_login": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "preferences": user_data.get("preferences", {}),
                "permissions": self._get_default_permissions(user_data["role"])
            }
            
            await self.db.users.insert_one(user_doc)
            
            logger.info(f"Created user {user_id} for organization {user_data['organization_id']}")
            
            return User(
                user_id=user_id,
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=UserRole(user_data["role"]),
                organization_id=user_data["organization_id"],
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                preferences=user_data.get("preferences", {}),
                permissions=self._get_default_permissions(user_data["role"])
            )
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user_doc = await self.db.users.find_one({"email": email, "is_active": True})
            if not user_doc:
                return None
            
            if not self.password_manager.verify_password(password, user_doc["password_hash"]):
                return None
            
            # Update last login
            await self.db.users.update_one(
                {"user_id": user_doc["user_id"]},
                {"$set": {"last_login": datetime.utcnow().isoformat()}}
            )
            
            return User(
                user_id=user_doc["user_id"],
                email=user_doc["email"],
                first_name=user_doc["first_name"],
                last_name=user_doc["last_name"],
                role=UserRole(user_doc["role"]),
                organization_id=user_doc["organization_id"],
                is_active=user_doc["is_active"],
                is_verified=user_doc["is_verified"],
                last_login=datetime.fromisoformat(user_doc["last_login"]) if user_doc["last_login"] else None,
                created_at=datetime.fromisoformat(user_doc["created_at"]),
                updated_at=datetime.fromisoformat(user_doc["updated_at"]),
                preferences=user_doc.get("preferences", {}),
                permissions=user_doc.get("permissions", [])
            )
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_doc = await self.db.users.find_one({"user_id": user_id})
            if not user_doc:
                return None
            
            return User(
                user_id=user_doc["user_id"],
                email=user_doc["email"],
                first_name=user_doc["first_name"],
                last_name=user_doc["last_name"],
                role=UserRole(user_doc["role"]),
                organization_id=user_doc["organization_id"],
                is_active=user_doc["is_active"],
                is_verified=user_doc["is_verified"],
                last_login=datetime.fromisoformat(user_doc["last_login"]) if user_doc["last_login"] else None,
                created_at=datetime.fromisoformat(user_doc["created_at"]),
                updated_at=datetime.fromisoformat(user_doc["updated_at"]),
                preferences=user_doc.get("preferences", {}),
                permissions=user_doc.get("permissions", [])
            )
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise
    
    async def get_organization_users(self, organization_id: str) -> List[User]:
        """Get all users in an organization"""
        try:
            user_docs = await self.db.users.find({"organization_id": organization_id, "is_active": True}).to_list(length=None)
            
            users = []
            for user_doc in user_docs:
                users.append(User(
                    user_id=user_doc["user_id"],
                    email=user_doc["email"],
                    first_name=user_doc["first_name"],
                    last_name=user_doc["last_name"],
                    role=UserRole(user_doc["role"]),
                    organization_id=user_doc["organization_id"],
                    is_active=user_doc["is_active"],
                    is_verified=user_doc["is_verified"],
                    last_login=datetime.fromisoformat(user_doc["last_login"]) if user_doc["last_login"] else None,
                    created_at=datetime.fromisoformat(user_doc["created_at"]),
                    updated_at=datetime.fromisoformat(user_doc["updated_at"]),
                    preferences=user_doc.get("preferences", {}),
                    permissions=user_doc.get("permissions", [])
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting organization users: {e}")
            raise
    
    def generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role.value,
                "organization_id": user.organization_id,
                "permissions": user.permissions,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def _get_default_permissions(self, role: Union[UserRole, str]) -> List[str]:
        """Get default permissions for role"""
        role_str = role.value if isinstance(role, UserRole) else role
        
        permissions_map = {
            UserRole.SUPER_ADMIN.value: [
                "users:create", "users:read", "users:update", "users:delete",
                "organizations:create", "organizations:read", "organizations:update", "organizations:delete",
                "campaigns:create", "campaigns:read", "campaigns:update", "campaigns:delete",
                "analytics:read", "reports:create", "reports:read", "reports:delete",
                "settings:read", "settings:update", "billing:read", "billing:update"
            ],
            UserRole.ORG_ADMIN.value: [
                "users:create", "users:read", "users:update", "users:delete",
                "organizations:read", "organizations:update",
                "campaigns:create", "campaigns:read", "campaigns:update", "campaigns:delete",
                "analytics:read", "reports:create", "reports:read", "reports:delete",
                "settings:read", "settings:update", "billing:read"
            ],
            UserRole.MANAGER.value: [
                "users:read",
                "campaigns:create", "campaigns:read", "campaigns:update",
                "analytics:read", "reports:create", "reports:read",
                "settings:read"
            ],
            UserRole.ANALYST.value: [
                "campaigns:read",
                "analytics:read", "reports:create", "reports:read",
                "settings:read"
            ],
            UserRole.VIEWER.value: [
                "campaigns:read",
                "analytics:read", "reports:read"
            ],
            UserRole.GUEST.value: [
                "campaigns:read"
            ]
        }
        
        return permissions_map.get(role_str, [])

class OrganizationManager:
    """Manages organizations and subscriptions"""
    
    def __init__(self, db: AsyncIOMotorClient, stripe_secret_key: str):
        self.db = db
        self.stripe_secret_key = stripe_secret_key
        stripe.api_key = stripe_secret_key
        self.plan_configs = self._load_plan_configurations()
    
    def _load_plan_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Load subscription plan configurations"""
        return {
            SubscriptionPlan.FREE.value: {
                "max_users": 2,
                "max_campaigns": 5,
                "max_storage_gb": 1,
                "features": ["basic_analytics", "email_support"],
                "price_monthly": 0,
                "price_yearly": 0
            },
            SubscriptionPlan.STARTER.value: {
                "max_users": 5,
                "max_campaigns": 25,
                "max_storage_gb": 10,
                "features": ["advanced_analytics", "campaign_templates", "priority_support"],
                "price_monthly": 29,
                "price_yearly": 290
            },
            SubscriptionPlan.PROFESSIONAL.value: {
                "max_users": 15,
                "max_campaigns": 100,
                "max_storage_gb": 50,
                "features": ["advanced_analytics", "campaign_templates", "ab_testing", "api_access", "priority_support"],
                "price_monthly": 99,
                "price_yearly": 990
            },
            SubscriptionPlan.ENTERPRISE.value: {
                "max_users": 100,
                "max_campaigns": 1000,
                "max_storage_gb": 500,
                "features": ["advanced_analytics", "campaign_templates", "ab_testing", "api_access", "white_label", "dedicated_support", "sso"],
                "price_monthly": 299,
                "price_yearly": 2990
            }
        }
    
    async def create_organization(self, org_data: Dict[str, Any]) -> Organization:
        """Create a new organization"""
        try:
            organization_id = str(uuid.uuid4())
            plan = SubscriptionPlan(org_data.get("subscription_plan", SubscriptionPlan.FREE.value))
            plan_config = self.plan_configs[plan.value]
            
            # Create Stripe customer if not free plan
            stripe_customer_id = None
            if plan != SubscriptionPlan.FREE:
                stripe_customer = stripe.Customer.create(
                    email=org_data["billing_email"],
                    name=org_data["name"],
                    metadata={"organization_id": organization_id}
                )
                stripe_customer_id = stripe_customer.id
            
            # Create organization document
            org_doc = {
                "organization_id": organization_id,
                "name": org_data["name"],
                "domain": org_data.get("domain", ""),
                "subscription_plan": plan.value,
                "subscription_status": SubscriptionStatus.TRIAL.value if plan != SubscriptionPlan.FREE else SubscriptionStatus.ACTIVE.value,
                "max_users": plan_config["max_users"],
                "max_campaigns": plan_config["max_campaigns"],
                "max_storage_gb": plan_config["max_storage_gb"],
                "features": plan_config["features"],
                "billing_info": {
                    "billing_email": org_data["billing_email"],
                    "stripe_customer_id": stripe_customer_id,
                    "payment_method": None,
                    "billing_address": org_data.get("billing_address", {})
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "settings": org_data.get("settings", {})
            }
            
            await self.db.organizations.insert_one(org_doc)
            
            logger.info(f"Created organization {organization_id}")
            
            return Organization(
                organization_id=organization_id,
                name=org_data["name"],
                domain=org_data.get("domain", ""),
                subscription_plan=plan,
                subscription_status=SubscriptionStatus.TRIAL.value if plan != SubscriptionPlan.FREE else SubscriptionStatus.ACTIVE.value,
                max_users=plan_config["max_users"],
                max_campaigns=plan_config["max_campaigns"],
                max_storage_gb=plan_config["max_storage_gb"],
                features=plan_config["features"],
                billing_info=org_doc["billing_info"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                settings=org_data.get("settings", {})
            )
            
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            raise
    
    async def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        try:
            org_doc = await self.db.organizations.find_one({"organization_id": organization_id})
            if not org_doc:
                return None
            
            return Organization(
                organization_id=org_doc["organization_id"],
                name=org_doc["name"],
                domain=org_doc["domain"],
                subscription_plan=SubscriptionPlan(org_doc["subscription_plan"]),
                subscription_status=SubscriptionStatus(org_doc["subscription_status"]),
                max_users=org_doc["max_users"],
                max_campaigns=org_doc["max_campaigns"],
                max_storage_gb=org_doc["max_storage_gb"],
                features=org_doc["features"],
                billing_info=org_doc["billing_info"],
                created_at=datetime.fromisoformat(org_doc["created_at"]),
                updated_at=datetime.fromisoformat(org_doc["updated_at"]),
                settings=org_doc.get("settings", {})
            )
            
        except Exception as e:
            logger.error(f"Error getting organization {organization_id}: {e}")
            raise
    
    async def update_subscription(self, organization_id: str, new_plan: SubscriptionPlan) -> Organization:
        """Update organization subscription plan"""
        try:
            org = await self.get_organization(organization_id)
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            plan_config = self.plan_configs[new_plan.value]
            
            # Update organization document
            updates = {
                "subscription_plan": new_plan.value,
                "max_users": plan_config["max_users"],
                "max_campaigns": plan_config["max_campaigns"],
                "max_storage_gb": plan_config["max_storage_gb"],
                "features": plan_config["features"],
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.db.organizations.update_one(
                {"organization_id": organization_id},
                {"$set": updates}
            )
            
            logger.info(f"Updated subscription for organization {organization_id} to {new_plan.value}")
            
            # Return updated organization
            return await self.get_organization(organization_id)
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise

class TeamCollaborationManager:
    """Manages team collaboration and invitations"""
    
    def __init__(self, db: AsyncIOMotorClient, email_service: EmailService):
        self.db = db
        self.email_service = email_service
    
    async def invite_user(self, organization_id: str, email: str, role: UserRole, invited_by: str) -> TeamInvitation:
        """Invite a user to join the organization"""
        try:
            invitation_id = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            # Create invitation document
            invitation_doc = {
                "invitation_id": invitation_id,
                "organization_id": organization_id,
                "email": email,
                "role": role.value,
                "invited_by": invited_by,
                "status": InvitationStatus.PENDING.value,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "accepted_at": None
            }
            
            await self.db.team_invitations.insert_one(invitation_doc)
            
            # Send invitation email
            await self.email_service.send_invitation_email(email, organization_id, role)
            
            logger.info(f"Sent invitation {invitation_id} to {email}")
            
            return TeamInvitation(
                invitation_id=invitation_id,
                organization_id=organization_id,
                email=email,
                role=role,
                invited_by=invited_by,
                status=InvitationStatus.PENDING,
                expires_at=expires_at,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error inviting user: {e}")
            raise
    
    async def accept_invitation(self, invitation_id: str, user_data: Dict[str, Any]) -> User:
        """Accept team invitation and create user"""
        try:
            # Get invitation
            invitation_doc = await self.db.team_invitations.find_one({"invitation_id": invitation_id})
            if not invitation_doc:
                raise ValueError(f"Invitation {invitation_id} not found")
            
            if invitation_doc["status"] != InvitationStatus.PENDING.value:
                raise ValueError("Invitation already processed")
            
            if datetime.fromisoformat(invitation_doc["expires_at"]) < datetime.utcnow():
                raise ValueError("Invitation expired")
            
            # Create user
            user_manager = UserManager(self.db, "jwt_secret")  # In production, get from config
            user_data.update({
                "role": UserRole(invitation_doc["role"]),
                "organization_id": invitation_doc["organization_id"]
            })
            
            user = await user_manager.create_user(user_data)
            
            # Update invitation status
            await self.db.team_invitations.update_one(
                {"invitation_id": invitation_id},
                {
                    "$set": {
                        "status": InvitationStatus.ACCEPTED.value,
                        "accepted_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            logger.info(f"User {user.user_id} accepted invitation {invitation_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            raise
    
    async def get_pending_invitations(self, organization_id: str) -> List[TeamInvitation]:
        """Get pending invitations for organization"""
        try:
            invitation_docs = await self.db.team_invitations.find({
                "organization_id": organization_id,
                "status": InvitationStatus.PENDING.value
            }).to_list(length=None)
            
            invitations = []
            for doc in invitation_docs:
                invitations.append(TeamInvitation(
                    invitation_id=doc["invitation_id"],
                    organization_id=doc["organization_id"],
                    email=doc["email"],
                    role=UserRole(doc["role"]),
                    invited_by=doc["invited_by"],
                    status=InvitationStatus(doc["status"]),
                    expires_at=datetime.fromisoformat(doc["expires_at"]),
                    created_at=datetime.fromisoformat(doc["created_at"]),
                    accepted_at=datetime.fromisoformat(doc["accepted_at"]) if doc.get("accepted_at") else None
                ))
            
            return invitations
            
        except Exception as e:
            logger.error(f"Error getting pending invitations: {e}")
            raise

class UsageQuotaManager:
    """Manages usage quotas and limits"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def check_quota(self, organization_id: str, quota_type: str) -> Dict[str, Any]:
        """Check if organization has quota available"""
        try:
            quota_doc = await self.db.usage_quotas.find_one({
                "organization_id": organization_id,
                "quota_type": quota_type
            })
            
            if not quota_doc:
                # Create default quota
                await self._create_default_quota(organization_id, quota_type)
                quota_doc = await self.db.usage_quotas.find_one({
                    "organization_id": organization_id,
                    "quota_type": quota_type
                })
            
            # Check if quota needs reset
            if self._should_reset_quota(quota_doc):
                await self._reset_quota(quota_doc["quota_id"])
                quota_doc["current_usage"] = 0
                quota_doc["last_reset"] = datetime.utcnow().isoformat()
            
            return {
                "quota_type": quota_type,
                "current_usage": quota_doc["current_usage"],
                "limit": quota_doc["limit"],
                "remaining": quota_doc["limit"] - quota_doc["current_usage"],
                "is_available": quota_doc["current_usage"] < quota_doc["limit"],
                "reset_period": quota_doc["reset_period"],
                "last_reset": quota_doc["last_reset"]
            }
            
        except Exception as e:
            logger.error(f"Error checking quota: {e}")
            raise
    
    async def increment_quota(self, organization_id: str, quota_type: str, amount: int = 1) -> bool:
        """Increment quota usage"""
        try:
            quota_info = await self.check_quota(organization_id, quota_type)
            
            if not quota_info["is_available"]:
                return False
            
            await self.db.usage_quotas.update_one(
                {
                    "organization_id": organization_id,
                    "quota_type": quota_type
                },
                {
                    "$inc": {"current_usage": amount},
                    "$set": {"updated_at": datetime.utcnow().isoformat()}
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing quota: {e}")
            raise
    
    async def _create_default_quota(self, organization_id: str, quota_type: str):
        """Create default quota for organization"""
        try:
            # Get organization to determine limits
            org_doc = await self.db.organizations.find_one({"organization_id": organization_id})
            if not org_doc:
                raise ValueError(f"Organization {organization_id} not found")
            
            quota_limits = {
                "users": org_doc["max_users"],
                "campaigns": org_doc["max_campaigns"],
                "storage_gb": org_doc["max_storage_gb"],
                "api_calls": 10000,  # Default API calls per month
                "reports": 100  # Default reports per month
            }
            
            quota_doc = {
                "quota_id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "quota_type": quota_type,
                "current_usage": 0,
                "limit": quota_limits.get(quota_type, 1000),
                "reset_period": "monthly",
                "last_reset": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.db.usage_quotas.insert_one(quota_doc)
            
        except Exception as e:
            logger.error(f"Error creating default quota: {e}")
            raise
    
    def _should_reset_quota(self, quota_doc: Dict[str, Any]) -> bool:
        """Check if quota should be reset"""
        last_reset = datetime.fromisoformat(quota_doc["last_reset"])
        reset_period = quota_doc["reset_period"]
        
        if reset_period == "monthly":
            return datetime.utcnow() - last_reset >= timedelta(days=30)
        elif reset_period == "weekly":
            return datetime.utcnow() - last_reset >= timedelta(days=7)
        elif reset_period == "daily":
            return datetime.utcnow() - last_reset >= timedelta(days=1)
        
        return False
    
    async def _reset_quota(self, quota_id: str):
        """Reset quota usage"""
        try:
            await self.db.usage_quotas.update_one(
                {"quota_id": quota_id},
                {
                    "$set": {
                        "current_usage": 0,
                        "last_reset": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error resetting quota: {e}")
            raise

class EmailService:
    """Email service for notifications and invitations"""
    
    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    async def send_invitation_email(self, email: str, organization_id: str, role: UserRole):
        """Send team invitation email"""
        try:
            # Create email content
            subject = f"Invitation to join OmniFy Cloud Connect"
            body = f"""
            You have been invited to join OmniFy Cloud Connect as a {role.value}.
            
            Click the link below to accept the invitation:
            https://app.omnify.com/invite/{organization_id}
            
            This invitation will expire in 7 days.
            
            Best regards,
            The OmniFy Team
            """
            
            await self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Error sending invitation email: {e}")
            raise
    
    async def _send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # In production, use async SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

class PasswordManager:
    """Password management utilities"""
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

class MultiTenancyService:
    """Main service for multi-tenancy and user management"""
    
    def __init__(self, db: AsyncIOMotorClient, jwt_secret: str, stripe_secret_key: str, email_config: Dict[str, str]):
        self.db = db
        self.user_manager = UserManager(db, jwt_secret)
        self.organization_manager = OrganizationManager(db, stripe_secret_key)
        self.email_service = EmailService(
            email_config["smtp_host"],
            email_config["smtp_port"],
            email_config["smtp_user"],
            email_config["smtp_password"]
        )
        self.team_manager = TeamCollaborationManager(db, self.email_service)
        self.quota_manager = UsageQuotaManager(db)
    
    async def create_organization_with_admin(self, org_data: Dict[str, Any], admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create organization with admin user"""
        try:
            # Create organization
            organization = await self.organization_manager.create_organization(org_data)
            
            # Create admin user
            admin_data["role"] = UserRole.ORG_ADMIN
            admin_data["organization_id"] = organization.organization_id
            admin = await self.user_manager.create_user(admin_data)
            
            # Initialize quotas
            await self.quota_manager._create_default_quota(organization.organization_id, "users")
            await self.quota_manager._create_default_quota(organization.organization_id, "campaigns")
            await self.quota_manager._create_default_quota(organization.organization_id, "storage_gb")
            
            return {
                "organization": organization,
                "admin_user": admin,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Error creating organization with admin: {e}")
            raise
    
    async def invite_team_member(self, organization_id: str, email: str, role: UserRole, invited_by: str) -> TeamInvitation:
        """Invite team member to organization"""
        return await self.team_manager.invite_user(organization_id, email, role, invited_by)
    
    async def check_organization_quota(self, organization_id: str, quota_type: str) -> Dict[str, Any]:
        """Check organization quota"""
        return await self.quota_manager.check_quota(organization_id, quota_type)
    
    async def get_organization_overview(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive organization overview"""
        try:
            organization = await self.organization_manager.get_organization(organization_id)
            users = await self.user_manager.get_organization_users(organization_id)
            invitations = await self.team_manager.get_pending_invitations(organization_id)
            
            # Get quota usage
            quotas = {}
            quota_types = ["users", "campaigns", "storage_gb", "api_calls", "reports"]
            for quota_type in quota_types:
                quotas[quota_type] = await self.quota_manager.check_quota(organization_id, quota_type)
            
            return {
                "organization": organization,
                "users": users,
                "pending_invitations": invitations,
                "quotas": quotas,
                "summary": {
                    "total_users": len(users),
                    "active_users": len([u for u in users if u.is_active]),
                    "pending_invitations": len(invitations),
                    "subscription_plan": organization.subscription_plan.value,
                    "subscription_status": organization.subscription_status.value
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting organization overview: {e}")
            raise

# Global instance
multi_tenancy_service = None

def get_multi_tenancy_service(db: AsyncIOMotorClient, jwt_secret: str, stripe_secret_key: str, email_config: Dict[str, str]) -> MultiTenancyService:
    """Get multi-tenancy service instance"""
    global multi_tenancy_service
    if multi_tenancy_service is None:
        multi_tenancy_service = MultiTenancyService(db, jwt_secret, stripe_secret_key, email_config)
    return multi_tenancy_service
