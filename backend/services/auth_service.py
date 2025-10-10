"""
Authentication Service for Omnify Cloud Connect
Handles JWT tokens, user management, and multi-tenant security
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.user_models import (
    User, UserCreate, UserLogin, UserUpdate, PasswordResetRequest,
    Organization, OrganizationCreate, UserRole, SubscriptionTier,
    UserInvitation, UserInvitationCreate, UserInvitationAccept
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and user management service"""

    def __init__(self, db: AsyncIOMotorDatabase, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.db = db
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.jwt_expiration = timedelta(hours=24)

    # ========== PASSWORD MANAGEMENT ==========

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def generate_reset_token(self) -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)

    # ========== JWT TOKEN MANAGEMENT ==========

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.jwt_expiration
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    # ========== USER MANAGEMENT ==========

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing = await self.db.users.find_one({"email": user_data.email})
        if existing:
            raise ValueError("User with this email already exists")

        # Create or get organization
        if user_data.organization_name:
            org = await self._create_organization(
                OrganizationCreate(name=user_data.organization_name),
                owner_email=user_data.email
            )
        else:
            # Handle invitation flow
            org = await self._handle_invitation(user_data.invitation_code, user_data.email)

        # Create user
        user_id = f"user_{secrets.token_hex(16)}"
        hashed_password = self.hash_password(user_data.password)

        user = User(
            user_id=user_id,
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            organization_id=org.organization_id,
            role=UserRole.OWNER if user_data.organization_name else UserRole.MEMBER
        )

        await self.db.users.insert_one(user.dict())
        return user

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password"""
        user_data = await self.db.users.find_one({"email": login_data.email})
        if not user_data:
            return None

        user = User(**user_data)
        if not self.verify_password(login_data.password, user.password_hash):
            return None

        # Update last login
        await self.db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = await self.db.users.find_one({"user_id": user_id})
        return User(**user_data) if user_data else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = await self.db.users.find_one({"email": email})
        return User(**user_data) if user_data else None

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        """Update user information"""
        update_data = {"updated_at": datetime.utcnow()}

        if updates.full_name:
            update_data["full_name"] = updates.full_name
        if updates.preferences:
            update_data["preferences"] = updates.preferences
        if updates.password:
            update_data["password_hash"] = self.hash_password(updates.password)

        result = await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user"""
        result = await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # ========== ORGANIZATION MANAGEMENT ==========

    async def _create_organization(self, org_data: OrganizationCreate, owner_email: str) -> Organization:
        """Create a new organization"""
        org_id = f"org_{secrets.token_hex(16)}"
        slug = org_data.slug or org_data.name.lower().replace(" ", "-").replace("_", "-")

        # Ensure unique slug
        existing = await self.db.organizations.find_one({"slug": slug})
        if existing:
            slug = f"{slug}-{secrets.token_hex(4)}"

        org = Organization(
            organization_id=org_id,
            name=org_data.name,
            slug=slug,
            owner_id="",  # Will be set when user is created
            subscription_tier=SubscriptionTier.STARTER
        )

        await self.db.organizations.insert_one(org.dict())
        return org

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        org_data = await self.db.organizations.find_one({"organization_id": org_id})
        return Organization(**org_data) if org_data else None

    async def update_organization(self, org_id: str, updates: Dict[str, Any]) -> bool:
        """Update organization"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.db.organizations.update_one(
            {"organization_id": org_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    # ========== INVITATION SYSTEM ==========

    async def _handle_invitation(self, invitation_code: Optional[str], email: str) -> Organization:
        """Handle user invitation"""
        if not invitation_code:
            raise ValueError("Organization name or invitation code required")

        # Find invitation
        invitation_data = await self.db.user_invitations.find_one({
            "token": invitation_code,
            "email": email,
            "accepted_at": None,
            "expires_at": {"$gt": datetime.utcnow()}
        })

        if not invitation_data:
            raise ValueError("Invalid or expired invitation")

        invitation = UserInvitation(**invitation_data)

        # Get organization
        org = await self.get_organization(invitation.organization_id)
        if not org:
            raise ValueError("Organization not found")

        return org

    async def create_invitation(self, org_id: str, invitation_data: UserInvitationCreate, invited_by: str) -> UserInvitation:
        """Create user invitation"""
        invitation_id = f"inv_{secrets.token_hex(16)}"
        token = self.generate_reset_token()

        invitation = UserInvitation(
            invitation_id=invitation_id,
            organization_id=org_id,
            email=invitation_data.email,
            role=invitation_data.role,
            invited_by=invited_by,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )

        await self.db.user_invitations.insert_one(invitation.dict())
        return invitation

    async def accept_invitation(self, accept_data: UserInvitationAccept) -> User:
        """Accept user invitation"""
        # Find and validate invitation
        invitation_data = await self.db.user_invitations.find_one({
            "token": accept_data.token,
            "accepted_at": None,
            "expires_at": {"$gt": datetime.utcnow()}
        })

        if not invitation_data:
            raise ValueError("Invalid or expired invitation token")

        invitation = UserInvitation(**invitation_data)

        # Create user
        user_data = UserCreate(
            email=invitation.email,
            password=accept_data.password,
            full_name=accept_data.full_name,
            invitation_code=accept_data.token
        )

        user = await self.create_user(user_data)

        # Mark invitation as accepted
        await self.db.user_invitations.update_one(
            {"invitation_id": invitation.invitation_id},
            {"$set": {"accepted_at": datetime.utcnow()}}
        )

        return user

    # ========== PASSWORD RESET ==========

    async def initiate_password_reset(self, reset_data: PasswordResetRequest) -> str:
        """Initiate password reset"""
        user = await self.get_user_by_email(reset_data.email)
        if not user:
            # Don't reveal if email exists
            return "If the email exists, a reset link has been sent"

        # Generate reset token
        reset_token = self.generate_reset_token()

        # Store reset token (in a real implementation, you'd send an email)
        # For now, just return the token for testing
        await self.db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expires": datetime.utcnow() + timedelta(hours=1)
            }}
        )

        return reset_token  # In production, send via email

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        user_data = await self.db.users.find_one({
            "reset_token": token,
            "reset_token_expires": {"$gt": datetime.utcnow()}
        })

        if not user_data:
            return False

        # Update password
        hashed_password = self.hash_password(new_password)
        await self.db.users.update_one(
            {"user_id": user.user_data["user_id"]},
            {"$set": {
                "password_hash": hashed_password,
                "reset_token": None,
                "reset_token_expires": None,
                "updated_at": datetime.utcnow()
            }}
        )

        return True

    # ========== AUTHENTICATION HELPERS ==========

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.decode_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        return await self.get_user_by_id(user_id)

    async def get_current_organization(self, token: str) -> Optional[Organization]:
        """Get current organization from JWT token"""
        payload = self.decode_token(token)
        if not payload:
            return None

        org_id = payload.get("organization_id")
        if not org_id:
            return None

        return await self.get_organization(org_id)

    async def create_user_token(self, user: User, organization: Organization) -> str:
        """Create JWT token for user"""
        token_data = {
            "user_id": user.user_id,
            "organization_id": organization.organization_id,
            "role": user.role,
            "email": user.email
        }
        return self.create_access_token(token_data)

    # ========== SUBSCRIPTION MANAGEMENT ==========

    async def check_user_limits(self, user: User, organization: Organization) -> Dict[str, Any]:
        """Check if user/org is within subscription limits"""
        # Count current users in organization
        user_count = await self.db.users.count_documents({
            "organization_id": organization.organization_id,
            "is_active": True
        })

        # Count active campaigns
        campaign_count = await self.db.campaigns.count_documents({
            "organization_id": organization.organization_id,
            "status": {"$in": ["active", "draft"]}
        })

        limits = {
            "users": {"current": user_count, "limit": organization.max_users},
            "campaigns": {"current": campaign_count, "limit": organization.max_campaigns}
        }

        return limits
