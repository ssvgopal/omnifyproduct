# 🤖 Vibe Coder Implementation Prompts (10 October 2025)

## 📋 Overview

This document provides comprehensive, ready-to-use prompts for Vibe Coders (AI coding assistants) to implement Omnify Cloud Connect features. Each prompt is self-contained with context, requirements, and validation criteria.

---

## 🚀 AGENTKIT IMPLEMENTATION (RECOMMENDED - 4 WEEKS)

### **Prompt A1: AgentKit Foundation & Core Agents (Week 1)**

```
IMPLEMENTATION: AgentKit Foundation with 4 Core Agents

CONTEXT: Build Omnify Cloud Connect using OpenAI AgentKit for 70% cost reduction and 8x faster delivery.

REQUIREMENTS:
1. Setup: AgentKit environment, ChatGPT Enterprise, GoHighLevel SaaS Pro
2. Agent 1 - Creative Intelligence: AI creative repurposing, AIDA analysis, brand compliance
3. Agent 2 - Marketing Automation: Campaign management, multi-platform publishing, lead nurturing
4. Agent 3 - Client Management: Onboarding, billing (Stripe), success tracking
5. Agent 4 - Analytics: Real-time tracking, predictive analytics, ROI analysis

TECH STACK: OpenAI AgentKit, ChatGPT Enterprise ($30/user/month), GoHighLevel ($497/month)

DELIVERABLES: 4 operational agents, GoHighLevel integration, visual workflows, compliance setup

VALIDATION: All agents functional, GoHighLevel connected, workflows execute, compliance enabled

REFERENCES: analysis/OPENAI_AGENTKIT_INTEGRATION_ANALYSIS.md, gaps_analysis_10Oct.md

PRIORITY: CRITICAL | EFFORT: 1 week
```

### **Prompt A2: Advanced Agents & Enterprise Features (Week 2)**

```
IMPLEMENTATION: Advanced Agents + Enterprise Security

CONTEXT: Build 3 advanced agents for complex workflows and enterprise compliance.

REQUIREMENTS:
1. Agent 5 - Workflow Orchestration: Cross-agent coordination, error handling, optimization
2. Agent 6 - Compliance: SOC 2 monitoring, audit logging, security incident response
3. Agent 7 - Performance: Real-time monitoring, automated optimization, cost management
4. Enterprise: Multi-tenant security, audit logging, data retention, encryption

DELIVERABLES: 3 advanced agents, enterprise security, multi-tenant isolation, compliance validation

VALIDATION: Advanced agents operational, security audit passed, multi-tenancy working

PRIORITY: HIGH | EFFORT: 1 week
```

### **Prompt A3: Agent Orchestration & White-Label (Week 3)**

```
IMPLEMENTATION: Agent Orchestration + White-Label Platform

CONTEXT: Unify all 7 agents with white-label branding capabilities.

REQUIREMENTS:
1. Orchestration: Unified agent coordination, centralized monitoring, auto-scaling
2. White-Label: Custom branding, client portal, custom domains, SSL, mobile-responsive
3. Integration: Seamless GoHighLevel across agents, unified data flow, centralized auth

DELIVERABLES: Orchestration system, white-label platform, client portal, mobile UI

VALIDATION: Agents coordinate seamlessly, branding customizable, client portal functional

PRIORITY: HIGH | EFFORT: 1 week
```

### **Prompt A4: Production Deployment & Launch (Week 4)**

```
IMPLEMENTATION: Production Deployment + Public Launch

CONTEXT: Deploy to production and launch as first AgentKit-powered agency platform.

REQUIREMENTS:
1. Deployment: Production environment, security validation, load testing, monitoring
2. Launch Prep: Onboarding system, documentation, support, billing (Stripe), marketing
3. Go-Live: Production monitoring, client support, performance tracking, feedback collection

DELIVERABLES: Live platform, onboarding system, documentation, first clients onboarded

VALIDATION: Production stable, security passed, 99.9% uptime, clients using successfully

PRIORITY: CRITICAL | EFFORT: 1 week
```

---

## 🔌 PLATFORM INTEGRATIONS (8-12 WEEKS)

### **Prompt P1: Google Ads API Integration**

```
IMPLEMENTATION: Google Ads API Integration

REQUIREMENTS:
- OAuth2 authentication, campaign management, ad groups, keywords, bidding
- Performance metrics (CTR, CPC, ROAS), conversion tracking, budget management
- Automated bid optimization, quality score tracking

ENDPOINTS: POST/GET/PUT/DELETE /api/google-ads/campaigns, GET /api/google-ads/campaigns/{id}/metrics

TECH: Python FastAPI, google-ads-python, MongoDB, Redis caching

VALIDATION: OAuth working, campaigns manageable, metrics accurate, rate limiting handled

PRIORITY: CRITICAL | EFFORT: 2-3 weeks
```

