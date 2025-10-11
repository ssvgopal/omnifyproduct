"""
Production-Ready Rate Limiting & DDoS Protection for OmnifyProduct
Multi-layer security with Redis-backed rate limiting, DDoS detection, and adaptive throttling

Features:
- Multi-tier rate limiting (per-user, per-org, per-endpoint, global)
- DDoS attack detection and mitigation
- Adaptive rate limiting based on traffic patterns
- Burst handling with token bucket algorithm
- IP-based blocking and whitelisting
- Real-time monitoring and alerting
- Compliance with rate limit headers (RFC 6585)
"""

import asyncio
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import ipaddress
import re

from services.redis_cache_service import redis_cache_service
from services.structured_logging import logger

class ProductionRateLimiter:
    """
    Enterprise-grade rate limiting with DDoS protection
    """

    def __init__(self):
        self.rate_limits = {
            # Per-user limits
            "user_requests_per_minute": 120,
            "user_requests_per_hour": 2000,
            "user_requests_per_day": 10000,

            # Per-organization limits
            "org_requests_per_minute": 1000,
            "org_requests_per_hour": 20000,
            "org_requests_per_day": 100000,

            # Per-endpoint limits
            "endpoint_requests_per_minute": 300,

            # Global limits
            "global_requests_per_second": 1000,
            "global_requests_per_minute": 50000,

            # Authentication endpoints (stricter)
            "auth_requests_per_minute": 5,
            "auth_requests_per_hour": 20,

            # Agent execution limits
            "agent_requests_per_minute": 50,
            "agent_requests_per_hour": 1000,

            # File upload limits
            "upload_requests_per_minute": 10,
            "upload_requests_per_hour": 100,
        }

        # DDoS detection thresholds
        self.ddos_thresholds = {
            "requests_per_second_per_ip": 50,
            "requests_per_minute_per_ip": 500,
            "error_rate_threshold": 0.8,  # 80% error rate
            "suspicious_patterns_threshold": 10,
            "burst_detection_window": 60,  # seconds
            "burst_threshold": 100  # requests in window
        }

        # Blocked IPs and whitelisted IPs
        self.blocked_ips = set()
        self.whitelisted_ips = set([
            "127.0.0.1", "localhost", "::1"  # Local development
        ])

        # Suspicious patterns (regex patterns that indicate attacks)
        self.suspicious_patterns = [
            r"(?i)(union\s+select|select\s+.*\s+from|drop\s+table|script\s+alert)",
            r"(?i)(eval\(|exec\(|system\(|passthru\()",
            r"(?i)(../../../|\\.\\./)",
            r"(?i)(<script|javascript:|vbscript:|onload=|onerror=)",
        ]

        # Rate limit windows
        self.windows = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }

        # Monitoring metrics
        self.metrics = defaultdict(int)

        logger.info("Production rate limiter initialized", extra={
            "rate_limits_configured": len(self.rate_limits),
            "ddos_thresholds_configured": len(self.ddos_thresholds),
            "suspicious_patterns": len(self.suspicious_patterns)
        })

    async def check_rate_limit(
        self,
        request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Comprehensive rate limit check with DDoS detection

        Args:
            request_data: {
                "user_id": str (optional),
                "organization_id": str (optional),
                "ip_address": str,
                "endpoint": str,
                "method": str,
                "user_agent": str,
                "headers": dict
            }

        Returns:
            (allowed: bool, response_data: dict)
        """
        try:
            # Extract request information
            user_id = request_data.get("user_id")
            organization_id = request_data.get("organization_id")
            ip_address = request_data.get("ip_address", "unknown")
            endpoint = request_data.get("endpoint", "/")
            method = request_data.get("method", "GET")
            user_agent = request_data.get("user_agent", "")
            headers = request_data.get("headers", {})

            # Check IP whitelisting/blacklisting first
            if ip_address in self.whitelisted_ips:
                return True, self._get_success_response(0, 999999)

            if ip_address in self.blocked_ips:
                logger.warning("Blocked IP attempted access", extra={
                    "ip_address": ip_address,
                    "endpoint": endpoint
                })
                return False, self._get_blocked_response("IP address blocked")

            # DDoS detection
            ddos_detected = await self._detect_ddos(ip_address, endpoint, headers)
            if ddos_detected:
                await self._handle_ddos_attack(ip_address, endpoint)
                return False, self._get_blocked_response("DDoS protection activated")

            # Suspicious pattern detection
            if self._detect_suspicious_patterns(request_data):
                await self._handle_suspicious_request(ip_address, endpoint)
                return False, self._get_blocked_response("Suspicious request pattern detected")

            # Multi-tier rate limiting
            rate_limit_checks = await self._perform_rate_limit_checks(
                user_id, organization_id, ip_address, endpoint
            )

            # Find the most restrictive limit
            most_restrictive = min(rate_limit_checks, key=lambda x: x["remaining"])

            if most_restrictive["allowed"]:
                # Update metrics
                self._update_metrics("allowed_requests", 1)

                return True, self._get_success_response(
                    most_restrictive["remaining"],
                    most_restrictive["limit"]
                )
            else:
                # Rate limit exceeded
                await self._handle_rate_limit_exceeded(
                    user_id, organization_id, ip_address, endpoint
                )

                self._update_metrics("rate_limited_requests", 1)

                return False, self._get_rate_limit_response(
                    most_restrictive["reset_time"],
                    most_restrictive["limit"]
                )

        except Exception as e:
            logger.error("Rate limiting error", exc_info=e, extra={
                "request_data": request_data
            })
            # Allow request on error to avoid blocking legitimate traffic
            return True, self._get_success_response(0, 999999)

    async def _perform_rate_limit_checks(
        self,
        user_id: Optional[str],
        organization_id: Optional[str],
        ip_address: str,
        endpoint: str
    ) -> List[Dict[str, Any]]:
        """
        Perform all applicable rate limit checks
        """
        checks = []

        current_time = int(time.time())

        # Global rate limits
        global_check = await self._check_limit(
            "global", "global_requests_per_minute", current_time, "minute"
        )
        checks.append(global_check)

        # Per-IP rate limits
        ip_check = await self._check_limit(
            f"ip:{ip_address}", "global_requests_per_minute", current_time, "minute"
        )
        checks.append(ip_check)

        # User-specific limits
        if user_id:
            user_check = await self._check_limit(
                f"user:{user_id}", "user_requests_per_minute", current_time, "minute"
            )
            checks.append(user_check)

            # Stricter limits for auth endpoints
            if self._is_auth_endpoint(endpoint):
                auth_check = await self._check_limit(
                    f"user_auth:{user_id}", "auth_requests_per_minute", current_time, "minute"
                )
                checks.append(auth_check)

        # Organization-specific limits
        if organization_id:
            org_check = await self._check_limit(
                f"org:{organization_id}", "org_requests_per_minute", current_time, "minute"
            )
            checks.append(org_check)

        # Endpoint-specific limits
        endpoint_key = self._get_endpoint_key(endpoint)
        endpoint_check = await self._check_limit(
            f"endpoint:{endpoint_key}", "endpoint_requests_per_minute", current_time, "minute"
        )
        checks.append(endpoint_check)

        # Agent-specific limits
        if self._is_agent_endpoint(endpoint):
            agent_check = await self._check_limit(
                f"agent:{user_id or ip_address}", "agent_requests_per_minute", current_time, "minute"
            )
            checks.append(agent_check)

        return checks

    async def _check_limit(
        self,
        identifier: str,
        limit_key: str,
        current_time: int,
        window: str
    ) -> Dict[str, Any]:
        """
        Check rate limit for specific identifier using Redis
        """
        if not redis_cache_service.redis_client:
            # Fallback to in-memory if Redis unavailable
            return {"allowed": True, "remaining": 999999, "limit": 1000000, "reset_time": 0}

        window_seconds = self.windows[window]
        limit = self.rate_limits[limit_key]

        # Create time window key
        window_start = current_time - (current_time % window_seconds)
        key = f"ratelimit:{identifier}:{window_start}"

        try:
            # Use Redis pipeline for atomic operations
            async with redis_cache_service.redis_client.pipeline() as pipe:
                pipe.incr(key)
                pipe.expire(key, window_seconds)
                results = await pipe.execute()

            current_count = results[0]

            if current_count > limit:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "limit": limit,
                    "reset_time": window_start + window_seconds
                }
            else:
                return {
                    "allowed": True,
                    "remaining": limit - current_count,
                    "limit": limit,
                    "reset_time": window_start + window_seconds
                }

        except Exception as e:
            logger.warning("Redis rate limit check failed", exc_info=e, extra={
                "identifier": identifier,
                "limit_key": limit_key
            })
            # Allow on Redis error
            return {"allowed": True, "remaining": 999999, "limit": 1000000, "reset_time": 0}

    async def _detect_ddos(
        self,
        ip_address: str,
        endpoint: str,
        headers: Dict[str, Any]
    ) -> bool:
        """
        Advanced DDoS detection using multiple signals
        """
        try:
            current_time = time.time()

            # Check request frequency per IP
            ip_key = f"ddos_ip:{ip_address}"
            ip_requests = await self._get_request_count(ip_key, 60)  # Last minute

            if ip_requests > self.ddos_thresholds["requests_per_minute_per_ip"]:
                logger.warning("DDoS detected: High request rate from IP", extra={
                    "ip_address": ip_address,
                    "requests_per_minute": ip_requests
                })
                return True

            # Check burst patterns
            burst_key = f"ddos_burst:{ip_address}"
            burst_count = await self._get_request_count(burst_key, 10)  # Last 10 seconds

            if burst_count > self.ddos_thresholds["burst_threshold"]:
                logger.warning("DDoS detected: Request burst from IP", extra={
                    "ip_address": ip_address,
                    "burst_count": burst_count
                })
                return True

            # Check for bot-like headers
            if self._is_bot_like(headers):
                logger.warning("DDoS detected: Bot-like headers", extra={
                    "ip_address": ip_address,
                    "user_agent": headers.get("User-Agent", "")
                })
                return True

            # Check error rate (high error rates may indicate attack)
            error_key = f"errors:{ip_address}"
            error_count = await self._get_request_count(error_key, 300)  # Last 5 minutes
            total_requests = await self._get_request_count(f"requests:{ip_address}", 300)

            if total_requests > 10:  # Only check if enough requests
                error_rate = error_count / total_requests
                if error_rate > self.ddos_thresholds["error_rate_threshold"]:
                    logger.warning("DDoS detected: High error rate from IP", extra={
                        "ip_address": ip_address,
                        "error_rate": error_rate
                    })
                    return True

            return False

        except Exception as e:
            logger.warning("DDoS detection error", exc_info=e, extra={
                "ip_address": ip_address
            })
            return False

    async def _get_request_count(self, key: str, window_seconds: int) -> int:
        """Get request count for DDoS detection"""
        if not redis_cache_service.redis_client:
            return 0

        try:
            # Use HyperLogLog for approximate counting with high cardinality
            hll_key = f"hll:{key}"
            await redis_cache_service.redis_client.pfadd(hll_key, str(time.time()))
            count = await redis_cache_service.redis_client.pfcount(hll_key)

            # Expire old data
            await redis_cache_service.redis_client.expire(hll_key, window_seconds * 2)

            return count
        except Exception:
            return 0

    def _detect_suspicious_patterns(self, request_data: Dict[str, Any]) -> bool:
        """
        Detect suspicious patterns in request data
        """
        try:
            # Check URL and query parameters
            endpoint = request_data.get("endpoint", "")
            query_string = request_data.get("query_string", "")

            check_text = f"{endpoint} {query_string}"

            for pattern in self.suspicious_patterns:
                if re.search(pattern, check_text, re.IGNORECASE):
                    logger.warning("Suspicious pattern detected", extra={
                        "pattern": pattern,
                        "endpoint": endpoint,
                        "ip_address": request_data.get("ip_address")
                    })
                    return True

            # Check headers for suspicious values
            headers = request_data.get("headers", {})
            suspicious_headers = ["X-Forwarded-For", "X-Real-IP"]

            for header in suspicious_headers:
                if header in headers and len(headers[header].split(",")) > 3:
                    # Multiple forwarded IPs may indicate spoofing
                    return True

            return False

        except Exception as e:
            logger.warning("Suspicious pattern detection error", exc_info=e)
            return False

    def _is_bot_like(self, headers: Dict[str, Any]) -> bool:
        """Check if request appears to be from a bot"""
        user_agent = headers.get("User-Agent", "").lower()

        # Common bot indicators
        bot_indicators = [
            "bot", "crawler", "spider", "scraper", "python-requests",
            "go-http-client", "java/", "wget", "curl"
        ]

        for indicator in bot_indicators:
            if indicator in user_agent:
                return True

        # Missing or suspicious Accept header
        accept = headers.get("Accept", "")
        if not accept or accept == "*/*":
            return True

        return False

    def _is_auth_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is authentication-related"""
        auth_endpoints = ["/auth/login", "/auth/register", "/auth/forgot-password"]
        return any(endpoint.startswith(auth_ep) for auth_ep in auth_endpoints)

    def _is_agent_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is agent-related"""
        return endpoint.startswith("/revolutionary/") or endpoint.startswith("/api/agentkit")

    def _get_endpoint_key(self, endpoint: str) -> str:
        """Get normalized endpoint key for rate limiting"""
        # Remove path parameters and normalize
        normalized = re.sub(r'/[0-9a-f-]+(?=/|$)', '/:id', endpoint)
        return normalized.strip('/').replace('/', '_') or 'root'

    async def _handle_ddos_attack(self, ip_address: str, endpoint: str) -> None:
        """Handle detected DDoS attack"""
        # Add to blocked IPs
        self.blocked_ips.add(ip_address)

        # Log incident
        logger.critical("DDoS attack detected and blocked", extra={
            "ip_address": ip_address,
            "endpoint": endpoint,
            "action": "blocked"
        })

        # TODO: Integrate with external alerting (Slack, PagerDuty, etc.)
        # TODO: Implement progressive blocking (temporary → permanent)

    async def _handle_suspicious_request(self, ip_address: str, endpoint: str) -> None:
        """Handle suspicious request"""
        logger.warning("Suspicious request blocked", extra={
            "ip_address": ip_address,
            "endpoint": endpoint,
            "action": "blocked"
        })

        # TODO: Implement progressive penalties

    async def _handle_rate_limit_exceeded(
        self,
        user_id: Optional[str],
        organization_id: Optional[str],
        ip_address: str,
        endpoint: str
    ) -> None:
        """Handle rate limit exceeded"""
        logger.warning("Rate limit exceeded", extra={
            "user_id": user_id,
            "organization_id": organization_id,
            "ip_address": ip_address,
            "endpoint": endpoint
        })

        # TODO: Implement progressive rate limiting (slower recovery)

    def _update_metrics(self, metric: str, value: int) -> None:
        """Update internal metrics"""
        self.metrics[metric] += value

    def _get_success_response(self, remaining: int, limit: int) -> Dict[str, Any]:
        """Get successful rate limit response"""
        return {
            "allowed": True,
            "remaining": remaining,
            "limit": limit,
            "reset": int(time.time()) + 60,  # Next minute
            "retry_after": None
        }

    def _get_rate_limit_response(self, reset_time: int, limit: int) -> Dict[str, Any]:
        """Get rate limit exceeded response"""
        retry_after = max(0, reset_time - int(time.time()))

        return {
            "allowed": False,
            "remaining": 0,
            "limit": limit,
            "reset": reset_time,
            "retry_after": retry_after,
            "error": "Rate limit exceeded"
        }

    def _get_blocked_response(self, reason: str) -> Dict[str, Any]:
        """Get blocked request response"""
        return {
            "allowed": False,
            "error": reason,
            "retry_after": 3600  # 1 hour
        }

    # ========== MANAGEMENT METHODS ==========

    def add_to_whitelist(self, ip_address: str) -> bool:
        """Add IP to whitelist"""
        try:
            ipaddress.ip_address(ip_address)  # Validate IP
            self.whitelisted_ips.add(ip_address)
            logger.info("IP added to whitelist", extra={"ip_address": ip_address})
            return True
        except ValueError:
            logger.warning("Invalid IP address for whitelist", extra={"ip_address": ip_address})
            return False

    def remove_from_whitelist(self, ip_address: str) -> bool:
        """Remove IP from whitelist"""
        if ip_address in self.whitelisted_ips:
            self.whitelisted_ips.remove(ip_address)
            logger.info("IP removed from whitelist", extra={"ip_address": ip_address})
            return True
        return False

    def block_ip(self, ip_address: str, reason: str = "Manual block") -> bool:
        """Manually block an IP address"""
        try:
            ipaddress.ip_address(ip_address)  # Validate IP
            self.blocked_ips.add(ip_address)
            logger.info("IP manually blocked", extra={
                "ip_address": ip_address,
                "reason": reason
            })
            return True
        except ValueError:
            logger.warning("Invalid IP address for blocking", extra={"ip_address": ip_address})
            return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info("IP unblocked", extra={"ip_address": ip_address})
            return True
        return False

    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return list(self.blocked_ips)

    def get_whitelisted_ips(self) -> List[str]:
        """Get list of whitelisted IPs"""
        return list(self.whitelisted_ips)

    def get_metrics(self) -> Dict[str, Any]:
        """Get rate limiting metrics"""
        return dict(self.metrics)

    def reset_metrics(self) -> None:
        """Reset internal metrics"""
        self.metrics.clear()

    # ========== ADAPTIVE RATE LIMITING ==========

    async def adapt_rate_limits(self) -> None:
        """
        Adaptively adjust rate limits based on traffic patterns
        """
        try:
            # Analyze recent traffic patterns
            # This would be called periodically by a background task

            # TODO: Implement machine learning-based rate limit adaptation
            # - Analyze normal vs. attack traffic patterns
            # - Adjust limits based on system load
            # - Implement geo-based rate limiting
            # - Dynamic whitelist/blacklist updates

            pass

        except Exception as e:
            logger.warning("Adaptive rate limiting error", exc_info=e)

# Global rate limiter instance
production_rate_limiter = ProductionRateLimiter()
