# 💸 Low-Cost Mode (Cost Guardrails)

Low-Cost Mode reduces operational expenses by enforcing lightweight quotas, request rate limits, and cost-aware defaults across the platform. It is designed for early-stage deployments where keeping monthly spend minimal is critical (<$50/mo target).

## 🧩 What It Does
- Rate limits requests per tenant (RPM)
- Enforces daily per-tenant quotas (requests, estimated tokens)
- Applies cost-aware defaults (small LLM models, max tokens)
- Adds caching guidance for expensive endpoints
- Supports a soft monthly cost cap (best-effort)

## ⚙️ Enable It

1) Copy and edit environment configuration:
```bash
cp env.example .env
# Set LOW_COST_MODE=true and adjust limits as needed
```

2) Key variables:
```bash
LOW_COST_MODE=true
RATE_LIMIT_RPM=120
QUOTA_REQUESTS_PER_DAY=5000
QUOTA_TOKENS_PER_DAY=250000
COST_MONTHLY_CAP_USD=25
CACHE_TTL_SECONDS=600
LLM_DEFAULT_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=512
```

## 🏗️ How It Works
- A lightweight middleware in `backend/agentkit_server.py` checks per-tenant RPM and daily quotas using the in-process guardrails (`backend/services/cost_guardrails.py`).
- Tenant identity is derived from `X-Organization-Id`/`X-Tenant-Id` headers; falls back to client IP if missing.
- LLM usage should call `cost_guardrails.record_tokens(tenant, tokens)` and `cost_guardrails.record_cost(usd)` where applicable (extend gradually in LLM call sites).

## 🧪 Recommended Usage Patterns
- Cache expensive GET endpoints for 5–15 minutes (CDN + client-side memoization).
- Batch LLM calls and summarize early; cap max tokens.
- Prefer webhooks over polling for platform integrations.
- Schedule EYES analytics hourly/daily and serve stored results in UI.
- Gate premium features (AgentKit, advanced models) by plan.

## 🚨 Limits & Notes
- The in-process limits are approximate and best for a single-instance deployment. For multi-instance setups, use Redis-backed rate limiting.
- Monthly cost cap is best-effort; integrate with provider cost alerts for enforcement.
- For enterprise tenants, disable or loosen limits per plan.

## 📈 Upgrade Path
- Swap in Redis-based rate limiting and quotas when scaling.
- Add per-endpoint costs and route high-cost calls through stricter quotas.
- Implement token usage accounting in all LLM call sites.

## 📂 Files
- `backend/services/cost_guardrails.py` – guardrails implementation
- `backend/agentkit_server.py` – middleware wiring
- `env.example` – environment flags and defaults

With Low-Cost Mode enabled, you can operate lean while preserving production readiness and UX quality.