### **Prompt P2: Meta Ads API Integration**

```
IMPLEMENTATION: Meta Ads (Facebook/Instagram) API

REQUIREMENTS:
- Facebook OAuth, campaign creation, ad sets, creative management
- Audience targeting, performance tracking, Facebook Pixel integration
- Image/video upload, carousel ads, stories ads

ENDPOINTS: POST/GET/PUT /api/meta-ads/campaigns, POST /api/meta-ads/creatives, GET /api/meta-ads/insights

TECH: Python FastAPI, facebook-business SDK, MongoDB, cloud storage

VALIDATION: OAuth working, campaigns created, creatives uploaded, insights accurate

PRIORITY: CRITICAL | EFFORT: 2-3 weeks
```

### **Prompt P3: GoHighLevel API Integration**

```
IMPLEMENTATION: GoHighLevel CRM & Marketing Automation

REQUIREMENTS:
- OAuth2, contact management, campaigns, workflows, email/SMS
- Pipeline management, appointments, communication history
- Webhook integration for real-time updates

ENDPOINTS: POST/GET/PUT/DELETE /api/gohighlevel/contacts, POST /api/gohighlevel/campaigns

TECH: Python FastAPI, requests, MongoDB, webhooks

VALIDATION: OAuth working, CRM functional, campaigns created, workflows execute

PRIORITY: CRITICAL | EFFORT: 2-3 weeks
```

### **Prompt P4: Shopify & Google Analytics**

```
IMPLEMENTATION: Shopify + Google Analytics Integration

REQUIREMENTS:
- Shopify: OAuth, product sync, order tracking, customer data, revenue attribution
- GA4: OAuth, event tracking, conversion tracking, funnel analysis, real-time data

ENDPOINTS: POST/GET /api/shopify/*, POST/GET /api/analytics/*

TECH: Python FastAPI, shopify-python-api, google-analytics-data, MongoDB

VALIDATION: Both OAuth working, data syncing, revenue attribution accurate

PRIORITY: HIGH | EFFORT: 2-3 weeks
```

---

## 🧠 CAMPAIGN INTELLIGENCE (8-10 WEEKS)

### **Prompt C1: Campaign Brief Analysis**

```
IMPLEMENTATION: AI-Powered Campaign Brief Analysis

REQUIREMENTS:
- Parse PDF/Word/text briefs, extract structured data
- Gap analysis, risk assessment, completeness scoring (0-100)
- AI insights using GPT-4, optimization recommendations

ENDPOINTS: POST /api/briefs, POST /api/briefs/{id}/analyze, GET /api/briefs/{id}/recommendations

TECH: Python FastAPI, PyPDF2, python-docx, OpenAI GPT-4, MongoDB

VALIDATION: Parses all formats, extracts accurately, scores reasonable, analysis <30s

PRIORITY: HIGH | EFFORT: 2-3 weeks
```

### **Prompt C2: Creative AIDA Analysis**

```
IMPLEMENTATION: Creative Asset Analysis (AIDA Framework)

REQUIREMENTS:
- Image/video analysis using OpenAI Vision + GPT-4
- AIDA scoring: Attention, Interest, Desire, Action (0-100 each)
- Creative fatigue detection, performance prediction, brand compliance

ENDPOINTS: POST /api/creatives, POST /api/creatives/{id}/analyze, GET /api/creatives/{id}/aida-score

TECH: Python FastAPI, OpenAI Vision API, GPT-4, FFmpeg, MongoDB

VALIDATION: Analyzes images/videos, AIDA scores consistent, recommendations actionable

PRIORITY: HIGH | EFFORT: 2-3 weeks
```

### **Prompt C3: Multi-Platform Analytics & Attribution**

```
IMPLEMENTATION: Unified Analytics + Attribution Modeling

REQUIREMENTS:
- Cross-platform metric normalization, unified ROAS/CTR/CPC/CPM
- Attribution models: first-touch, last-touch, linear, time-decay, position-based
- Budget optimization, ROAS optimization, scaling opportunities

ENDPOINTS: GET /api/analytics/unified, POST /api/attribution/calculate, GET /api/optimization/budget

TECH: Python FastAPI, pandas, numpy, scikit-learn, MongoDB, TimescaleDB, Redis

VALIDATION: Metrics normalized, attribution accurate, optimization recommendations valid

PRIORITY: HIGH | EFFORT: 3-4 weeks
```

