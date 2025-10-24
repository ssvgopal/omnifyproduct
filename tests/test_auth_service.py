# tests/test_auth_service.py
"""
Authentication Service Tests
Tests for user registration, login, JWT tokens, password management, and multi-tenancy
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import jwt
from passlib.context import CryptContext

# Import the auth service
from services.auth_service import AuthService
from models.user_models import User, UserCreate, UserLogin, UserRole, SubscriptionTier, OrganizationCreate


class TestAuthService:
    """Test suite for Authentication Service"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.organizations = AsyncMock()
        mock_db.subscriptions = AsyncMock()
        mock_db.user_invitations = AsyncMock()
        return mock_db

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create AuthService instance for testing"""
        return AuthService(
            db=mock_db,
            jwt_secret="test-secret-key",
            jwt_algorithm="HS256"
        )

    @pytest.fixture
    def test_user_data(self):
        """Test user data"""
        return UserCreate(
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
            organization_name="Test Org"
        )

    @pytest.fixture
    def test_organization_data(self):
        """Test organization data"""
        return OrganizationCreate(
            name="Test Organization",
            slug="test-org"
        )

    # ========== PASSWORD MANAGEMENT TESTS ==========

    def test_password_hashing_bcrypt(self, auth_service):
        """Test password hashing with bcrypt"""
        password = "test123"  # Very short password to avoid bcrypt issues
        
        hashed_password = auth_service.hash_password(password)
        
        assert hashed_password != password
        assert len(hashed_password) > 50  # bcrypt hashes are long
        assert hashed_password.startswith("$2b$")  # bcrypt prefix

    def test_password_verification(self, auth_service):
        """Test password verification"""
        password = "test123"  # Very short password to avoid bcrypt issues
        hashed_password = auth_service.hash_password(password)
        
        # Test correct password
        assert auth_service.verify_password(password, hashed_password) is True
        
        # Test incorrect password
        assert auth_service.verify_password("wrongpassword", hashed_password) is False

    def test_generate_reset_token(self, auth_service):
        """Test password reset token generation"""
        token1 = auth_service.generate_reset_token()
        token2 = auth_service.generate_reset_token()
        
        assert len(token1) > 20  # Should be a reasonable length
        assert token1 != token2  # Should be unique
        assert isinstance(token1, str)

    # ========== JWT TOKEN TESTS ==========

    def test_jwt_token_generation(self, auth_service):
        """Test JWT token generation"""
        user_data = {
            "user_id": "test_user_id",
            "email": "test@example.com",
            "organization_id": "test_org_id",
            "role": "member"
        }
        
        token = auth_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        
        # Decode and verify token
        decoded = auth_service.decode_token(token)
        assert decoded is not None
        assert decoded["user_id"] == "test_user_id"
        assert decoded["email"] == "test@example.com"

    def test_jwt_token_validation(self, auth_service):
        """Test JWT token validation"""
        user_data = {
            "user_id": "test_user_id",
            "organization_id": "test_org_id",
            "role": "member"
        }
        
        token = auth_service.create_access_token(user_data)
        decoded = auth_service.decode_token(token)
        
        assert decoded is not None
        assert decoded["user_id"] == "test_user_id"
        assert decoded["organization_id"] == "test_org_id"
        assert decoded["role"] == "member"
        assert "exp" in decoded  # Should have expiration

    def test_jwt_token_expiration(self, auth_service):
        """Test JWT token expiration"""
        user_data = {"user_id": "test_user_id"}
        
        # Create token with very short expiration
        with patch.object(auth_service, 'jwt_expiration', timedelta(microseconds=1)):
            token = auth_service.create_access_token(user_data)
            # Wait a bit to ensure expiration
            import time
            time.sleep(0.01)
            
            decoded = auth_service.decode_token(token)
            assert decoded is None  # Should be expired

    def test_jwt_token_invalid(self, auth_service):
        """Test JWT token with invalid signature"""
        invalid_token = "invalid.jwt.token"
        
        decoded = auth_service.decode_token(invalid_token)
        assert decoded is None

    # ========== USER ROLE TESTS ==========

    def test_user_role_assignment(self, auth_service):
        """Test user role assignment validation"""
        valid_roles = [UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER]
        
        for role in valid_roles:
            assert role in ["owner", "admin", "manager", "member", "viewer"]

    def test_user_role_validation(self, auth_service):
        """Test user role validation"""
        # Test valid roles
        assert UserRole.OWNER == "owner"
        assert UserRole.ADMIN == "admin"
        assert UserRole.MANAGER == "manager"
        assert UserRole.MEMBER == "member"
        assert UserRole.VIEWER == "viewer"

    # ========== SUBSCRIPTION TESTS ==========

    def test_subscription_tier_validation(self, auth_service):
        """Test subscription tier validation"""
        # Test valid tiers
        assert SubscriptionTier.STARTER == "starter"
        assert SubscriptionTier.PROFESSIONAL == "professional"
        assert SubscriptionTier.ENTERPRISE == "enterprise"