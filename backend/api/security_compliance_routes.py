"""
Security & Compliance API Routes
Production-grade API endpoints for security, encryption, audit logging, and compliance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.security_compliance_service import (
    get_encryption_manager, get_password_manager, get_audit_logger,
    get_security_policy_manager, get_compliance_manager,
    EncryptionManager, PasswordManager, AuditLogger, SecurityPolicyManager, ComplianceManager,
    SecurityLevel, ComplianceFramework, AuditEventType
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class PasswordValidationRequest(BaseModel):
    password: str = Field(..., description="Password to validate")

class PasswordValidationResponse(BaseModel):
    is_valid: bool
    score: int
    errors: List[str]
    suggestions: List[str]

class EncryptionRequest(BaseModel):
    data: str = Field(..., description="Data to encrypt")

class EncryptionResponse(BaseModel):
    encrypted_data: str
    encryption_method: str
    timestamp: str

class DecryptionRequest(BaseModel):
    encrypted_data: str = Field(..., description="Encrypted data to decrypt")

class DecryptionResponse(BaseModel):
    decrypted_data: str
    decryption_method: str
    timestamp: str

class AuditLogRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    event_type: str = Field(..., description="Event type")
    resource: str = Field(..., description="Resource accessed")
    action: str = Field(..., description="Action performed")
    details: Dict[str, Any] = Field({}, description="Additional details")

class SecurityPolicyRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    compliance_frameworks: List[str] = Field(..., description="Compliance frameworks")
    severity: str = Field(..., description="Security level")

class ComplianceCheckResponse(BaseModel):
    framework: str
    is_compliant: bool
    score: int
    requirements: List[str]
    violations: List[str]
    recommendations: List[str]

# Dependency
async def get_security_service(db: AsyncIOMotorClient = Depends(get_database)) -> tuple:
    master_key = "omnify_master_key_2024"  # In production, this should come from environment
    encryption_manager = get_encryption_manager(master_key)
    password_manager = get_password_manager()
    audit_logger = get_audit_logger(db)
    security_policy_manager = get_security_policy_manager(db)
    compliance_manager = get_compliance_manager(db, audit_logger)
    
    return encryption_manager, password_manager, audit_logger, security_policy_manager, compliance_manager

# Password Security Endpoints
@router.post("/api/security/password/validate", response_model=PasswordValidationResponse, summary="Validate Password Strength")
async def validate_password_strength(
    request: PasswordValidationRequest,
    services: tuple = Depends(get_security_service)
):
    """
    Validate password strength against security policies.
    Returns validation results with score, errors, and suggestions.
    """
    try:
        _, password_manager, _, _, _ = services
        validation_result = password_manager.validate_password_strength(request.password)
        
        return PasswordValidationResponse(
            is_valid=validation_result["is_valid"],
            score=validation_result["score"],
            errors=validation_result["errors"],
            suggestions=validation_result["suggestions"]
        )
    except Exception as e:
        logger.error(f"Error validating password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate password"
        )

@router.post("/api/security/password/hash", summary="Hash Password")
async def hash_password(
    password: str = Body(..., description="Password to hash"),
    services: tuple = Depends(get_security_service)
):
    """
    Hash a password using secure bcrypt algorithm.
    Returns the hashed password for storage.
    """
    try:
        _, password_manager, _, _, _ = services
        hashed_password = password_manager.hash_password(password)
        
        return {
            "hashed_password": hashed_password,
            "algorithm": "bcrypt",
            "rounds": 12,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to hash password"
        )

@router.post("/api/security/password/verify", summary="Verify Password")
async def verify_password(
    password: str = Body(..., description="Plain text password"),
    hashed_password: str = Body(..., description="Hashed password"),
    services: tuple = Depends(get_security_service)
):
    """
    Verify a password against its hash.
    Returns verification result.
    """
    try:
        _, password_manager, _, _, _ = services
        is_valid = password_manager.verify_password(password, hashed_password)
        
        return {
            "is_valid": is_valid,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify password"
        )

@router.get("/api/security/password/generate", summary="Generate Secure Password")
async def generate_secure_password(
    length: int = Query(16, description="Password length"),
    services: tuple = Depends(get_security_service)
):
    """
    Generate a secure random password.
    Returns a cryptographically secure password.
    """
    try:
        _, password_manager, _, _, _ = services
        secure_password = password_manager.generate_secure_password(length)
        
        return {
            "password": secure_password,
            "length": length,
            "strength": "high",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate password"
        )

# Data Encryption Endpoints
@router.post("/api/security/encrypt", response_model=EncryptionResponse, summary="Encrypt Data")
async def encrypt_data(
    request: EncryptionRequest,
    services: tuple = Depends(get_security_service)
):
    """
    Encrypt sensitive data using AES encryption.
    Returns encrypted data for secure storage.
    """
    try:
        encryption_manager, _, _, _, _ = services
        encrypted_data = encryption_manager.encrypt_data(request.data)
        
        return EncryptionResponse(
            encrypted_data=encrypted_data,
            encryption_method="AES-256-GCM",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error encrypting data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt data"
        )

@router.post("/api/security/decrypt", response_model=DecryptionResponse, summary="Decrypt Data")
async def decrypt_data(
    request: DecryptionRequest,
    services: tuple = Depends(get_security_service)
):
    """
    Decrypt previously encrypted data.
    Returns decrypted data for use.
    """
    try:
        encryption_manager, _, _, _, _ = services
        decrypted_data = encryption_manager.decrypt_data(request.encrypted_data)
        
        return DecryptionResponse(
            decrypted_data=decrypted_data,
            decryption_method="AES-256-GCM",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error decrypting data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt data"
        )

@router.post("/api/security/encrypt-pii", summary="Encrypt PII Data")
async def encrypt_pii_data(
    pii_data: Dict[str, Any] = Body(..., description="PII data to encrypt"),
    services: tuple = Depends(get_security_service)
):
    """
    Encrypt personally identifiable information.
    Returns encrypted PII data for compliance.
    """
    try:
        encryption_manager, _, _, _, _ = services
        encrypted_pii = encryption_manager.encrypt_pii(pii_data)
        
        return {
            "encrypted_pii": encrypted_pii,
            "encryption_method": "AES-256-GCM",
            "pii_fields_encrypted": list(encrypted_pii.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error encrypting PII: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt PII data"
        )

@router.post("/api/security/decrypt-pii", summary="Decrypt PII Data")
async def decrypt_pii_data(
    encrypted_pii: Dict[str, Any] = Body(..., description="Encrypted PII data"),
    services: tuple = Depends(get_security_service)
):
    """
    Decrypt previously encrypted PII data.
    Returns decrypted PII data for authorized use.
    """
    try:
        encryption_manager, _, _, _, _ = services
        decrypted_pii = encryption_manager.decrypt_pii(encrypted_pii)
        
        return {
            "decrypted_pii": decrypted_pii,
            "decryption_method": "AES-256-GCM",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error decrypting PII: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt PII data"
        )

# Audit Logging Endpoints
@router.post("/api/security/audit/log", summary="Log Audit Event")
async def log_audit_event(
    request: AuditLogRequest,
    http_request: Request,
    services: tuple = Depends(get_security_service)
):
    """
    Log an audit event for compliance tracking.
    Records user actions, data access, and security events.
    """
    try:
        _, _, audit_logger, _, _ = services
        
        # Get client IP and user agent
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "")
        
        # Create audit log entry
        audit_log = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=request.user_id,
            event_type=AuditEventType(request.event_type),
            resource=request.resource,
            action=request.action,
            details=request.details,
            ip_address=client_ip,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            compliance_tags=[]
        )
        
        log_id = await audit_logger.log_event(audit_log)
        
        return {
            "log_id": log_id,
            "status": "logged",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error logging audit event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log audit event"
        )

@router.get("/api/security/audit/logs", summary="Get Audit Logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    services: tuple = Depends(get_security_service)
):
    """
    Retrieve audit logs with filtering options.
    Returns audit logs for compliance reporting.
    """
    try:
        _, _, audit_logger, _, _ = services
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Parse event type
        event_type_enum = AuditEventType(event_type) if event_type else None
        
        logs = await audit_logger.get_audit_logs(
            user_id=user_id,
            event_type=event_type_enum,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return {
            "logs": logs,
            "total_count": len(logs),
            "filters": {
                "user_id": user_id,
                "event_type": event_type,
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )

@router.post("/api/security/audit/cleanup", summary="Cleanup Old Audit Logs")
async def cleanup_audit_logs(
    services: tuple = Depends(get_security_service)
):
    """
    Clean up old audit logs based on retention policy.
    Removes logs older than the retention period.
    """
    try:
        _, _, audit_logger, _, _ = services
        deleted_count = await audit_logger.cleanup_old_logs()
        
        return {
            "deleted_count": deleted_count,
            "retention_days": audit_logger.retention_days,
            "cleanup_status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error cleaning up audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup audit logs"
        )

# Security Policy Endpoints
@router.get("/api/security/policies", summary="Get Security Policies")
async def get_security_policies(
    compliance_framework: Optional[str] = Query(None, description="Filter by compliance framework"),
    services: tuple = Depends(get_security_service)
):
    """
    Get security policies for compliance management.
    Returns active security policies and their configurations.
    """
    try:
        _, _, _, security_policy_manager, _ = services
        
        framework_enum = ComplianceFramework(compliance_framework) if compliance_framework else None
        policies = await security_policy_manager.get_policies(framework_enum)
        
        return {
            "policies": policies,
            "total_count": len(policies),
            "compliance_framework": compliance_framework,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting security policies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security policies"
        )

@router.post("/api/security/policies", summary="Create Security Policy")
async def create_security_policy(
    request: SecurityPolicyRequest,
    services: tuple = Depends(get_security_service)
):
    """
    Create a new security policy.
    Defines security rules and compliance requirements.
    """
    try:
        _, _, _, security_policy_manager, _ = services
        
        # Create security policy
        policy = SecurityPolicy(
            policy_id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            rules=request.rules,
            compliance_frameworks=[ComplianceFramework(f) for f in request.compliance_frameworks],
            severity=SecurityLevel(request.severity),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        policy_id = await security_policy_manager.create_policy(policy)
        
        return {
            "policy_id": policy_id,
            "name": policy.name,
            "status": "created",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating security policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create security policy"
        )

@router.post("/api/security/policies/{policy_id}/enforce", summary="Enforce Security Policy")
async def enforce_security_policy(
    policy_id: str,
    data: Dict[str, Any] = Body(..., description="Data to validate against policy"),
    services: tuple = Depends(get_security_service)
):
    """
    Enforce a security policy on data.
    Validates data against policy rules and returns compliance status.
    """
    try:
        _, _, _, security_policy_manager, _ = services
        enforcement_result = await security_policy_manager.enforce_policy(policy_id, data)
        
        return enforcement_result
    except Exception as e:
        logger.error(f"Error enforcing security policy {policy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enforce security policy"
        )

# Compliance Endpoints
@router.get("/api/security/compliance/gdpr/{client_id}", response_model=ComplianceCheckResponse, summary="Check GDPR Compliance")
async def check_gdpr_compliance(
    client_id: str,
    services: tuple = Depends(get_security_service)
):
    """
    Check GDPR compliance status for a client.
    Returns compliance score, violations, and recommendations.
    """
    try:
        _, _, _, _, compliance_manager = services
        compliance_status = await compliance_manager.check_gdpr_compliance(client_id)
        
        return ComplianceCheckResponse(
            framework=compliance_status["framework"],
            is_compliant=compliance_status["is_compliant"],
            score=compliance_status["score"],
            requirements=compliance_status["requirements"],
            violations=compliance_status["violations"],
            recommendations=compliance_status["recommendations"]
        )
    except Exception as e:
        logger.error(f"Error checking GDPR compliance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check GDPR compliance"
        )

@router.get("/api/security/compliance/soc2/{client_id}", response_model=ComplianceCheckResponse, summary="Check SOC2 Compliance")
async def check_soc2_compliance(
    client_id: str,
    services: tuple = Depends(get_security_service)
):
    """
    Check SOC 2 compliance status for a client.
    Returns compliance score, trust principles, and recommendations.
    """
    try:
        _, _, _, _, compliance_manager = services
        compliance_status = await compliance_manager.check_soc2_compliance(client_id)
        
        return ComplianceCheckResponse(
            framework=compliance_status["framework"],
            is_compliant=compliance_status["is_compliant"],
            score=compliance_status["score"],
            requirements=compliance_status["trust_principles"],
            violations=compliance_status["violations"],
            recommendations=compliance_status["recommendations"]
        )
    except Exception as e:
        logger.error(f"Error checking SOC2 compliance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check SOC2 compliance"
        )

@router.get("/api/security/compliance/overview/{client_id}", summary="Get Compliance Overview")
async def get_compliance_overview(
    client_id: str,
    services: tuple = Depends(get_security_service)
):
    """
    Get comprehensive compliance overview for a client.
    Returns status for all supported compliance frameworks.
    """
    try:
        _, _, _, _, compliance_manager = services
        
        # Check all compliance frameworks
        gdpr_status = await compliance_manager.check_gdpr_compliance(client_id)
        soc2_status = await compliance_manager.check_soc2_compliance(client_id)
        
        # Calculate overall compliance score
        total_score = gdpr_status["score"] + soc2_status["score"]
        max_score = 200  # 100 per framework
        overall_score = (total_score / max_score) * 100
        
        return {
            "client_id": client_id,
            "overall_score": overall_score,
            "overall_compliant": overall_score >= 80,
            "frameworks": {
                "gdpr": gdpr_status,
                "soc2": soc2_status
            },
            "summary": {
                "total_requirements_met": len(gdpr_status["requirements"]) + len(soc2_status["trust_principles"]),
                "total_violations": len(gdpr_status["violations"]) + len(soc2_status["violations"]),
                "total_recommendations": len(gdpr_status["recommendations"]) + len(soc2_status["recommendations"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting compliance overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get compliance overview"
        )

# Security Health Check
@router.get("/api/security/health", summary="Security Health Check")
async def security_health_check(
    services: tuple = Depends(get_security_service)
):
    """
    Check the health of the security and compliance system.
    Returns service status and security capabilities.
    """
    try:
        encryption_manager, password_manager, audit_logger, security_policy_manager, compliance_manager = services
        
        # Check database connection
        await audit_logger.db.admin.command('ping')
        
        # Check service components
        components = {
            "encryption_manager": encryption_manager is not None,
            "password_manager": password_manager is not None,
            "audit_logger": audit_logger is not None,
            "security_policy_manager": security_policy_manager is not None,
            "compliance_manager": compliance_manager is not None
        }
        
        all_healthy = all(components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
            "capabilities": {
                "password_security": True,
                "data_encryption": True,
                "audit_logging": True,
                "security_policies": True,
                "compliance_checking": True,
                "gdpr_compliance": True,
                "soc2_compliance": True
            },
            "supported_frameworks": [framework.value for framework in ComplianceFramework],
            "security_levels": [level.value for level in SecurityLevel],
            "audit_event_types": [event_type.value for event_type in AuditEventType],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking security health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
