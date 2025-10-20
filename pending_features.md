# Pending Features and Implementation Plan

This document captures gaps across the end-to-end user flow and how to implement them.

## 1) Onboarding & Auth
- Gaps
  - Email verification, password reset, MFA, Social/SSO (OIDC)
  - Per-tenant RBAC with resource-level permissions and admin UI
  - Session management: device list, revocation, idle/absolute TTL
  - Org lifecycle: invites, team roles, plan upgrades/downgrades
- How to implement
  - Add endpoints: `POST /auth/register`, `POST /auth/verify`, `POST /auth/reset` (tokens via SES/Resend)
  - Integrate OIDC (Auth0/Okta) adapters; store `sub` and map to tenant roles
  - Create `sessions` collection; add revoke endpoints; Redis-backed session cache
  - Build `organizations/{id}/invites` endpoints + UI wizard; add role editor and plan switch flows

## 2) Tenant Isolation & Data Model
- Gaps
  - Consistent enforcement of `organization_id` on all reads/writes
  - Data migrations/versioning, soft-deletes, PII minimization
  - Demo/seed data per vertical
- How to implement
  - Add dependency `get_tenant_context` middleware; validate org on every repo call
  - Introduce `migrations/` with simple migrator; add `deleted_at` and `data_retention_days`
  - Provide `seed:<vertical>` scripts to populate demo data

## 3) Integrations & Webhooks
- Gaps
  - Guided “Connect Platforms” wizard; scope checks and sandbox mode
  - Webhook framework: verification, retries, idempotency, DLQ
  - Coverage gaps: GA4, HubSpot, Salesforce, TikTok/YouTube Ads
  - Sync strategy: delta/backfill, pagination resumability
- How to implement
  - Frontend wizard with step checks; backend `/integrations/*/connect/test`
  - Webhook module: HMAC verify, retry with backoff, idempotency keys, DLQ collection
  - Implement GA4 (Measurement/Data API), HubSpot CRM, Salesforce REST; add TikTok/YouTube Ads basic reads
  - Add sync jobs (Celery) with checkpoints cursors; store `next_page_token` per account

## 4) Brain Modules & ML Lifecycle
- Gaps
  - ORACLE/VOICE/CURIOSITY/MEMORY/REFLEXES/FACE not implemented
  - EYES: complete data loaders, feature store, retraining cadence
  - Model versioning, drift detection, A/B, canary rollouts, registry
  - Acceptance metrics reporting (AUC, Silhouette, latency)
- How to implement
  - Implement each module service + API + UI; define input/output schemas
  - Add feature store collections; schedulers for retrain; store `model_version`
  - Integrate model registry (MLflow-like simple collection) and drift monitors
  - Persist metrics per model/run; FACE dashboard to visualize trends

## 5) API Hygiene & Performance
- Gaps
  - Strict schema validation/sanitization and idempotency for POSTs
  - Standard pagination/filtering; consistent defaults
  - Per-endpoint caching (ETag/Last-Modified), stale-while-revalidate pattern
- How to implement
  - Pydantic models for all routes; sanitizer utilities for strings/HTML
  - Idempotency keys via `Idempotency-Key` header + store request hashes
  - Add response validators; unify pagination params; add ETag hashing

## 6) Cost & FinOps
- Gaps
  - Per-tenant cost dashboard; alert thresholds by plan
  - Plan-aware quotas; admin overrides
  - LLM optimization (prompt/result caching, embeddings dedupe, batching)
- How to implement
  - Create `/admin/costs` endpoints + UI; aggregate costs by tenant
  - Policy engine mapping plans → quotas; override UI
  - Redis cache for prompts/results; content hashing; batch job runners

## 7) Frontend & UX
- Gaps
  - Guided onboarding checklist; empty states; error/edge UX
  - Accessibility audit (WCAG); keyboard navigation; focus states
  - PERFORMANCE: code-splitting, lazy-loading, skeletons, client cache hooks
  - FACE dashboard: single-page exec insights with KPIs
- How to implement
  - Add `OnboardingChecklist` component + route guards
  - Run axe-core audit, add roles/aria, focus management utilities
  - Configure route-based chunks, suspense + skeletons, SWR/React Query caching
  - Build FACE page with cross-module KPIs and alerts

## 8) Billing & Plans
- Gaps
  - Stripe subscriptions wiring: webhooks (invoice, payment, cancel), proration
  - Feature gating by plan; seat-based pricing
- How to implement
  - Implement Stripe webhook handlers; sync subscription state to tenant
  - Feature flags by plan; middleware checks; seat/licensing counter per org

## 9) Observability & Ops
- Gaps
  - OpenTelemetry tracing; dashboards; SLO alerts
  - Backups/DR; restore drills; secrets rotation
- How to implement
  - Add OTEL SDK, traces to key routes; Grafana dashboards & alerts
  - MongoDB backups; restore runbook; integrate KMS or secret manager with rotation

## 10) Security & Compliance
- Gaps
  - DPA/retention policies; PII mapping; field encryption
  - Expanded audit logs (auth, config, exports, admin actions)
- How to implement
  - Policy docs + retention workers; AES-GCM field encryption for sensitive data
  - Audit middleware and sinks; searchable admin audit UI

## 11) Testing & Quality
- Gaps
  - E2E (Playwright/Cypress), contract tests, load/security tests
  - Sandbox “demo mode” with redacted data
- How to implement
  - Add E2E suite; Pact/contract tests for integrations; k6/Gatling load tests; ZAP/DAST scans
  - Demo toggle with simulated safe integrations and masked data

## 12) Deployment & Delivery
- Gaps
  - Quality gates (coverage/lint/type-check), staged promotions
  - Progressive delivery (canary/blue-green)
- How to implement
  - CI: add coverage thresholds, mypy/ruff/black; manual approval for prod
  - Add Argo Rollouts or Helm canary strategy; health criteria-based promotion

---

### Immediate Priorities (Phase 1)
1. Validation + Idempotency + Pagination standardization
2. Guided Onboarding + Invitations + Email verification/reset
3. Plan-aware quotas and cost dashboard
4. EYES full pipeline + FACE dashboard MVP

### Deliverables by Phase
- Phase 1 (2–3 weeks): Safety/UX foundations + EYES/Face MVP
- Phase 2 (3–4 weeks): Stripe subscriptions + GA4/HubSpot + ORACLE
- Phase 3 (4–6 weeks): Observability/Security hardening + VOICE/CURIOSITY
