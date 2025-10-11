"""
Redis Caching Service for OmnifyProduct
High-performance caching layer with intelligent cache strategies

Features:
- API response caching with TTL
- Session management
- Rate limiting counters
- Background job queuing
- Cache warming strategies
- Performance monitoring
"""

import json
import hashlib
import asyncio
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from services.structured_logging import logger

class RedisCacheService:
    """
    Redis-based caching service with advanced features
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", password: str = None):
        self.redis_url = redis_url
        self.password = password
        self.redis_client: Optional[redis.Redis] = None
        self.cache_prefix = "omnify:"
        self.session_prefix = "session:"
        self.rate_limit_prefix = "ratelimit:"
        self.job_queue_prefix = "job:"

        # Cache TTL configurations
        self.cache_ttl = {
            "api_response": 300,      # 5 minutes for API responses
            "agent_result": 1800,     # 30 minutes for agent results
            "analytics": 3600,        # 1 hour for analytics data
            "user_session": 86400,    # 24 hours for user sessions
            "campaign_data": 1800,    # 30 minutes for campaign data
            "rate_limit": 60,         # 1 minute for rate limiting
        }

        logger.info("Redis cache service initialized", extra={
            "cache_ttl_config": self.cache_ttl,
            "redis_url": redis_url.replace(password or "", "***") if password else redis_url
        })

    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                password=self.password,
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )

            # Test connection
            await self.redis_client.ping()

            logger.info("Redis connection established", extra={
                "redis_url": self.redis_url.replace(self.password or "", "***") if self.password else self.redis_url
            })

        except Exception as e:
            logger.error("Failed to connect to Redis", exc_info=e, extra={
                "redis_url": self.redis_url.replace(self.password or "", "***") if self.password else self.redis_url
            })
            raise

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    # ========== API RESPONSE CACHING ==========

    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """Generate consistent cache key from endpoint and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True, default=str)

        # Include user_id for user-specific caching
        key_components = [endpoint, sorted_params]
        if user_id:
            key_components.append(user_id)

        key_string = "|".join(key_components)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"{self.cache_prefix}api:{key_hash}"

    async def get_cached_response(self, endpoint: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached API response if available"""
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(endpoint, params, user_id)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                response = json.loads(cached_data)
                logger.debug("Cache hit for API response", extra={
                    "endpoint": endpoint,
                    "cache_key": cache_key,
                    "user_id": user_id
                })
                return response

            logger.debug("Cache miss for API response", extra={
                "endpoint": endpoint,
                "cache_key": cache_key,
                "user_id": user_id
            })
            return None

        except Exception as e:
            logger.warning("Error retrieving cached response", exc_info=e, extra={
                "endpoint": endpoint,
                "user_id": user_id
            })
            return None

    async def set_cached_response(self, endpoint: str, params: Dict[str, Any], response: Dict[str, Any],
                                user_id: Optional[str] = None, ttl: Optional[int] = None) -> None:
        """Cache API response with TTL"""
        if not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key(endpoint, params, user_id)
            ttl_value = ttl or self.cache_ttl["api_response"]

            # Serialize response
            cached_data = json.dumps(response, default=str)

            await self.redis_client.setex(cache_key, ttl_value, cached_data)

            logger.debug("API response cached", extra={
                "endpoint": endpoint,
                "cache_key": cache_key,
                "ttl": ttl_value,
                "user_id": user_id,
                "response_size": len(cached_data)
            })

        except Exception as e:
            logger.warning("Error caching API response", exc_info=e, extra={
                "endpoint": endpoint,
                "user_id": user_id
            })

    async def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        if not self.redis_client:
            return 0

        try:
            # Find keys matching pattern
            keys = await self.redis_client.keys(f"{self.cache_prefix}{pattern}")

            if keys:
                await self.redis_client.delete(*keys)
                logger.info("Cache invalidated", extra={
                    "pattern": pattern,
                    "keys_deleted": len(keys)
                })
                return len(keys)

            return 0

        except Exception as e:
            logger.warning("Error invalidating cache", exc_info=e, extra={
                "pattern": pattern
            })
            return 0

    # ========== SESSION MANAGEMENT ==========

    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create user session with TTL"""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")

        session_id = hashlib.sha256(f"{user_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:32]

        try:
            session_key = f"{self.session_prefix}{session_id}"

            # Add session metadata
            session_data.update({
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            })

            await self.redis_client.setex(
                session_key,
                self.cache_ttl["user_session"],
                json.dumps(session_data, default=str)
            )

            logger.info("User session created", extra={
                "session_id": session_id,
                "user_id": user_id
            })

            return session_id

        except Exception as e:
            logger.error("Failed to create session", exc_info=e, extra={
                "user_id": user_id
            })
            raise

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data and update last activity"""
        if not self.redis_client:
            return None

        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis_client.get(session_key)

            if session_data:
                # Update last activity
                session_dict = json.loads(session_data)
                session_dict["last_activity"] = datetime.utcnow().isoformat()

                await self.redis_client.setex(
                    session_key,
                    self.cache_ttl["user_session"],
                    json.dumps(session_dict, default=str)
                )

                return session_dict

            return None

        except Exception as e:
            logger.warning("Error retrieving session", exc_info=e, extra={
                "session_id": session_id
            })
            return None

    async def destroy_session(self, session_id: str) -> bool:
        """Destroy user session"""
        if not self.redis_client:
            return False

        try:
            session_key = f"{self.session_prefix}{session_id}"
            result = await self.redis_client.delete(session_key)

            logger.info("Session destroyed", extra={
                "session_id": session_id,
                "deleted": bool(result)
            })

            return bool(result)

        except Exception as e:
            logger.warning("Error destroying session", exc_info=e, extra={
                "session_id": session_id
            })
            return False

    # ========== RATE LIMITING ==========

    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
        """
        Check if request is within rate limit
        Returns: (allowed: bool, remaining_requests: int)
        """
        if not self.redis_client:
            return True, limit  # Allow if Redis unavailable

        try:
            rate_key = f"{self.rate_limit_prefix}{identifier}:{int(datetime.utcnow().timestamp() / window_seconds)}"

            # Use Redis pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                pipe.incr(rate_key)
                pipe.expire(rate_key, window_seconds)
                results = await pipe.execute()

            current_count = results[0]

            if current_count > limit:
                logger.warning("Rate limit exceeded", extra={
                    "identifier": identifier,
                    "current_count": current_count,
                    "limit": limit,
                    "window_seconds": window_seconds
                })
                return False, 0

            remaining = limit - current_count
            return True, remaining

        except Exception as e:
            logger.warning("Error checking rate limit", exc_info=e, extra={
                "identifier": identifier
            })
            return True, limit  # Allow on error

    # ========== BACKGROUND JOB QUEUING ==========

    async def enqueue_job(self, queue_name: str, job_data: Dict[str, Any], priority: int = 0) -> str:
        """Add job to queue with priority"""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")

        job_id = hashlib.sha256(f"{queue_name}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

        try:
            job = {
                "job_id": job_id,
                "queue": queue_name,
                "data": job_data,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
                "status": "queued"
            }

            # Use sorted set for priority queue (lower score = higher priority)
            await self.redis_client.zadd(
                f"{self.job_queue_prefix}queue:{queue_name}",
                {json.dumps(job, default=str): priority}
            )

            logger.info("Job enqueued", extra={
                "job_id": job_id,
                "queue": queue_name,
                "priority": priority
            })

            return job_id

        except Exception as e:
            logger.error("Failed to enqueue job", exc_info=e, extra={
                "queue_name": queue_name,
                "priority": priority
            })
            raise

    async def dequeue_job(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Remove and return highest priority job from queue"""
        if not self.redis_client:
            return None

        try:
            # Get highest priority job (lowest score)
            result = await self.redis_client.zpopmin(f"{self.job_queue_prefix}queue:{queue_name}", 1)

            if result:
                job_data = json.loads(result[0][0])
                job_data["status"] = "processing"

                logger.info("Job dequeued", extra={
                    "job_id": job_data["job_id"],
                    "queue": queue_name
                })

                return job_data

            return None

        except Exception as e:
            logger.warning("Error dequeuing job", exc_info=e, extra={
                "queue_name": queue_name
            })
            return None

    async def get_queue_length(self, queue_name: str) -> int:
        """Get number of jobs in queue"""
        if not self.redis_client:
            return 0

        try:
            return await self.redis_client.zcard(f"{self.job_queue_prefix}queue:{queue_name}")
        except Exception as e:
            logger.warning("Error getting queue length", exc_info=e, extra={
                "queue_name": queue_name
            })
            return 0

    # ========== CACHE WARMING ==========

    async def warm_cache(self, endpoints: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Pre-populate cache with frequently accessed data
        endpoints: List of {"endpoint": str, "params": dict, "user_id": str}
        """
        if not self.redis_client:
            return {"warmed": 0, "errors": 0}

        warmed = 0
        errors = 0

        for endpoint_config in endpoints:
            try:
                # This would typically call the actual endpoint to get fresh data
                # For now, we'll simulate cache warming
                cache_key = self._generate_cache_key(
                    endpoint_config["endpoint"],
                    endpoint_config["params"],
                    endpoint_config.get("user_id")
                )

                # Set a placeholder with short TTL to indicate cache warming in progress
                await self.redis_client.setex(
                    cache_key,
                    30,  # 30 seconds to allow actual data to populate
                    json.dumps({"status": "warming"}, default=str)
                )

                warmed += 1

            except Exception as e:
                logger.warning("Error warming cache", exc_info=e, extra={
                    "endpoint": endpoint_config.get("endpoint")
                })
                errors += 1

        logger.info("Cache warming completed", extra={
            "endpoints_attempted": len(endpoints),
            "warmed": warmed,
            "errors": errors
        })

        return {"warmed": warmed, "errors": errors}

    # ========== MONITORING & METRICS ==========

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        if not self.redis_client:
            return {"status": "disconnected"}

        try:
            info = await self.redis_client.info()

            # Get cache key counts
            cache_keys = await self.redis_client.keys(f"{self.cache_prefix}*")
            session_keys = await self.redis_client.keys(f"{self.session_prefix}*")
            rate_limit_keys = await self.redis_client.keys(f"{self.rate_limit_prefix}*")
            job_keys = await self.redis_client.keys(f"{self.job_queue_prefix}*")

            return {
                "status": "connected",
                "cache_keys": len(cache_keys),
                "session_keys": len(session_keys),
                "rate_limit_keys": len(rate_limit_keys),
                "job_keys": len(job_keys),
                "total_keys": len(cache_keys) + len(session_keys) + len(rate_limit_keys) + len(job_keys),
                "redis_info": {
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_days": info.get("uptime_in_days")
                }
            }

        except Exception as e:
            logger.warning("Error getting cache stats", exc_info=e)
            return {"status": "error", "error": str(e)}

    async def clear_cache(self, pattern: str = "*") -> int:
        """Clear all cache keys matching pattern"""
        if not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(f"{self.cache_prefix}{pattern}")
            if keys:
                await self.redis_client.delete(*keys)
                logger.info("Cache cleared", extra={
                    "pattern": pattern,
                    "keys_deleted": len(keys)
                })
                return len(keys)
            return 0

        except Exception as e:
            logger.warning("Error clearing cache", exc_info=e, extra={
                "pattern": pattern
            })
            return 0

# Global cache service instance
redis_cache_service = RedisCacheService()
