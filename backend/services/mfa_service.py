"""
Multi-Factor Authentication (MFA) Service for OmniFy Cloud Connect
Supports TOTP, SMS, Email, and Hardware Tokens (FIDO2/WebAuthn)
"""

import asyncio
import json
import logging
import secrets
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import qrcode
from io import BytesIO
import pyotp
import aiohttp
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MFAMethod(str, Enum):
    """MFA methods supported"""
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, Authy)
    SMS = "sms"  # SMS-based verification
    EMAIL = "email"  # Email-based verification
    HARDWARE_TOKEN = "hardware_token"  # FIDO2/WebAuthn hardware tokens


class MFAStatus(str, Enum):
    """MFA status"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    PENDING_SETUP = "pending_setup"
    LOCKED = "locked"


@dataclass
class MFASecret:
    """MFA secret data"""
    user_id: str
    method: MFAMethod
    secret: str  # Encrypted secret
    backup_codes: List[str]  # Encrypted backup codes
    is_verified: bool
    created_at: datetime
    last_used: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None


@dataclass
class MFASession:
    """MFA verification session"""
    session_id: str
    user_id: str
    method: MFAMethod
    expires_at: datetime
    verified: bool = False
    attempts: int = 0
    max_attempts: int = 5


class MFAService:
    """Multi-Factor Authentication Service"""
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        encryption_key: str,
        sms_api_key: Optional[str] = None,
        email_service: Optional[Any] = None
    ):
        self.db = db
        self.encryption_key = encryption_key
        self.sms_api_key = sms_api_key
        self.email_service = email_service
        self.totp_issuer = "OmniFy Cloud Connect"
        self.totp_interval = 30  # 30 seconds
        
        # Rate limiting
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.verification_code_expiry = timedelta(minutes=10)
    
    # ========== TOTP (Time-based One-Time Password) ==========
    
    def generate_totp_secret(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """Generate TOTP secret for user"""
        try:
            # Generate secret
            secret = pyotp.random_base32()
            
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name=self.totp_issuer
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            
            # Encrypt secret before storing
            encrypted_secret = self._encrypt_secret(secret)
            
            # Store in database
            mfa_secret = {
                "user_id": user_id,
                "method": MFAMethod.TOTP.value,
                "secret": encrypted_secret,
                "backup_codes": [],
                "is_verified": False,
                "created_at": datetime.utcnow(),
                "failed_attempts": 0
            }
            
            return {
                "secret": secret,  # Return plain secret for QR code generation
                "qr_code": f"data:image/png;base64,{qr_code_data}",
                "uri": totp_uri,
                "backup_codes": self._generate_backup_codes(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error generating TOTP secret: {e}")
            raise
    
    async def setup_totp(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """Setup TOTP for user"""
        try:
            # Check if TOTP already exists
            existing = await self.db.mfa_secrets.find_one({
                "user_id": user_id,
                "method": MFAMethod.TOTP.value
            })
            
            if existing and existing.get("is_verified"):
                raise ValueError("TOTP is already set up and verified for this user")
            
            # Generate TOTP secret
            totp_data = self.generate_totp_secret(user_id, user_email)
            
            # Encrypt backup codes
            encrypted_backup_codes = [
                self._encrypt_secret(code) for code in totp_data["backup_codes"]
            ]
            
            # Store in database
            mfa_doc = {
                "user_id": user_id,
                "method": MFAMethod.TOTP.value,
                "secret": self._encrypt_secret(totp_data["secret"]),
                "backup_codes": encrypted_backup_codes,
                "is_verified": False,
                "created_at": datetime.utcnow(),
                "failed_attempts": 0
            }
            
            if existing:
                await self.db.mfa_secrets.update_one(
                    {"user_id": user_id, "method": MFAMethod.TOTP.value},
                    {"$set": mfa_doc}
                )
            else:
                await self.db.mfa_secrets.insert_one(mfa_doc)
            
            return {
                "qr_code": totp_data["qr_code"],
                "uri": totp_data["uri"],
                "backup_codes": totp_data["backup_codes"],  # Return plain codes for user to save
                "status": "pending_verification"
            }
            
        except Exception as e:
            logger.error(f"Error setting up TOTP: {e}")
            raise
    
    async def verify_totp(self, user_id: str, code: str) -> bool:
        """Verify TOTP code"""
        try:
            # Get TOTP secret
            mfa_doc = await self.db.mfa_secrets.find_one({
                "user_id": user_id,
                "method": MFAMethod.TOTP.value
            })
            
            if not mfa_doc:
                return False
            
            # Check if locked
            if mfa_doc.get("locked_until"):
                if datetime.utcnow() < mfa_doc["locked_until"]:
                    raise ValueError("MFA is locked due to too many failed attempts")
                else:
                    # Unlock
                    await self.db.mfa_secrets.update_one(
                        {"user_id": user_id, "method": MFAMethod.TOTP.value},
                        {"$unset": {"locked_until": ""}, "$set": {"failed_attempts": 0}}
                    )
            
            # Decrypt secret
            secret = self._decrypt_secret(mfa_doc["secret"])
            
            # Verify code
            totp = pyotp.TOTP(secret, interval=self.totp_interval)
            is_valid = totp.verify(code, valid_window=1)  # Allow 1 time step window
            
            # Also check backup codes
            if not is_valid:
                backup_codes = mfa_doc.get("backup_codes", [])
                for encrypted_code in backup_codes:
                    if self._decrypt_secret(encrypted_code) == code:
                        is_valid = True
                        # Remove used backup code
                        backup_codes.remove(encrypted_code)
                        await self.db.mfa_secrets.update_one(
                            {"user_id": user_id, "method": MFAMethod.TOTP.value},
                            {"$set": {"backup_codes": backup_codes}}
                        )
                        break
            
            if is_valid:
                # Reset failed attempts and mark as verified
                await self.db.mfa_secrets.update_one(
                    {"user_id": user_id, "method": MFAMethod.TOTP.value},
                    {
                        "$set": {
                            "is_verified": True,
                            "last_used": datetime.utcnow(),
                            "failed_attempts": 0
                        },
                        "$unset": {"locked_until": ""}
                    }
                )
                return True
            else:
                # Increment failed attempts
                failed_attempts = mfa_doc.get("failed_attempts", 0) + 1
                update_data = {"$set": {"failed_attempts": failed_attempts}}
                
                if failed_attempts >= self.max_failed_attempts:
                    update_data["$set"]["locked_until"] = datetime.utcnow() + self.lockout_duration
                
                await self.db.mfa_secrets.update_one(
                    {"user_id": user_id, "method": MFAMethod.TOTP.value},
                    update_data
                )
                return False
                
        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            raise
    
    # ========== SMS MFA ==========
    
    async def send_sms_code(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Send SMS verification code"""
        try:
            # Generate 6-digit code
            code = str(secrets.randbelow(900000) + 100000)
            
            # Encrypt code
            encrypted_code = self._encrypt_secret(code)
            
            # Store verification session
            session_id = str(uuid.uuid4())
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "method": MFAMethod.SMS.value,
                "code": encrypted_code,
                "phone_number": phone_number,
                "expires_at": datetime.utcnow() + self.verification_code_expiry,
                "verified": False,
                "attempts": 0,
                "created_at": datetime.utcnow()
            }
            
            await self.db.mfa_sessions.insert_one(session)
            
            # Send SMS (using Twilio or similar)
            if self.sms_api_key:
                await self._send_sms_via_api(phone_number, code)
            else:
                logger.warning("SMS API key not configured, code would be: %s", code)
            
            return {
                "session_id": session_id,
                "message": "SMS code sent successfully",
                "expires_in": int(self.verification_code_expiry.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS code: {e}")
            raise
    
    async def verify_sms_code(self, session_id: str, code: str) -> bool:
        """Verify SMS code"""
        try:
            # Get session
            session = await self.db.mfa_sessions.find_one({"session_id": session_id})
            
            if not session:
                return False
            
            # Check expiration
            if datetime.utcnow() > session["expires_at"]:
                await self.db.mfa_sessions.delete_one({"session_id": session_id})
                raise ValueError("Verification code has expired")
            
            # Check attempts
            if session.get("attempts", 0) >= self.max_failed_attempts:
                await self.db.mfa_sessions.delete_one({"session_id": session_id})
                raise ValueError("Too many failed attempts")
            
            # Verify code
            stored_code = self._decrypt_secret(session["code"])
            is_valid = stored_code == code
            
            if is_valid:
                # Mark as verified and create MFA secret
                await self.db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"verified": True}}
                )
                
                # Store SMS method as verified
                await self.db.mfa_secrets.update_one(
                    {
                        "user_id": session["user_id"],
                        "method": MFAMethod.SMS.value
                    },
                    {
                        "$set": {
                            "is_verified": True,
                            "last_used": datetime.utcnow(),
                            "phone_number": session["phone_number"]
                        }
                    },
                    upsert=True
                )
                
                return True
            else:
                # Increment attempts
                await self.db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$inc": {"attempts": 1}}
                )
                return False
                
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            raise
    
    # ========== Email MFA ==========
    
    async def send_email_code(self, user_id: str, email: str) -> Dict[str, Any]:
        """Send email verification code"""
        try:
            # Generate 6-digit code
            code = str(secrets.randbelow(900000) + 100000)
            
            # Encrypt code
            encrypted_code = self._encrypt_secret(code)
            
            # Store verification session
            session_id = str(uuid.uuid4())
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "method": MFAMethod.EMAIL.value,
                "code": encrypted_code,
                "email": email,
                "expires_at": datetime.utcnow() + self.verification_code_expiry,
                "verified": False,
                "attempts": 0,
                "created_at": datetime.utcnow()
            }
            
            await self.db.mfa_sessions.insert_one(session)
            
            # Send email
            if self.email_service:
                await self.email_service.send_verification_email(email, code)
            else:
                logger.warning("Email service not configured, code would be: %s", code)
            
            return {
                "session_id": session_id,
                "message": "Email code sent successfully",
                "expires_in": int(self.verification_code_expiry.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Error sending email code: {e}")
            raise
    
    async def verify_email_code(self, session_id: str, code: str) -> bool:
        """Verify email code"""
        try:
            # Get session
            session = await self.db.mfa_sessions.find_one({"session_id": session_id})
            
            if not session:
                return False
            
            # Check expiration
            if datetime.utcnow() > session["expires_at"]:
                await self.db.mfa_sessions.delete_one({"session_id": session_id})
                raise ValueError("Verification code has expired")
            
            # Check attempts
            if session.get("attempts", 0) >= self.max_failed_attempts:
                await self.db.mfa_sessions.delete_one({"session_id": session_id})
                raise ValueError("Too many failed attempts")
            
            # Verify code
            stored_code = self._decrypt_secret(session["code"])
            is_valid = stored_code == code
            
            if is_valid:
                # Mark as verified and create MFA secret
                await self.db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"verified": True}}
                )
                
                # Store email method as verified
                await self.db.mfa_secrets.update_one(
                    {
                        "user_id": session["user_id"],
                        "method": MFAMethod.EMAIL.value
                    },
                    {
                        "$set": {
                            "is_verified": True,
                            "last_used": datetime.utcnow(),
                            "email": session["email"]
                        }
                    },
                    upsert=True
                )
                
                return True
            else:
                # Increment attempts
                await self.db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$inc": {"attempts": 1}}
                )
                return False
                
        except Exception as e:
            logger.error(f"Error verifying email code: {e}")
            raise
    
    # ========== MFA Status and Management ==========
    
    async def get_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """Get MFA status for user"""
        try:
            mfa_secrets = await self.db.mfa_secrets.find(
                {"user_id": user_id, "is_verified": True}
            ).to_list(length=10)
            
            methods = [MFASecret(**doc) for doc in mfa_secrets]
            
            return {
                "user_id": user_id,
                "mfa_enabled": len(methods) > 0,
                "methods": [
                    {
                        "method": m.method.value,
                        "created_at": m.created_at.isoformat(),
                        "last_used": m.last_used.isoformat() if m.last_used else None
                    }
                    for m in methods
                ],
                "status": MFAStatus.ENABLED.value if methods else MFAStatus.DISABLED.value
            }
            
        except Exception as e:
            logger.error(f"Error getting MFA status: {e}")
            raise
    
    async def disable_mfa(self, user_id: str, method: MFAMethod) -> bool:
        """Disable MFA for user"""
        try:
            result = await self.db.mfa_secrets.delete_one({
                "user_id": user_id,
                "method": method.value
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error disabling MFA: {e}")
            raise
    
    async def require_mfa(self, user_id: str) -> bool:
        """Check if MFA is required for user"""
        try:
            mfa_secrets = await self.db.mfa_secrets.find({
                "user_id": user_id,
                "is_verified": True
            }).to_list(length=1)
            
            return len(mfa_secrets) > 0
        except Exception as e:
            logger.error(f"Error checking MFA requirement: {e}")
            return False
    
    # ========== Helper Methods ==========
    
    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt secret using Fernet encryption"""
        from core.encryption import encrypt_secret
        return encrypt_secret(secret)
    
    def _decrypt_secret(self, encrypted: str) -> str:
        """Decrypt secret using Fernet decryption"""
        from core.encryption import decrypt_secret
        return decrypt_secret(encrypted)
    
    def _generate_backup_codes(self, user_id: str, count: int = 10) -> List[str]:
        """Generate backup codes"""
        return [secrets.token_urlsafe(8) for _ in range(count)]
    
    async def _send_sms_via_api(self, phone_number: str, code: str):
        """Send SMS via API (Twilio, AWS SNS, etc.)"""
        # TODO: Implement actual SMS sending
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(body=f"Your OmniFy verification code is: {code}", from_=twilio_number, to=phone_number)
        logger.info(f"Would send SMS to {phone_number} with code: {code}")

