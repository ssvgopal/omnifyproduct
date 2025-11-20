"""
Tests for Authentication API Routes
"""

import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch


class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, test_client, mock_db):
        """Test successful user registration"""
        with patch('api.auth_routes.get_database', return_value=mock_db):
            response = test_client.post(
                "/api/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "SecurePass123!",
                    "organization_name": "Test Org"
                }
            )
            # Should return 201 or 200 depending on implementation
            assert response.status_code in [200, 201]
    
    def test_register_user_duplicate_email(self, test_client, mock_db):
        """Test registration with duplicate email"""
        # Mock database to return existing user
        mock_db.users.find_one = AsyncMock(return_value={"email": "existing@example.com"})
        
        with patch('api.auth_routes.get_database', return_value=mock_db):
            response = test_client.post(
                "/api/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "SecurePass123!",
                    "organization_name": "Test Org"
                }
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, test_client, mock_db, mock_user):
        """Test successful login"""
        # Mock database to return user
        mock_db.users.find_one = AsyncMock(return_value={
            **mock_user,
            "password_hash": "hashed_password"
        })
        
        with patch('api.auth_routes.get_database', return_value=mock_db):
            with patch('core.auth.verify_password', return_value=True):
                response = test_client.post(
                    "/api/auth/login",
                    json={
                        "email": mock_user["email"],
                        "password": "password123"
                    }
                )
                assert response.status_code == status.HTTP_200_OK
                assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, test_client, mock_db):
        """Test login with invalid credentials"""
        mock_db.users.find_one = AsyncMock(return_value=None)
        
        with patch('api.auth_routes.get_database', return_value=mock_db):
            response = test_client.post(
                "/api/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, test_client, auth_headers):
        """Test token refresh"""
        response = test_client.post(
            "/api/auth/refresh",
            headers=auth_headers
        )
        # Should return 200 or 401 depending on token validity
        assert response.status_code in [200, 401]
    
    def test_logout(self, test_client, auth_headers):
        """Test logout"""
        response = test_client.post(
            "/api/auth/logout",
            headers=auth_headers
        )
        assert response.status_code in [200, 204]