---

## 🤖 AUTOMATION & WORKFLOW (6-8 WEEKS)

### **Prompt W1: Automated Campaign Deployment**

```
IMPLEMENTATION: Automated Campaign Deployment System

REQUIREMENTS:
- Template-based campaign creation, multi-platform deployment
- Automated bid management, budget pacing, creative rotation
- Audience targeting automation, campaign scheduling

ENDPOINTS: POST /api/automation/campaigns, POST /api/automation/bids, POST /api/automation/schedule

TECH: Python FastAPI, Celery, RabbitMQ, MongoDB

VALIDATION: Campaigns deploy successfully, bids optimize, budget paces correctly

PRIORITY: MEDIUM | EFFORT: 3-4 weeks
```

### **Prompt W2: Real-Time Monitoring & Alerting**

```
IMPLEMENTATION: Real-Time Monitoring + Escalation System

REQUIREMENTS:
- Continuous performance tracking, WebSocket real-time updates
- Threshold-based alerting, multi-channel notifications (email, SMS, Slack)
- Escalation workflows, automated interventions, emergency pause

ENDPOINTS: GET /api/monitoring/realtime, POST /api/alerts/configure, POST /api/alerts/escalate

TECH: Python FastAPI, WebSocket, Celery, Redis, Twilio, SendGrid, Slack API

VALIDATION: Alerts trigger within 5 minutes, interventions prevent losses, escalation works

PRIORITY: MEDIUM | EFFORT: 2-3 weeks
```

---

## 📊 ANALYTICS & REPORTING (6-8 WEEKS)

### **Prompt R1: Executive Dashboard**

```
IMPLEMENTATION: Interactive Executive Dashboard

REQUIREMENTS:
- Real-time data visualization, interactive charts (Chart.js/D3.js)
- Customizable widgets, drag-and-drop builder, role-specific templates
- Mobile-responsive, dashboard sharing, export capabilities

TECH: React 19, TypeScript, Chart.js/D3.js, TailwindCSS, shadcn/ui

VALIDATION: Dashboard loads <3s, interactive, customizable, mobile-responsive

PRIORITY: HIGH | EFFORT: 3-4 weeks
```

### **Prompt R2: Template-Driven Reporting**

```
IMPLEMENTATION: Report Builder + Pre-Built Templates

REQUIREMENTS:
- Drag-and-drop report builder, scheduled generation
- Multi-format export (PDF, Excel, CSV, PowerPoint), email distribution
- Pre-built templates: Multi-Platform Analysis, Creative Performance, ROI Analysis

ENDPOINTS: POST /api/reports, POST /api/reports/schedule, GET /api/reports/{id}/export

TECH: Python FastAPI, ReportLab (PDF), openpyxl (Excel), python-pptx, Celery

VALIDATION: Reports generate correctly, exports work, scheduled delivery on time

PRIORITY: HIGH | EFFORT: 3-4 weeks
```

---

## 🏗️ INFRASTRUCTURE (4-6 WEEKS)

### **Prompt I1: Docker & CI/CD**

```
IMPLEMENTATION: Docker Containerization + CI/CD Pipeline

REQUIREMENTS:
- Dockerfiles (backend, frontend), docker-compose (dev, prod), multi-stage builds
- GitHub Actions: automated testing, code quality, security scanning, deployment
- Environment management (dev, staging, prod), rollback capabilities

DELIVERABLES: Dockerfiles, docker-compose.yml, .github/workflows/*.yml

VALIDATION: Containers run locally, CI/CD deploys to staging, tests pass

PRIORITY: CRITICAL | EFFORT: 1-2 weeks
```

### **Prompt I2: Database & Caching**

```
IMPLEMENTATION: MongoDB Schema + Redis Caching

REQUIREMENTS:
- Complete MongoDB schema with migrations, indexes, constraints
- Redis caching for API responses, session management, cache invalidation
- Backup automation, point-in-time recovery, query optimization

DELIVERABLES: MongoDB schema, migration scripts, Redis configuration

VALIDATION: Schema complete, migrations work, cache hit rate >70%, backups automated

PRIORITY: CRITICAL | EFFORT: 2-3 weeks
```

### **Prompt I3: Background Jobs & Monitoring**

