"""
Session Management Service
Handles user sessions, device tracking, and session revocation
"""

import logging
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import hashlib
import json

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions"""
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        redis_client: Optional[Any] = None
    ):
        self.db = db
        self.redis = redis_client
        self.idle_timeout = timedelta(hours=2)  # 2 hours idle timeout
        self.absolute_timeout = timedelta(days=30)  # 30 days absolute timeout
        self.remember_me_timeout = timedelta(days=90)  # 90 days for remember me
    
    async def create_session(
        self,
        user_id: str,
        organization_id: str,
        device_info: Dict[str, Any],
        remember_me: bool = False
    ) -> Dict[str, Any]:
        """Create new session"""
        try:
            session_id = secrets.token_urlsafe(32)
            device_id = self._generate_device_id(device_info)
            
            expires_at = datetime.utcnow() + (self.remember_me_timeout if remember_me else self.absolute_timeout)
            last_activity = datetime.utcnow()
            
            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "organization_id": organization_id,
                "device_id": device_id,
                "device_info": device_info,
                "ip_address": device_info.get("ip_address"),
                "user_agent": device_info.get("user_agent"),
                "created_at": datetime.utcnow(),
                "last_activity": last_activity,
                "expires_at": expires_at,
                "is_active": True,
                "remember_me": remember_me
            }
            
            await self.db.sessions.insert_one(session_doc)
            
            # Cache in Redis if available
            if self.redis:
                await self._cache_session(session_id, session_doc)
            
            return {
                "session_id": session_id,
                "device_id": device_id,
                "expires_at": expires_at.isoformat(),
                "created_at": session_doc["created_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            # Try Redis first
            if self.redis:
                cached = await self._get_cached_session(session_id)
                if cached:
                    return cached
            
            # Get from database
            session = await self.db.sessions.find_one({
                "session_id": session_id,
                "is_active": True
            })
            
            if not session:
                return None
            
            # Check expiration
            if datetime.utcnow() > session["expires_at"]:
                await self.db.sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"is_active": False}}
                )
                return None
            
            # Check idle timeout
            idle_time = datetime.utcnow() - session["last_activity"]
            if idle_time > self.idle_timeout:
                await self.db.sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"is_active": False}}
                )
                return None
            
            # Cache in Redis
            if self.redis:
                await self._cache_session(session_id, session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        try:
            result = await self.db.sessions.update_one(
                {"session_id": session_id, "is_active": True},
                {"$set": {"last_activity": datetime.utcnow()}}
            )
            
            # Update cache
            if self.redis and result.modified_count > 0:
                session = await self.db.sessions.find_one({"session_id": session_id})
                if session:
                    await self._cache_session(session_id, session)
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return False
    
    async def revoke_session(self, session_id: str, user_id: str) -> bool:
        """Revoke specific session"""
        try:
            result = await self.db.sessions.update_one(
                {"session_id": session_id, "user_id": user_id},
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
            )
            
            # Remove from cache
            if self.redis:
                await self._remove_cached_session(session_id)
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False
    
    async def revoke_all_sessions(self, user_id: str, exclude_session_id: Optional[str] = None) -> int:
        """Revoke all sessions for user except current"""
        try:
            query = {"user_id": user_id, "is_active": True}
            if exclude_session_id:
                query["session_id"] = {"$ne": exclude_session_id}
            
            result = await self.db.sessions.update_many(
                query,
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
            )
            
            # Remove from cache
            if self.redis:
                sessions = await self.db.sessions.find(query).to_list(length=100)
                for session in sessions:
                    await self._remove_cached_session(session["session_id"])
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error revoking all sessions: {e}")
            raise
    
    async def revoke_device_sessions(self, user_id: str, device_id: str) -> int:
        """Revoke all sessions for specific device"""
        try:
            result = await self.db.sessions.update_many(
                {"user_id": user_id, "device_id": device_id, "is_active": True},
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error revoking device sessions: {e}")
            raise
    
    async def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all active sessions for user"""
        try:
            sessions = await self.db.sessions.find({
                "user_id": user_id,
                "is_active": True
            }).sort("last_activity", -1).to_list(length=50)
            
            return [
                {
                    "session_id": s["session_id"],
                    "device_id": s["device_id"],
                    "device_info": s.get("device_info", {}),
                    "ip_address": s.get("ip_address"),
                    "user_agent": s.get("user_agent"),
                    "created_at": s["created_at"].isoformat(),
                    "last_activity": s["last_activity"].isoformat(),
                    "expires_at": s["expires_at"].isoformat(),
                    "is_current": False  # Will be set by caller
                }
                for s in sessions
            ]
            
        except Exception as e:
            logger.error(f"Error listing user sessions: {e}")
            raise
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            result = await self.db.sessions.update_many(
                {
                    "is_active": True,
                    "$or": [
                        {"expires_at": {"$lt": datetime.utcnow()}},
                        {"last_activity": {"$lt": datetime.utcnow() - self.idle_timeout}}
                    ]
                },
                {"$set": {"is_active": False}}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def _generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """Generate device ID from device info"""
        device_string = json.dumps({
            "user_agent": device_info.get("user_agent", ""),
            "platform": device_info.get("platform", ""),
            "browser": device_info.get("browser", "")
        }, sort_keys=True)
        
        return hashlib.sha256(device_string.encode()).hexdigest()[:16]
    
    async def _cache_session(self, session_id: str, session_data: Dict[str, Any]):
        """Cache session in Redis"""
        try:
            if self.redis:
                # Convert datetime to ISO string for JSON serialization
                cache_data = {**session_data}
                for key, value in cache_data.items():
                    if isinstance(value, datetime):
                        cache_data[key] = value.isoformat()
                
                await self.redis.setex(
                    f"session:{session_id}",
                    int(self.absolute_timeout.total_seconds()),
                    json.dumps(cache_data)
                )
        except Exception as e:
            logger.warning(f"Error caching session: {e}")
    
    async def _get_cached_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from Redis cache"""
        try:
            if self.redis:
                cached = await self.redis.get(f"session:{session_id}")
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Error getting cached session: {e}")
        return None
    
    async def _remove_cached_session(self, session_id: str):
        """Remove session from Redis cache"""
        try:
            if self.redis:
                await self.redis.delete(f"session:{session_id}")
        except Exception as e:
            logger.warning(f"Error removing cached session: {e}")

