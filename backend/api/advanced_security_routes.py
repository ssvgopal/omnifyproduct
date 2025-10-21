"""
Advanced Security Features API Routes
Production-grade API endpoints for SSO, advanced authentication, and compliance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import redis

from services.advanced_security_service import (
    get_advanced_security_service, AdvancedSecurityService,
    AuthenticationMethod, ComplianceStandard, SecurityLevel, AuditEventType
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class SecurityPolicyRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field("", description="Policy description")
    compliance_standards: Optional[List[str]] = Field([], description="Compliance standards")
    password_policy: Optional[Dict[str, Any]] = Field({}, description="Password policy")
    mfa_requirements: Optional[Dict[str, Any]] = Field({}, description="MFA requirements")
    session_policy: Optional[Dict[str, Any]] = Field({}, description="Session policy")
    data_retention_policy: Optional[Dict[str, Any]] = Field({}, description="Data retention policy")
    access_control_policy: Optional[Dict[str, Any]] = Field({}, description="Access control policy")

class UserSecurityProfileRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    password: str = Field(..., description="User password")
    security_policy_id: str = Field(..., description="Security policy ID")

class MFAEnableRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    method: str = Field(..., description="MFA method")

class MFAVerifyRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    token: str = Field(..., description="MFA token")

class SAMLConfigRequest(BaseModel):
    entity_id: str = Field(..., description="SAML entity ID")
    sso_url: str = Field(..., description="SAML SSO URL")
    slo_url: Optional[str] = Field(None, description="SAML SLO URL")
    x509_cert: str = Field(..., description="X.509 certificate")
    name_id_format: Optional[str] = Field("urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress", description="Name ID format")
    attribute_mapping: Optional[Dict[str, Any]] = Field({}, description="Attribute mapping")

class OIDCConfigRequest(BaseModel):
    client_id: str = Field(..., description="OIDC client ID")
    client_secret: str = Field(..., description="OIDC client secret")
    issuer_url: str = Field(..., description="OIDC issuer URL")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI")
    scopes: Optional[List[str]] = Field(["openid", "profile", "email"], description="OIDC scopes")
    attribute_mapping: Optional[Dict[str, Any]] = Field({}, description="Attribute mapping")

class OAuth2ConfigRequest(BaseModel):
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    authorization_url: str = Field(..., description="Authorization URL")
    token_url: str = Field(..., description="Token URL")
    user_info_url: Optional[str] = Field(None, description="User info URL")
    scopes: Optional[List[str]] = Field([], description="OAuth2 scopes")
    attribute_mapping: Optional[Dict[str, Any]] = Field({}, description="Attribute mapping")

class ComplianceReportRequest(BaseModel):
    standard: str = Field(..., description="Compliance standard")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")

class SecurityPolicyResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    compliance_standards: List[str]
    password_policy: Dict[str, Any]
    mfa_requirements: Dict[str, Any]
    session_policy: Dict[str, Any]
    data_retention_policy: Dict[str, Any]
    access_control_policy: Dict[str, Any]
    created_at: str
    updated_at: str

class UserSecurityProfileResponse(BaseModel):
    user_id: str
    authentication_methods: List[str]
    mfa_enabled: bool
    password_last_changed: str
    failed_login_attempts: int
    account_locked_until: Optional[str]
    security_level: str
    compliance_flags: List[str]
    last_login: Optional[str]
    created_at: str
    updated_at: str

class SecurityDashboardResponse(BaseModel):
    organization_id: str
    security_statistics: Dict[str, Any]
    recent_audit_logs: List[Dict[str, Any]]
    security_policies: List[Dict[str, Any]]
    compliance_standards: List[str]
    authentication_methods: List[str]
    generated_at: str

# Dependency
async def get_security_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedSecurityService:
    # In production, initialize Redis properly
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    return get_advanced_security_service(db, redis_client)

# Security Policy Management
@router.post("/api/security/policies", response_model=SecurityPolicyResponse, summary="Create Security Policy")
async def create_security_policy(
    request: SecurityPolicyRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Create a new security policy.
    Defines security requirements and compliance standards.
    """
    try:
        # Validate compliance standards
        for standard in request.compliance_standards:
            try:
                ComplianceStandard(standard)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid compliance standard: {standard}"
                )
        
        policy_data = {
            "name": request.name,
            "description": request.description,
            "compliance_standards": request.compliance_standards,
            "password_policy": request.password_policy,
            "mfa_requirements": request.mfa_requirements,
            "session_policy": request.session_policy,
            "data_retention_policy": request.data_retention_policy,
            "access_control_policy": request.access_control_policy
        }
        
        policy_id = await security_service.create_security_policy(policy_data)
        
        # Get created policy
        policy_doc = await security_service.db.security_policies.find_one({"policy_id": policy_id})
        
        return SecurityPolicyResponse(
            policy_id=policy_doc["policy_id"],
            name=policy_doc["name"],
            description=policy_doc["description"],
            compliance_standards=policy_doc["compliance_standards"],
            password_policy=policy_doc["password_policy"],
            mfa_requirements=policy_doc["mfa_requirements"],
            session_policy=policy_doc["session_policy"],
            data_retention_policy=policy_doc["data_retention_policy"],
            access_control_policy=policy_doc["access_control_policy"],
            created_at=policy_doc["created_at"],
            updated_at=policy_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating security policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create security policy"
        )

