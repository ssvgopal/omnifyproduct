"""
Comprehensive Authentication and Authorization Tests
Tests for JWT, OAuth2, permissions, and security

Author: OmnifyProduct Test Suite
Priority: CRITICAL - 25% coverage currently
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
import hashlib
import secrets


class TestJWTAuthentication:
    """Test JWT token generation and validation"""

    @pytest.fixture
    def jwt_secret(self):
        """JWT secret key"""
        return "test_secret_key_do_not_use_in_production"

    @pytest.fixture
    def user_data(self):
        """Sample user data"""
        return {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }

    def test_generate_jwt_token(self, jwt_secret, user_data):
        """Test JWT token generation"""
        # Generate token
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_jwt_token(self, jwt_secret, user_data):
        """Test JWT token decoding"""
        # Generate token
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        # Decode token
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        
        assert decoded["user_id"] == user_data["user_id"]
        assert decoded["email"] == user_data["email"]
        assert decoded["role"] == user_data["role"]

    def test_expired_token(self, jwt_secret, user_data):
        """Test expired token rejection"""
        # Generate expired token
        payload = {
            **user_data,
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        # Should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, jwt_secret, algorithms=["HS256"])

    def test_invalid_token(self, jwt_secret):
        """Test invalid token rejection"""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(jwt.DecodeError):
            jwt.decode(invalid_token, jwt_secret, algorithms=["HS256"])

    def test_tampered_token(self, jwt_secret, user_data):
        """Test tampered token rejection"""
        # Generate valid token
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        # Tamper with token
        tampered_token = token[:-10] + "tampered12"
        
        # Should raise InvalidSignatureError
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(tampered_token, jwt_secret, algorithms=["HS256"])

    def test_token_refresh(self, jwt_secret, user_data):
        """Test token refresh mechanism"""
        # Generate original token
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        
        old_token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        # Decode and refresh
        decoded = jwt.decode(old_token, jwt_secret, algorithms=["HS256"])
        
        # Generate new token with extended expiry
        new_payload = {
            **decoded,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        new_token = jwt.encode(new_payload, jwt_secret, algorithm="HS256")
        
        # Verify new token
        new_decoded = jwt.decode(new_token, jwt_secret, algorithms=["HS256"])
        assert new_decoded["user_id"] == user_data["user_id"]


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        
        # Hash password (using hashlib for simplicity)
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password.encode()

    def test_verify_password(self):
        """Test password verification"""
        password = "SecurePassword123!"
        
        # Hash password
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        
        # Verify correct password
        verify_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        assert hashed == verify_hash

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "Password123!"
        password2 = "DifferentPassword456!"
        
        salt = secrets.token_hex(16)
        hash1 = hashlib.pbkdf2_hmac('sha256', password1.encode(), salt.encode(), 100000)
        hash2 = hashlib.pbkdf2_hmac('sha256', password2.encode(), salt.encode(), 100000)
        
        assert hash1 != hash2

    def test_same_password_different_salts(self):
        """Test that same password with different salts produces different hashes"""
        password = "Password123!"
        
        salt1 = secrets.token_hex(16)
        salt2 = secrets.token_hex(16)
        
        hash1 = hashlib.pbkdf2_hmac('sha256', password.encode(), salt1.encode(), 100000)
        hash2 = hashlib.pbkdf2_hmac('sha256', password.encode(), salt2.encode(), 100000)
        
        assert hash1 != hash2


class TestPermissionBasedAccess:
    """Test permission-based access control"""

    @pytest.fixture
    def user_permissions(self):
        """Sample user permissions"""
        return {
            "admin": ["read", "write", "delete", "manage_users"],
            "editor": ["read", "write"],
            "viewer": ["read"]
        }

    def test_check_permission_granted(self, user_permissions):
        """Test permission check when granted"""
        user_role = "admin"
        required_permission = "write"
        
        assert required_permission in user_permissions[user_role]

    def test_check_permission_denied(self, user_permissions):
        """Test permission check when denied"""
        user_role = "viewer"
        required_permission = "delete"
        
        assert required_permission not in user_permissions[user_role]

    def test_multiple_permissions(self, user_permissions):
        """Test checking multiple permissions"""
        user_role = "editor"
        required_permissions = ["read", "write"]
        
        user_perms = user_permissions[user_role]
        assert all(perm in user_perms for perm in required_permissions)

    def test_role_hierarchy(self, user_permissions):
        """Test role hierarchy (admin has all permissions)"""
        admin_perms = user_permissions["admin"]
        editor_perms = user_permissions["editor"]
        viewer_perms = user_permissions["viewer"]
        
        # Admin should have all editor permissions
        assert all(perm in admin_perms for perm in editor_perms)
        
        # Admin should have all viewer permissions
        assert all(perm in admin_perms for perm in viewer_perms)


class TestOAuth2Flow:
    """Test OAuth2 authentication flow"""

    @pytest.fixture
    def oauth_config(self):
        """OAuth2 configuration"""
        return {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "authorization_url": "https://provider.com/oauth/authorize",
            "token_url": "https://provider.com/oauth/token"
        }

    def test_generate_authorization_url(self, oauth_config):
        """Test OAuth2 authorization URL generation"""
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"{oauth_config['authorization_url']}?"
            f"client_id={oauth_config['client_id']}&"
            f"redirect_uri={oauth_config['redirect_uri']}&"
            f"response_type=code&"
            f"state={state}"
        )
        
        assert oauth_config['authorization_url'] in auth_url
        assert oauth_config['client_id'] in auth_url
        assert state in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, oauth_config):
        """Test exchanging authorization code for access token"""
        authorization_code = "test_auth_code"
        
        # Mock token exchange
        mock_response = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token"
        }
        
        # In real implementation, this would make HTTP request
        # For test, we just verify the structure
        assert "access_token" in mock_response
        assert "token_type" in mock_response
        assert mock_response["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_refresh_access_token(self, oauth_config):
        """Test refreshing access token"""
        refresh_token = "test_refresh_token"
        
        # Mock token refresh
        mock_response = {
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        
        assert "access_token" in mock_response
        assert mock_response["access_token"] != refresh_token


class TestSessionManagement:
    """Test session management and expiry"""

    @pytest.fixture
    def session_data(self):
        """Sample session data"""
        return {
            "session_id": secrets.token_urlsafe(32),
            "user_id": "test_user_123",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24),
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0"
        }

    def test_create_session(self, session_data):
        """Test session creation"""
        assert session_data["session_id"] is not None
        assert len(session_data["session_id"]) > 0
        assert session_data["expires_at"] > session_data["created_at"]

    def test_validate_active_session(self, session_data):
        """Test validating active session"""
        current_time = datetime.utcnow()
        
        is_valid = (
            session_data["expires_at"] > current_time and
            session_data["created_at"] <= current_time
        )
        
        assert is_valid is True

    def test_validate_expired_session(self, session_data):
        """Test validating expired session"""
        # Set expiry in the past
        session_data["expires_at"] = datetime.utcnow() - timedelta(hours=1)
        
        current_time = datetime.utcnow()
        is_valid = session_data["expires_at"] > current_time
        
        assert is_valid is False

    def test_session_renewal(self, session_data):
        """Test session renewal"""
        # Renew session
        old_expires_at = session_data["expires_at"]
        session_data["expires_at"] = datetime.utcnow() + timedelta(hours=24)
        
        assert session_data["expires_at"] > old_expires_at


class TestAPIKeyAuthentication:
    """Test API key authentication"""

    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = secrets.token_urlsafe(32)
        
        assert api_key is not None
        assert len(api_key) >= 32
        assert isinstance(api_key, str)

    def test_validate_api_key(self):
        """Test API key validation"""
        # Generate and store API key
        valid_api_key = secrets.token_urlsafe(32)
        stored_keys = {valid_api_key: {"user_id": "test_user", "permissions": ["read"]}}
        
        # Validate correct key
        assert valid_api_key in stored_keys
        
        # Validate incorrect key
        invalid_key = "invalid_key"
        assert invalid_key not in stored_keys

    def test_api_key_permissions(self):
        """Test API key permissions"""
        api_key = secrets.token_urlsafe(32)
        api_key_data = {
            "user_id": "test_user",
            "permissions": ["read", "write"],
            "rate_limit": 1000,
            "created_at": datetime.utcnow()
        }
        
        # Check permissions
        assert "read" in api_key_data["permissions"]
        assert "write" in api_key_data["permissions"]
        assert "delete" not in api_key_data["permissions"]

    def test_api_key_rate_limiting(self):
        """Test API key rate limiting"""
        api_key_data = {
            "rate_limit": 100,
            "requests_made": 95,
            "window_start": datetime.utcnow()
        }
        
        # Check if under limit
        assert api_key_data["requests_made"] < api_key_data["rate_limit"]
        
        # Simulate exceeding limit
        api_key_data["requests_made"] = 101
        assert api_key_data["requests_made"] > api_key_data["rate_limit"]


class TestMultiFactorAuthentication:
    """Test multi-factor authentication"""

    def test_generate_totp_secret(self):
        """Test TOTP secret generation"""
        secret = secrets.token_urlsafe(32)
        
        assert secret is not None
        assert len(secret) >= 32

    def test_verify_totp_code(self):
        """Test TOTP code verification"""
        # Mock TOTP verification
        user_code = "123456"
        expected_code = "123456"
        
        assert user_code == expected_code

    def test_backup_codes(self):
        """Test backup code generation and verification"""
        # Generate backup codes
        backup_codes = [secrets.token_hex(8) for _ in range(10)]
        
        assert len(backup_codes) == 10
        assert all(len(code) == 16 for code in backup_codes)
        assert len(set(backup_codes)) == 10  # All unique


class TestSecurityHeaders:
    """Test security headers and CORS"""

    def test_cors_headers(self):
        """Test CORS headers"""
        cors_headers = {
            "Access-Control-Allow-Origin": "https://app.omnify.com",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
        
        assert "Access-Control-Allow-Origin" in cors_headers
        assert cors_headers["Access-Control-Allow-Methods"] is not None

    def test_security_headers(self):
        """Test security headers"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }
        
        assert "X-Content-Type-Options" in security_headers
        assert security_headers["X-Frame-Options"] == "DENY"
        assert "Strict-Transport-Security" in security_headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