```
IMPLEMENTATION: Celery + Monitoring Stack

REQUIREMENTS:
- Celery + RabbitMQ for background jobs, scheduled tasks, retry logic
- Sentry for error tracking, DataDog/New Relic for APM, log aggregation
- Custom monitoring dashboards, alert configuration

DELIVERABLES: Celery setup, monitoring configuration, dashboards

VALIDATION: Background jobs process, monitoring comprehensive, alerts configured

PRIORITY: CRITICAL | EFFORT: 1-2 weeks
```

---

## 🔒 SECURITY & COMPLIANCE (3-4 WEEKS)

### **Prompt S1: Enhanced Authentication**

```
IMPLEMENTATION: OAuth2 + MFA + Social Login

REQUIREMENTS:
- OAuth2 with refresh tokens, multi-factor authentication (TOTP)
- Social login (Google, Facebook, LinkedIn), password policies
- Session management, email verification, password reset

TECH: Python FastAPI, PyJWT, pyotp, OAuth libraries

VALIDATION: OAuth working, MFA functional, social login works, sessions secure

PRIORITY: CRITICAL | EFFORT: 2 weeks
```

### **Prompt S2: API Security & Compliance**

```
IMPLEMENTATION: API Key Management + Rate Limiting + Audit Logging

REQUIREMENTS:
- HashiCorp Vault or AWS Secrets Manager for API keys
- Per-user/plan rate limiting, DDoS protection, encryption at rest/transit
- Comprehensive audit logging, GDPR compliance features

TECH: Python FastAPI, Vault/AWS Secrets, Redis, TLS/SSL

VALIDATION: Keys secure, rate limiting works, audit logs comprehensive, GDPR compliant

PRIORITY: CRITICAL | EFFORT: 2-3 weeks
```

---

## 🎨 FRONTEND UI (8-10 WEEKS)

### **Prompt F1: Campaign Management UI**

```
IMPLEMENTATION: Campaign Management Interface

REQUIREMENTS:
- Campaign list with filters/sorting, detail view, creation wizard
- Campaign editing, duplication, archiving, bulk operations
- Performance overview, quick actions, templates

TECH: React 19, TypeScript, TailwindCSS, shadcn/ui, React Query

VALIDATION: UI intuitive, all operations work, performance optimized, mobile-responsive

PRIORITY: HIGH | EFFORT: 3-4 weeks
```

### **Prompt F2: Creative Asset Library**

```
IMPLEMENTATION: Creative Asset Library

REQUIREMENTS:
- Asset upload, grid view, preview/lightbox, editing
- Tagging, search/filtering, versioning, performance tracking
- Bulk operations, download, sharing

TECH: React 19, TypeScript, TailwindCSS, shadcn/ui, React Dropzone

VALIDATION: Upload works, preview functional, search accurate, performance good

PRIORITY: HIGH | EFFORT: 2-3 weeks
```

### **Prompt F3: Settings & Configuration**

```
IMPLEMENTATION: Settings & Configuration UI

REQUIREMENTS:
- Account settings, profile management, team management
- Integration configuration, billing/subscription, notification preferences
- Security settings, API keys, white-label configuration

TECH: React 19, TypeScript, TailwindCSS, shadcn/ui, React Hook Form

VALIDATION: All settings functional, changes persist, UI intuitive

PRIORITY: HIGH | EFFORT: 2-3 weeks
```

---

## 📋 USAGE INSTRUCTIONS

### **For Cursor/Windsurf/Aider:**
1. Copy entire prompt including context and requirements
2. Paste into AI coding assistant
3. Let AI generate implementation
4. Review and test generated code
5. Iterate based on validation criteria

### **For Sequential Implementation:**
1. Start with AgentKit prompts (A1-A4) for fastest delivery
2. Or start with Infrastructure (I1-I3) for traditional approach
3. Then Platform Integrations (P1-P4)
4. Then Campaign Intelligence (C1-C3)
5. Then Automation (W1-W2)
6. Then Analytics (R1-R2)
7. Finally Frontend (F1-F3)

### **Testing Strategy:**
- Each prompt includes validation criteria
- Write tests before implementation (TDD)
- Target >80% code coverage
- Integration tests for all API endpoints
- E2E tests for critical user flows

---

## 🎯 RECOMMENDATION

**Start with AgentKit Prompts (A1-A4)** for:
- 4-week delivery vs 8-11 months
- 70% cost reduction
- Built-in enterprise compliance
- First-mover advantage

**Fallback to Traditional Prompts** if AgentKit access delayed.

---

**Document Version**: 1.0  
**Date**: 10 October 2025  
**Status**: Ready for Implementation
