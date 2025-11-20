"""
Email Verification Service
Handles email verification, password reset, and email notifications
"""

import logging
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import aiohttp
import os

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for email verification and password reset"""
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        email_api_key: Optional[str] = None,
        email_from: Optional[str] = None
    ):
        self.db = db
        self.email_api_key = email_api_key or os.environ.get('EMAIL_API_KEY')
        self.email_from = email_from or os.environ.get('EMAIL_FROM', 'noreply@omnify.cloud')
        self.verification_token_expiry = timedelta(hours=24)
        self.reset_token_expiry = timedelta(hours=1)
        self.base_url = os.environ.get('APP_URL', 'http://localhost:3000')
    
    async def send_verification_email(self, user_id: str, email: str) -> Dict[str, Any]:
        """Send email verification email"""
        try:
            # Generate verification token
            token = secrets.token_urlsafe(32)
            
            # Store verification token
            verification_doc = {
                "user_id": user_id,
                "email": email,
                "token": token,
                "type": "email_verification",
                "expires_at": datetime.utcnow() + self.verification_token_expiry,
                "created_at": datetime.utcnow(),
                "verified": False
            }
            
            await self.db.email_verifications.insert_one(verification_doc)
            
            # Send email
            verification_url = f"{self.base_url}/verify-email?token={token}"
            
            email_content = f"""
            <html>
            <body>
                <h2>Verify Your Email Address</h2>
                <p>Thank you for signing up for OmniFy Cloud Connect!</p>
                <p>Please click the link below to verify your email address:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </body>
            </html>
            """
            
            await self._send_email(
                to_email=email,
                subject="Verify Your Email - OmniFy Cloud Connect",
                html_content=email_content
            )
            
            return {
                "success": True,
                "message": "Verification email sent",
                "expires_in": int(self.verification_token_expiry.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            raise
    
    async def verify_email(self, token: str) -> bool:
        """Verify email with token"""
        try:
            # Find verification record
            verification = await self.db.email_verifications.find_one({
                "token": token,
                "type": "email_verification",
                "verified": False
            })
            
            if not verification:
                return False
            
            # Check expiration
            if datetime.utcnow() > verification["expires_at"]:
                await self.db.email_verifications.delete_one({"token": token})
                raise ValueError("Verification token has expired")
            
            # Mark as verified
            await self.db.email_verifications.update_one(
                {"token": token},
                {"$set": {"verified": True, "verified_at": datetime.utcnow()}}
            )
            
            # Update user
            await self.db.users.update_one(
                {"user_id": verification["user_id"]},
                {"$set": {"is_verified": True, "email_verified_at": datetime.utcnow()}}
            )
            
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            raise
    
    async def send_password_reset_email(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            # Find user
            user = await self.db.users.find_one({"email": email, "is_active": True})
            if not user:
                # Don't reveal if user exists
                return {
                    "success": True,
                    "message": "If an account exists with this email, a password reset link has been sent"
                }
            
            # Generate reset token
            token = secrets.token_urlsafe(32)
            
            # Store reset token
            reset_doc = {
                "user_id": user["user_id"],
                "email": email,
                "token": token,
                "type": "password_reset",
                "expires_at": datetime.utcnow() + self.reset_token_expiry,
                "created_at": datetime.utcnow(),
                "used": False
            }
            
            await self.db.password_resets.insert_one(reset_doc)
            
            # Send email
            reset_url = f"{self.base_url}/reset-password?token={token}"
            
            email_content = f"""
            <html>
            <body>
                <h2>Reset Your Password</h2>
                <p>You requested to reset your password for OmniFy Cloud Connect.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
            </html>
            """
            
            await self._send_email(
                to_email=email,
                subject="Reset Your Password - OmniFy Cloud Connect",
                html_content=email_content
            )
            
            return {
                "success": True,
                "message": "Password reset email sent",
                "expires_in": int(self.reset_token_expiry.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            raise
    
    async def verify_reset_token(self, token: str) -> Dict[str, Any]:
        """Verify password reset token"""
        try:
            reset_doc = await self.db.password_resets.find_one({
                "token": token,
                "type": "password_reset",
                "used": False
            })
            
            if not reset_doc:
                return {"valid": False, "message": "Invalid or expired reset token"}
            
            # Check expiration
            if datetime.utcnow() > reset_doc["expires_at"]:
                await self.db.password_resets.delete_one({"token": token})
                return {"valid": False, "message": "Reset token has expired"}
            
            return {
                "valid": True,
                "user_id": reset_doc["user_id"],
                "email": reset_doc["email"]
            }
            
        except Exception as e:
            logger.error(f"Error verifying reset token: {e}")
            return {"valid": False, "message": "Error verifying token"}
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        try:
            # Verify token
            verification = await self.verify_reset_token(token)
            if not verification.get("valid"):
                raise ValueError(verification.get("message", "Invalid token"))
            
            user_id = verification["user_id"]
            
            # Hash new password
            from services.auth_service import AuthService
            auth_service = AuthService(self.db, os.environ.get('JWT_SECRET', ''))
            hashed_password = auth_service.hash_password(new_password)
            
            # Update password
            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"password_hash": hashed_password, "updated_at": datetime.utcnow()}}
            )
            
            # Mark token as used
            await self.db.password_resets.update_one(
                {"token": token},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
            
            # Invalidate all sessions (optional - for security)
            await self.db.sessions.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            raise
    
    async def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """Resend verification email"""
        try:
            user = await self.db.users.find_one({"email": email})
            if not user:
                raise ValueError("User not found")
            
            if user.get("is_verified"):
                raise ValueError("Email is already verified")
            
            # Delete old verification tokens
            await self.db.email_verifications.delete_many({
                "user_id": user["user_id"],
                "type": "email_verification"
            })
            
            # Send new verification email
            return await self.send_verification_email(user["user_id"], email)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error resending verification email: {e}")
            raise
    
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """Send email via email service (Resend, SendGrid, SES, etc.)"""
        try:
            # TODO: Integrate with actual email service
            # Example with Resend API:
            if self.email_api_key:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.email_api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "from": self.email_from,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content
                    }
                    # async with session.post(
                    #     "https://api.resend.com/emails",
                    #     headers=headers,
                    #     json=payload
                    # ) as response:
                    #     if response.status != 200:
                    #         raise Exception(f"Email service error: {response.status}")
                    logger.info(f"Would send email to {to_email} with subject: {subject}")
            else:
                logger.warning(f"Email API key not configured. Would send email to {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

