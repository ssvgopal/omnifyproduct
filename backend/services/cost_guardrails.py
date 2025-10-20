"""
Cost Guardrails and Low-Cost Mode Middleware

Provides request rate limiting, per-tenant quotas, and cost-aware controls
to keep operational costs low. Designed to work without external services,
with optional Redis integration later.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional


class CostGuardrails:
    """
    Simple in-process cost guardrails with per-tenant counters.
    Not a replacement for a full rate limiter, but sufficient for
    low-cost single-instance deployments.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._enabled = os.getenv("LOW_COST_MODE", "false").lower() == "true"
        # Defaults are intentionally conservative
        self._rate_limit_rpm = int(os.getenv("RATE_LIMIT_RPM", "120"))
        self._quota_requests_per_day = int(os.getenv("QUOTA_REQUESTS_PER_DAY", "5000"))
        self._quota_tokens_per_day = int(os.getenv("QUOTA_TOKENS_PER_DAY", "250000"))
        self._monthly_cap_usd = float(os.getenv("COST_MONTHLY_CAP_USD", "25"))
        self._cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "600"))
        self._llm_default_model = os.getenv("LLM_DEFAULT_MODEL", "gpt-4o-mini")
        self._llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "512"))

        # Sliding window RPM counters: {key: [timestamps]}
        self._per_minute_times: Dict[str, list[float]] = {}
        # Daily quotas: {date_key: {tenant_key: counts}}
        self._daily_requests: Dict[str, Dict[str, int]] = {}
        self._daily_tokens: Dict[str, Dict[str, int]] = {}
        # Rough monthly cost tracker (user-provided estimates). Optional.
        self._monthly_cost_usd: float = 0.0

    def is_enabled(self) -> bool:
        return self._enabled

    def get_cost_aware_defaults(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "rate_limit_rpm": self._rate_limit_rpm,
            "quota_requests_per_day": self._quota_requests_per_day,
            "quota_tokens_per_day": self._quota_tokens_per_day,
            "monthly_cap_usd": self._monthly_cap_usd,
            "cache_ttl_seconds": self._cache_ttl_seconds,
            "llm_default_model": self._llm_default_model,
            "llm_max_tokens": self._llm_max_tokens,
        }

    async def allow_request(self, tenant_key: str) -> bool:
        if not self._enabled:
            return True

        now = time.time()
        minute_window_start = now - 60.0
        date_key = time.strftime("%Y-%m-%d", time.gmtime(now))

        async with self._lock:
            # Rate limit RPM
            times = self._per_minute_times.setdefault(tenant_key, [])
            # Drop entries older than 60s
            while times and times[0] < minute_window_start:
                times.pop(0)
            if len(times) >= self._rate_limit_rpm:
                return False
            times.append(now)

            # Daily request quota
            day_requests = self._daily_requests.setdefault(date_key, {}).setdefault(tenant_key, 0)
            if day_requests >= self._quota_requests_per_day:
                return False
            self._daily_requests[date_key][tenant_key] = day_requests + 1

        return True

    async def record_tokens(self, tenant_key: str, tokens: int) -> bool:
        """Record token usage; returns False if over quota in low-cost mode."""
        if not self._enabled:
            return True

        now = time.time()
        date_key = time.strftime("%Y-%m-%d", time.gmtime(now))
        async with self._lock:
            day_tokens = self._daily_tokens.setdefault(date_key, {}).setdefault(tenant_key, 0)
            if day_tokens + tokens > self._quota_tokens_per_day:
                return False
            self._daily_tokens[date_key][tenant_key] = day_tokens + tokens
        return True

    async def record_cost(self, usd_amount: float) -> bool:
        """Record rough cost; returns False if over monthly cap in low-cost mode."""
        if not self._enabled:
            return True
        async with self._lock:
            if self._monthly_cost_usd + usd_amount > self._monthly_cap_usd:
                return False
            self._monthly_cost_usd += usd_amount
        return True

    async def get_usage_snapshot(self, tenant_key: str) -> Dict[str, Any]:
        """Return approximate current usage and limits for a tenant."""
        now = time.time()
        minute_window_start = now - 60.0
        date_key = time.strftime("%Y-%m-%d", time.gmtime(now))

        async with self._lock:
            times = self._per_minute_times.get(tenant_key, []).copy()
            rpm = len([t for t in times if t >= minute_window_start])
            requests_today = self._daily_requests.get(date_key, {}).get(tenant_key, 0)
            tokens_today = self._daily_tokens.get(date_key, {}).get(tenant_key, 0)
            cost_month = self._monthly_cost_usd

        return {
            "enabled": self._enabled,
            "limits": {
                "rate_limit_rpm": self._rate_limit_rpm,
                "quota_requests_per_day": self._quota_requests_per_day,
                "quota_tokens_per_day": self._quota_tokens_per_day,
                "monthly_cap_usd": self._monthly_cap_usd,
                "llm_default_model": self._llm_default_model,
                "llm_max_tokens": self._llm_max_tokens,
            },
            "usage": {
                "current_rpm": rpm,
                "requests_today": requests_today,
                "tokens_today": tokens_today,
                "estimated_monthly_cost_usd": cost_month,
            },
            "remaining": {
                "rpm_remaining": max(self._rate_limit_rpm - rpm, 0),
                "requests_today_remaining": max(self._quota_requests_per_day - requests_today, 0),
                "tokens_today_remaining": max(self._quota_tokens_per_day - tokens_today, 0),
                "monthly_cost_remaining_usd": max(self._monthly_cap_usd - cost_month, 0.0),
            },
        }


# Global singleton for app-wide usage
cost_guardrails = CostGuardrails()