@router.get("/api/security/policies", response_model=List[SecurityPolicyResponse], summary="List Security Policies")
async def list_security_policies(
    compliance_standard: Optional[str] = Query(None, description="Filter by compliance standard"),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    List security policies with filtering options.
    Returns policy definitions and configurations.
    """
    try:
        # Build query
        query = {}
        if compliance_standard:
            query["compliance_standards"] = compliance_standard
        
        # Get policies
        policies = await security_service.db.security_policies.find(query).sort("created_at", -1).to_list(length=None)
        
        policy_responses = []
        for policy in policies:
            policy_responses.append(SecurityPolicyResponse(
                policy_id=policy["policy_id"],
                name=policy["name"],
                description=policy["description"],
                compliance_standards=policy["compliance_standards"],
                password_policy=policy["password_policy"],
                mfa_requirements=policy["mfa_requirements"],
                session_policy=policy["session_policy"],
                data_retention_policy=policy["data_retention_policy"],
                access_control_policy=policy["access_control_policy"],
                created_at=policy["created_at"],
                updated_at=policy["updated_at"]
            ))
        
        return policy_responses
        
    except Exception as e:
        logger.error(f"Error listing security policies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list security policies"
        )

# User Security Profile Management
@router.post("/api/security/profiles", response_model=UserSecurityProfileResponse, summary="Create User Security Profile")
async def create_user_security_profile(
    request: UserSecurityProfileRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Create user security profile.
    Sets up authentication and security settings for a user.
    """
    try:
        user_id = await security_service.create_user_security_profile(
            request.user_id, request.password, request.security_policy_id
        )
        
        # Get created profile
        profile_doc = await security_service.db.user_security_profiles.find_one({"user_id": user_id})
        
        return UserSecurityProfileResponse(
            user_id=profile_doc["user_id"],
            authentication_methods=profile_doc["authentication_methods"],
            mfa_enabled=profile_doc["mfa_enabled"],
            password_last_changed=profile_doc["password_last_changed"],
            failed_login_attempts=profile_doc["failed_login_attempts"],
            account_locked_until=profile_doc.get("account_locked_until"),
            security_level=profile_doc["security_level"],
            compliance_flags=profile_doc["compliance_flags"],
            last_login=profile_doc.get("last_login"),
            created_at=profile_doc["created_at"],
            updated_at=profile_doc["updated_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user security profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user security profile"
        )

@router.get("/api/security/profiles/{user_id}", response_model=UserSecurityProfileResponse, summary="Get User Security Profile")
async def get_user_security_profile(
    user_id: str,
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Get user security profile.
    Returns security settings and status for a user.
    """
    try:
        profile = await security_service.db.user_security_profiles.find_one({"user_id": user_id})
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User security profile not found"
            )
        
        return UserSecurityProfileResponse(
            user_id=profile["user_id"],
            authentication_methods=profile["authentication_methods"],
            mfa_enabled=profile["mfa_enabled"],
            password_last_changed=profile["password_last_changed"],
            failed_login_attempts=profile["failed_login_attempts"],
            account_locked_until=profile.get("account_locked_until"),
            security_level=profile["security_level"],
            compliance_flags=profile["compliance_flags"],
            last_login=profile.get("last_login"),
            created_at=profile["created_at"],
            updated_at=profile["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user security profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user security profile"
        )

# Multi-Factor Authentication
@router.post("/api/security/mfa/enable", summary="Enable MFA")
async def enable_mfa(
    request: MFAEnableRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Enable multi-factor authentication for a user.
    Generates MFA secrets and setup instructions.
    """
    try:
        # Validate MFA method
        try:
            method = AuthenticationMethod(request.method)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MFA method: {request.method}"
            )
        
        result = await security_service.enable_mfa(request.user_id, method)
        
        return {
            "user_id": request.user_id,
            "method": request.method,
            "secret": result["secret"],
            "qr_code": result["qr_code"],
            "backup_codes": result["backup_codes"],
            "message": "MFA enabled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable MFA"
        )

@router.post("/api/security/mfa/verify", summary="Verify MFA Token")
async def verify_mfa_token(
    request: MFAVerifyRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Verify MFA token for authentication.
    Validates TOTP tokens and backup codes.
    """
    try:
        is_valid = await security_service.verify_mfa(request.user_id, request.token)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token"
            )
        
        return {
            "user_id": request.user_id,
            "verified": True,
            "message": "MFA token verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA token"
        )

# Single Sign-On Configuration
@router.post("/api/security/sso/saml", summary="Configure SAML SSO")
async def configure_saml_sso(
    request: SAMLConfigRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Configure SAML Single Sign-On.
    Sets up SAML identity provider integration.
    """
    try:
        config_data = {
            "entity_id": request.entity_id,
            "sso_url": request.sso_url,
            "slo_url": request.slo_url,
            "x509_cert": request.x509_cert,
            "name_id_format": request.name_id_format,
            "attribute_mapping": request.attribute_mapping
        }
        
        config_id = await security_service.sso_manager.configure_saml(config_data)
        
        return {
            "config_id": config_id,
            "type": "saml",
            "entity_id": request.entity_id,
            "sso_url": request.sso_url,
            "message": "SAML SSO configured successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error configuring SAML SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure SAML SSO"
        )

@router.post("/api/security/sso/oidc", summary="Configure OIDC SSO")
async def configure_oidc_sso(
    request: OIDCConfigRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Configure OpenID Connect Single Sign-On.
    Sets up OIDC identity provider integration.
    """
    try:
        config_data = {
            "client_id": request.client_id,
            "client_secret": request.client_secret,
            "issuer_url": request.issuer_url,
            "redirect_uri": request.redirect_uri,
            "scopes": request.scopes,
            "attribute_mapping": request.attribute_mapping
        }
        
        config_id = await security_service.sso_manager.configure_oidc(config_data)
        
        return {
            "config_id": config_id,
            "type": "oidc",
            "client_id": request.client_id,
            "issuer_url": request.issuer_url,
            "message": "OIDC SSO configured successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error configuring OIDC SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure OIDC SSO"
        )

@router.post("/api/security/sso/oauth2", summary="Configure OAuth2 SSO")
async def configure_oauth2_sso(
    request: OAuth2ConfigRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Configure OAuth2 Single Sign-On.
    Sets up OAuth2 identity provider integration.
    """
    try:
        config_data = {
            "client_id": request.client_id,
            "client_secret": request.client_secret,
            "authorization_url": request.authorization_url,
            "token_url": request.token_url,
            "user_info_url": request.user_info_url,
            "scopes": request.scopes,
            "attribute_mapping": request.attribute_mapping
        }
        
        config_id = await security_service.sso_manager.configure_oauth2(config_data)
        
        return {
            "config_id": config_id,
            "type": "oauth2",
            "client_id": request.client_id,
            "authorization_url": request.authorization_url,
            "message": "OAuth2 SSO configured successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error configuring OAuth2 SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure OAuth2 SSO"
        )

# Audit and Compliance
@router.get("/api/security/audit-logs", summary="Get Audit Logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    compliance_flags: Optional[str] = Query(None, description="Comma-separated compliance flags"),
    limit: int = Query(100, description="Number of logs to return"),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Get audit logs with filtering options.
    Returns compliance audit trail and security events.
    """
    try:
        # Build filters
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if event_type:
            filters["event_type"] = event_type
        if resource_type:
            filters["resource_type"] = resource_type
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if compliance_flags:
            filters["compliance_flags"] = compliance_flags.split(",")
        
        logs = await security_service.compliance_manager.get_audit_logs(filters, limit)
        
        return {
            "logs": logs,
            "total_count": len(logs),
            "filters_applied": filters
        }
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get audit logs"
        )

@router.post("/api/security/compliance/report", summary="Generate Compliance Report")
async def generate_compliance_report(
    request: ComplianceReportRequest = Body(...),
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Generate compliance report for specified standard.
    Returns detailed compliance analysis and recommendations.
    """
    try:
        # Validate compliance standard
        try:
            standard = ComplianceStandard(request.standard)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid compliance standard: {request.standard}"
            )
        
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        report = await security_service.compliance_manager.generate_compliance_report(
            standard, start_date, end_date
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate compliance report"
        )

# Dashboard Endpoint
@router.get("/api/security/dashboard/{organization_id}", response_model=SecurityDashboardResponse, summary="Get Security Dashboard")
async def get_security_dashboard(
    organization_id: str,
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Get comprehensive security dashboard.
    Returns security statistics, policies, and recent activity.
    """
    try:
        dashboard = await security_service.get_security_dashboard(organization_id)
        
        return SecurityDashboardResponse(
            organization_id=dashboard["organization_id"],
            security_statistics=dashboard["security_statistics"],
            recent_audit_logs=dashboard["recent_audit_logs"],
            security_policies=dashboard["security_policies"],
            compliance_standards=dashboard["compliance_standards"],
            authentication_methods=dashboard["authentication_methods"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting security dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security dashboard"
        )

# Security System Health Check
@router.get("/api/security/health", summary="Security System Health Check")
async def security_health_check(
    security_service: AdvancedSecurityService = Depends(get_security_service)
):
    """
    Check the health of the security system.
    Returns system status and capabilities.
    """
    try:
        # Check database connection
        await security_service.db.admin.command('ping')
        
        # Get system statistics
        stats = {
            "total_policies": await security_service.db.security_policies.count_documents({}),
            "total_profiles": await security_service.db.user_security_profiles.count_documents({}),
            "mfa_enabled_users": await security_service.db.user_security_profiles.count_documents({"mfa_enabled": True}),
            "total_audit_logs": await security_service.db.audit_logs.count_documents({}),
            "locked_accounts": await security_service.db.user_security_profiles.count_documents({
                "account_locked_until": {"$gt": datetime.utcnow().isoformat()}
            })
        }
        
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "password_manager": "healthy",
                "mfa_manager": "healthy",
                "sso_manager": "healthy",
                "compliance_manager": "healthy",
                "encryption": "healthy"
            },
            "statistics": stats,
            "capabilities": {
                "password_management": True,
                "multi_factor_authentication": True,
                "single_sign_on": True,
                "audit_logging": True,
                "compliance_reporting": True,
                "security_policies": True,
                "encryption": True,
                "access_control": True
            },
            "supported_authentication_methods": [am.value for am in AuthenticationMethod],
            "supported_compliance_standards": [cs.value for cs in ComplianceStandard],
            "supported_security_levels": [sl.value for sl in SecurityLevel],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking security health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
