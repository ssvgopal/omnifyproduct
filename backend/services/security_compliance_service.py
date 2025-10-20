"""
Security & Compliance System
Production-grade security, encryption, audit logging, and compliance features
"""

import asyncio
import json
import logging
import hashlib
import hmac
import secrets
import base64
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import aiohttp

logger = logging.getLogger(__name__)

class SecurityLevel(str, Enum):
    """Security level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceFramework(str, Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"

class AuditEventType(str, Enum):
    """Audit event types"""
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    compliance_frameworks: List[ComplianceFramework]
    severity: SecurityLevel
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    user_id: str
    event_type: AuditEventType
    resource: str
    action: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime
    compliance_tags: List[str] = None

class EncryptionManager:
    """Manages data encryption and decryption"""
    
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
        self.fernet_key = self._derive_fernet_key()
        self.cipher_suite = Fernet(self.fernet_key)
    
    def _derive_fernet_key(self) -> bytes:
        """Derive Fernet key from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'omnify_salt_2024',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_pii(self, pii_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt personally identifiable information"""
        encrypted_pii = {}
        pii_fields = ['email', 'phone', 'ssn', 'address', 'name']
        
        for key, value in pii_data.items():
            if key.lower() in pii_fields and value:
                encrypted_pii[key] = self.encrypt_data(str(value))
            else:
                encrypted_pii[key] = value
        
        return encrypted_pii
    
    def decrypt_pii(self, encrypted_pii: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt personally identifiable information"""
        decrypted_pii = {}
        pii_fields = ['email', 'phone', 'ssn', 'address', 'name']
        
        for key, value in encrypted_pii.items():
            if key.lower() in pii_fields and value:
                try:
                    decrypted_pii[key] = self.decrypt_data(str(value))
                except:
                    decrypted_pii[key] = value  # Fallback to original if decryption fails
            else:
                decrypted_pii[key] = value
        
        return decrypted_pii

class PasswordManager:
    """Manages password security and validation"""
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_symbols = True
        self.max_age_days = 90
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        validation_result = {
            "is_valid": True,
            "score": 0,
            "errors": [],
            "suggestions": []
        }
        
        # Length check
        if len(password) < self.min_length:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Password must be at least {self.min_length} characters long")
        else:
            validation_result["score"] += 1
        
        # Character type checks
        if self.require_uppercase and not any(c.isupper() for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one uppercase letter")
        else:
            validation_result["score"] += 1
        
        if self.require_lowercase and not any(c.islower() for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one lowercase letter")
        else:
            validation_result["score"] += 1
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one number")
        else:
            validation_result["score"] += 1
        
        if self.require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one special character")
        else:
            validation_result["score"] += 1
        
        # Common password check
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password is too common")
        
        # Generate suggestions
        if validation_result["score"] < 3:
            validation_result["suggestions"].append("Use a longer password with mixed characters")
        if validation_result["score"] < 4:
            validation_result["suggestions"].append("Include numbers and special characters")
        
        return validation_result
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        import string
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.retention_days = 2555  # 7 years for compliance
    
    async def log_event(self, audit_log: AuditLog) -> str:
        """Log an audit event"""
        try:
            log_doc = {
                "log_id": audit_log.log_id,
                "user_id": audit_log.user_id,
                "event_type": audit_log.event_type.value,
                "resource": audit_log.resource,
                "action": audit_log.action,
                "details": audit_log.details,
                "ip_address": audit_log.ip_address,
                "user_agent": audit_log.user_agent,
                "timestamp": audit_log.timestamp.isoformat(),
                "compliance_tags": audit_log.compliance_tags or [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.db.audit_logs.insert_one(log_doc)
            
            logger.info(f"Audit event logged: {audit_log.event_type.value} by {audit_log.user_id}")
            return audit_log.log_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            raise
    
    async def get_audit_logs(self, 
                           user_id: Optional[str] = None,
                           event_type: Optional[AuditEventType] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering"""
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            if event_type:
                query["event_type"] = event_type.value
            if start_date:
                query["timestamp"] = {"$gte": start_date.isoformat()}
            if end_date:
                if "timestamp" in query:
                    query["timestamp"]["$lte"] = end_date.isoformat()
                else:
                    query["timestamp"] = {"$lte": end_date.isoformat()}
            
            logs = await self.db.audit_logs.find(query).sort("timestamp", -1).limit(limit).to_list(length=None)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            raise
    
    async def cleanup_old_logs(self) -> int:
        """Clean up old audit logs based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            result = await self.db.audit_logs.delete_many({
                "timestamp": {"$lt": cutoff_date.isoformat()}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old audit logs")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old audit logs: {e}")
            raise

class SecurityPolicyManager:
    """Manages security policies and compliance"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.default_policies = self._load_default_policies()
    
    def _load_default_policies(self) -> List[SecurityPolicy]:
        """Load default security policies"""
        policies = [
            SecurityPolicy(
                policy_id="password_policy",
                name="Password Security Policy",
                description="Enforces strong password requirements",
                rules=[
                    {"type": "min_length", "value": 12},
                    {"type": "require_uppercase", "value": True},
                    {"type": "require_lowercase", "value": True},
                    {"type": "require_numbers", "value": True},
                    {"type": "require_symbols", "value": True},
                    {"type": "max_age_days", "value": 90}
                ],
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
                severity=SecurityLevel.HIGH,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SecurityPolicy(
                policy_id="data_encryption",
                name="Data Encryption Policy",
                description="Encrypts sensitive data at rest and in transit",
                rules=[
                    {"type": "encrypt_pii", "value": True},
                    {"type": "encrypt_passwords", "value": True},
                    {"type": "encrypt_api_keys", "value": True},
                    {"type": "use_tls", "value": True}
                ],
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOC2, ComplianceFramework.HIPAA],
                severity=SecurityLevel.CRITICAL,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SecurityPolicy(
                policy_id="access_control",
                name="Access Control Policy",
                description="Manages user access and permissions",
                rules=[
                    {"type": "require_mfa", "value": True},
                    {"type": "session_timeout", "value": 3600},
                    {"type": "max_login_attempts", "value": 5},
                    {"type": "lockout_duration", "value": 1800}
                ],
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
                severity=SecurityLevel.HIGH,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SecurityPolicy(
                policy_id="audit_logging",
                name="Audit Logging Policy",
                description="Comprehensive audit logging for compliance",
                rules=[
                    {"type": "log_all_access", "value": True},
                    {"type": "log_data_changes", "value": True},
                    {"type": "log_security_events", "value": True},
                    {"type": "retention_years", "value": 7}
                ],
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOC2, ComplianceFramework.HIPAA],
                severity=SecurityLevel.CRITICAL,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        return policies
    
    async def create_policy(self, policy: SecurityPolicy) -> str:
        """Create a new security policy"""
        try:
            policy_doc = {
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "rules": policy.rules,
                "compliance_frameworks": [f.value for f in policy.compliance_frameworks],
                "severity": policy.severity.value,
                "is_active": policy.is_active,
                "created_at": policy.created_at.isoformat() if policy.created_at else datetime.utcnow().isoformat(),
                "updated_at": policy.updated_at.isoformat() if policy.updated_at else datetime.utcnow().isoformat()
            }
            
            await self.db.security_policies.insert_one(policy_doc)
            
            logger.info(f"Created security policy: {policy.policy_id}")
            return policy.policy_id
            
        except Exception as e:
            logger.error(f"Error creating security policy: {e}")
            raise
    
    async def get_policies(self, compliance_framework: Optional[ComplianceFramework] = None) -> List[Dict[str, Any]]:
        """Get security policies"""
        try:
            query = {"is_active": True}
            if compliance_framework:
                query["compliance_frameworks"] = compliance_framework.value
            
            policies = await self.db.security_policies.find(query).to_list(length=None)
            return policies
            
        except Exception as e:
            logger.error(f"Error getting security policies: {e}")
            raise
    
    async def enforce_policy(self, policy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce a security policy"""
        try:
            policy = await self.db.security_policies.find_one({"policy_id": policy_id})
            if not policy:
                raise ValueError(f"Policy {policy_id} not found")
            
            enforcement_result = {
                "policy_id": policy_id,
                "is_compliant": True,
                "violations": [],
                "recommendations": []
            }
            
            # Enforce password policy
            if policy_id == "password_policy" and "password" in data:
                password_manager = PasswordManager()
                validation = password_manager.validate_password_strength(data["password"])
                if not validation["is_valid"]:
                    enforcement_result["is_compliant"] = False
                    enforcement_result["violations"].extend(validation["errors"])
                    enforcement_result["recommendations"].extend(validation["suggestions"])
            
            # Enforce data encryption policy
            if policy_id == "data_encryption":
                pii_fields = ['email', 'phone', 'ssn', 'address', 'name']
                for field in pii_fields:
                    if field in data and not self._is_encrypted(data[field]):
                        enforcement_result["is_compliant"] = False
                        enforcement_result["violations"].append(f"Field '{field}' contains unencrypted PII")
                        enforcement_result["recommendations"].append(f"Encrypt field '{field}' before storage")
            
            return enforcement_result
            
        except Exception as e:
            logger.error(f"Error enforcing policy {policy_id}: {e}")
            raise
    
    def _is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted"""
        try:
            # Simple check - encrypted data should be base64-like and longer
            if len(data) < 20:
                return False
            base64.urlsafe_b64decode(data)
            return True
        except:
            return False

class ComplianceManager:
    """Manages compliance with various frameworks"""
    
    def __init__(self, db: AsyncIOMotorClient, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
    
    async def check_gdpr_compliance(self, client_id: str) -> Dict[str, Any]:
        """Check GDPR compliance status"""
        try:
            compliance_status = {
                "framework": "GDPR",
                "is_compliant": True,
                "score": 0,
                "requirements": [],
                "violations": [],
                "recommendations": []
            }
            
            # Check data encryption
            encryption_policy = await self.db.security_policies.find_one({"policy_id": "data_encryption"})
            if encryption_policy and encryption_policy["is_active"]:
                compliance_status["score"] += 25
                compliance_status["requirements"].append("Data encryption implemented")
            else:
                compliance_status["is_compliant"] = False
                compliance_status["violations"].append("Data encryption not properly implemented")
                compliance_status["recommendations"].append("Enable data encryption policy")
            
            # Check audit logging
            audit_policy = await self.db.security_policies.find_one({"policy_id": "audit_logging"})
            if audit_policy and audit_policy["is_active"]:
                compliance_status["score"] += 25
                compliance_status["requirements"].append("Audit logging implemented")
            else:
                compliance_status["is_compliant"] = False
                compliance_status["violations"].append("Audit logging not properly implemented")
                compliance_status["recommendations"].append("Enable audit logging policy")
            
            # Check data retention
            retention_logs = await self.db.audit_logs.find({"user_id": client_id}).to_list(length=None)
            if len(retention_logs) > 0:
                compliance_status["score"] += 25
                compliance_status["requirements"].append("Data retention policy in place")
            else:
                compliance_status["violations"].append("No data retention evidence found")
                compliance_status["recommendations"].append("Implement data retention policy")
            
            # Check consent management
            consent_records = await self.db.consent_records.find({"client_id": client_id}).to_list(length=None)
            if len(consent_records) > 0:
                compliance_status["score"] += 25
                compliance_status["requirements"].append("Consent management implemented")
            else:
                compliance_status["violations"].append("Consent management not implemented")
                compliance_status["recommendations"].append("Implement consent management system")
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Error checking GDPR compliance: {e}")
            raise
    
    async def check_soc2_compliance(self, client_id: str) -> Dict[str, Any]:
        """Check SOC 2 compliance status"""
        try:
            compliance_status = {
                "framework": "SOC2",
                "is_compliant": True,
                "score": 0,
                "trust_principles": [],
                "violations": [],
                "recommendations": []
            }
            
            # Security principle
            security_policies = await self.db.security_policies.find({"is_active": True}).to_list(length=None)
            if len(security_policies) >= 3:
                compliance_status["score"] += 20
                compliance_status["trust_principles"].append("Security controls implemented")
            else:
                compliance_status["is_compliant"] = False
                compliance_status["violations"].append("Insufficient security controls")
                compliance_status["recommendations"].append("Implement additional security policies")
            
            # Availability principle
            availability_logs = await self.db.system_logs.find({"event_type": "availability"}).to_list(length=None)
            if len(availability_logs) > 0:
                compliance_status["score"] += 20
                compliance_status["trust_principles"].append("Availability monitoring implemented")
            else:
                compliance_status["violations"].append("Availability monitoring not implemented")
                compliance_status["recommendations"].append("Implement availability monitoring")
            
            # Processing integrity principle
            audit_logs = await self.db.audit_logs.find({}).to_list(length=None)
            if len(audit_logs) > 0:
                compliance_status["score"] += 20
                compliance_status["trust_principles"].append("Processing integrity controls implemented")
            else:
                compliance_status["violations"].append("Processing integrity controls not implemented")
                compliance_status["recommendations"].append("Implement processing integrity controls")
            
            # Confidentiality principle
            encryption_policy = await self.db.security_policies.find_one({"policy_id": "data_encryption"})
            if encryption_policy and encryption_policy["is_active"]:
                compliance_status["score"] += 20
                compliance_status["trust_principles"].append("Confidentiality controls implemented")
            else:
                compliance_status["violations"].append("Confidentiality controls not implemented")
                compliance_status["recommendations"].append("Implement confidentiality controls")
            
            # Privacy principle
            privacy_policy = await self.db.security_policies.find_one({"policy_id": "privacy_policy"})
            if privacy_policy and privacy_policy["is_active"]:
                compliance_status["score"] += 20
                compliance_status["trust_principles"].append("Privacy controls implemented")
            else:
                compliance_status["violations"].append("Privacy controls not implemented")
                compliance_status["recommendations"].append("Implement privacy controls")
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Error checking SOC2 compliance: {e}")
            raise

# Global instances
encryption_manager = None
password_manager = None
audit_logger = None
security_policy_manager = None
compliance_manager = None

def get_encryption_manager(master_key: str) -> EncryptionManager:
    """Get encryption manager instance"""
    global encryption_manager
    if encryption_manager is None:
        encryption_manager = EncryptionManager(master_key)
    return encryption_manager

def get_password_manager() -> PasswordManager:
    """Get password manager instance"""
    global password_manager
    if password_manager is None:
        password_manager = PasswordManager()
    return password_manager

def get_audit_logger(db: AsyncIOMotorClient) -> AuditLogger:
    """Get audit logger instance"""
    global audit_logger
    if audit_logger is None:
        audit_logger = AuditLogger(db)
    return audit_logger

def get_security_policy_manager(db: AsyncIOMotorClient) -> SecurityPolicyManager:
    """Get security policy manager instance"""
    global security_policy_manager
    if security_policy_manager is None:
        security_policy_manager = SecurityPolicyManager(db)
    return security_policy_manager

def get_compliance_manager(db: AsyncIOMotorClient, audit_logger: AuditLogger) -> ComplianceManager:
    """Get compliance manager instance"""
    global compliance_manager
    if compliance_manager is None:
        compliance_manager = ComplianceManager(db, audit_logger)
    return compliance_manager
