# Omnify AI Marketing Brain - Gap Analysis & Implementation Roadmap

**Analysis Date**: November 23, 2025  
**Requirements Source**: Comprehensive Requirements Document V3 (240 requirements)  
**Current Codebase**: Omnify Cloud Connect Platform  

---

## EXECUTIVE SUMMARY

### Critical Finding: **ARCHITECTURAL MISMATCH**

The existing codebase (Omnify Cloud Connect) is a **GENERAL MARKETING AUTOMATION PLATFORM** with AgentKit integration, while the requirements document defines a **SPECIALIZED AI MARKETING INTELLIGENCE LAYER** focused on attribution, prediction, and budget optimization for DTC brands.

**Gap Severity**: **CRITICAL** - Requires new implementation track alongside existing platform

**Estimated Effort**: 6-8 weeks for MVP implementation (MEMORY + ORACLE + CURIOSITY + FACE)

---

## SECTION 1: STRATEGIC ARCHITECTURE GAPS

### GAP 1.1: Database Architecture Mismatch ⚠️ **CRITICAL**

**Requirement**:
- Supabase (PostgreSQL) database (Req C.1)
- Specific schema: channels, campaigns, creatives, daily_metrics, cohorts tables
- Beauty/DTC-focused data model with LTV tracking

**Current Implementation**:
- MongoDB with AgentKit-focused collections
- Collections: users, agents, workflows, campaigns (general CRM schema)
- No channels, daily_metrics, or cohorts tables

**Impact**: 
- Cannot support requirements without schema redesign
- All MEMORY/ORACLE/CURIOSITY modules depend on this schema

**Recommendation**: 
1. **Option A (Recommended)**: Add Supabase alongside MongoDB for marketing intelligence modules
2. **Option B**: Extend MongoDB schema with required collections (adapter layer complexity)

---

### GAP 1.2: Target Market Mismatch ⚠️ **HIGH**

**Requirement**:
- Primary ICP: $50M-$100M DTC/subscription brands (Beauty, Supplements, Health & Wellness)
- Focus: Meta/Google/TikTok ad spend optimization
- Pain: Cross-channel attribution, creative fatigue, budget misallocation

**Current Implementation**:
- General B2B/B2C marketing automation
- Platform-agnostic CRM + workflow builder
- Target: Mid-market businesses (broad)

**Impact**:
- Messaging, features, and UX not optimized for DTC vertical
- No vertical-specific pain point solutions

**Recommendation**:
- Create DTC-specific product track or white-label variant
- Implement vertical-specific features separately

---

### GAP 1.3: Core Brain Module Architecture Missing ⚠️ **CRITICAL**

**Requirement**:
Three core brain modules answering:
1. **MEMORY**: "What actually happened?" (Attribution truth)
2. **ORACLE**: "What will break next?" (7-14 day predictions)
3. **CURIOSITY**: "What should we do tomorrow?" (Top 3 actions)

**Current Implementation**:
Four different brain modules:
1. **memory_client_service.py**: Customer segmentation/churn (NOT attribution)
2. **oracle_predictive_service.py**: Generic predictions (NOT DTC-focused)
3. **curiosity_market_service.py**: Market intelligence (NOT budget recommendations)
4. **face_experience_service.py**: UX optimization (NOT intelligence dashboard)

**Impact**:
- Existing modules solve DIFFERENT problems than requirements
- Cannot reuse existing brain logic without complete rewrite
- Name collision creates confusion

**Recommendation**:
- Rename existing modules to avoid confusion (e.g., ClientIntelligenceService)
- Create NEW modules: MemoryAttributionService, OraclePredictiveService, CuriosityActionService
- Implement in separate namespace: `backend/services/marketing_intelligence/`

---

## SECTION 2: MODULE-SPECIFIC GAPS

### GAP 2.1: MEMORY Module - Attribution & ROI Truth Layer ⚠️ **CRITICAL**

**Status**: **NOT IMPLEMENTED** (existing memory_client_service does NOT meet requirements)

#### Required Features (Per Req B.3):
- [ ] Unified ROI calculation across Meta/Google/TikTok
- [ ] LTV-adjusted ROAS computation
- [ ] Cross-channel attribution (solving "110% attribution problem")
- [ ] Winner/loser channel marking (ROAS > blended * 1.15)
- [ ] Blended MER (Marketing Efficiency Ratio) calculation
- [ ] Cohort LTV factor integration

#### Required Input Schema (Req C.1):
- [ ] `channels` table (channel_id, channel_name, platform)
- [ ] `daily_metrics` table (date, channel_id, campaign_id, creative_id, impressions, clicks, spend, conversions, revenue)
- [ ] `cohorts` table (cohort_month, customer_count, ltv_30d, ltv_60d, ltv_90d)

#### Required Output Schema (Req B.3.4):
```json
{
  "totals": {
    "spend": number,
    "revenue": number,
    "roas": number,
    "ltv_adjusted_revenue": number,
    "ltv_roas": number
  },
  "channels": [
    {
      "channel_id": string,
      "channel_name": string,
      "spend": number,
      "revenue": number,
      "roas": number,
      "ltv_roas": number,
      "status": "winner" | "loser" | "neutral"
    }
  ]
}
```

#### Acceptance Criteria (Req B.3.5):
- [ ] ROI MAPE (Mean Absolute Percentage Error) ≤20%
- [ ] CLV RMSE ≤25%
- [ ] Unified customer journey data across all platforms

**Current Gap**: Existing `memory_client_service.py` focuses on customer segmentation and churn prediction, NOT attribution/ROI calculation. Completely different problem domain.

**Implementation Effort**: **2-3 weeks**

---

### GAP 2.2: ORACLE Module - Prediction & Risk Engine ⚠️ **CRITICAL**

**Status**: **PARTIALLY IMPLEMENTED** (25% - algorithm misalignment)

#### Required Features (Per Req B.4):

**ENGINE 1 - Creative Fatigue Detection** (Req B.4.2.1):
- [x] ✅ Exists in `oracle_predictive_service.py::predict_creative_fatigue`
- [ ] ❌ Uses different algorithm than requirements (needs CVR/CPA deterioration detection)
- [ ] ❌ Missing frequency > 3.5 audience saturation check
- [ ] ❌ Output schema mismatch (needs fatigue_probability_7d, fatigue_probability_14d)

**ENGINE 2 - ROI Decay Detection** (Req B.4.2.2):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Required: Channel-level ROAS drop > 15% detection
- [ ] Required: Spend increasing but ROAS declining detection
- [ ] Required: Decay severity scoring (high/medium/low)

**ENGINE 3 - LTV Drift Detection** (Req B.4.2.3):
- [x] ✅ Partially exists in `forecast_ltv` method
- [ ] ❌ Missing cohort comparison logic (recent cohorts vs historical baseline)
- [ ] ❌ Missing 10% drift threshold detection
- [ ] ❌ Missing trend direction analysis (accelerating/stabilizing)

**Risk Aggregation** (Req B.4.3):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Required: Global risk level (RED/YELLOW/GREEN)
- [ ] Required: Count ≥3 high-severity risks → RED
- [ ] Required: 1-2 moderate risks → YELLOW

#### Required Output Schema (Req B.4.4):
```json
{
  "creative_fatigue": [ /* array with fatigue_probability_7d, fatigue_probability_14d */ ],
  "roi_decay_channels": [ /* array with decay_severity, roas_trend */ ],
  "ltv_drift": { "status": "drifting|stable|improving", "severity": "high|medium|low" },
  "risk_level": "red|yellow|green"
}
```

#### Acceptance Criteria (Req B.4.5):
- [ ] Fatigue prediction AUC ≥0.75 (7-day forecast)
- [ ] LTV prediction RMSE ≤25%
- [ ] Compound learning moat (accuracy improves over time)

**Current Gap**: `oracle_predictive_service.py` has rule-based fatigue prediction but lacks the three-engine architecture and risk aggregation required by the specifications.

**Implementation Effort**: **2-3 weeks**

---

### GAP 2.3: CURIOSITY Module - Decision & Recommendation Engine ⚠️ **CRITICAL**

**Status**: **NOT IMPLEMENTED** (existing curiosity_market_service does NOT meet requirements)

#### Required Features (Per Req B.5):

**GENERATOR 1 - Shift Budget Actions** (Req B.5.2.1):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Identify losers (MEMORY) + decaying channels (ORACLE)
- [ ] Calculate shift_amount (e.g., 10% of current spend)
- [ ] Target highest-ROAS winner not at capacity
- [ ] Estimate impact = shift_amount * (target_ROAS - source_ROAS)

**GENERATOR 2 - Pause Creative Actions** (Req B.5.2.2):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Flag creatives with fatigue_probability_7d > 0.6
- [ ] Estimate impact = daily_spend * predicted_performance_drop * 7 days
- [ ] Urgency = "high" if probability > 0.8

**GENERATOR 3 - Increase Budget Actions** (Req B.5.2.3):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Identify winners with ROAS > blended_ROAS * 1.2
- [ ] Calculate increase_amount (5-10% of current spend)
- [ ] Estimate impact = increase_amount * (channel_ROAS - blended_ROAS)

**GENERATOR 4 - Retention/LTV Focus Actions** (Req B.5.2.4):
- [ ] ❌ NOT IMPLEMENTED (optional for MVP)

#### Action Ranking & Selection (Req B.5.3):
- [ ] ❌ NOT IMPLEMENTED
- [ ] Scoring function: score = (impact * 0.4) + (severity * 0.3) + (confidence * 0.2) + (urgency * 0.1)
- [ ] Return TOP 3 ACTIONS only
- [ ] Ensure action diversity (max 1 increase_budget action)

#### Required Output Schema (Req B.5.4):
```json
{
  "actions": [
    {
      "action_type": "shift_budget|pause_creative|increase_budget|focus_retention",
      "priority": 1|2|3,
      "target": { "from": string, "to": string },
      "amount": { "current": number, "recommended": number, "change_percent": number },
      "estimated_impact_usd": number,
      "rationale": string,
      "urgency": "high|medium|low",
      "severity": "high|medium|low",
      "confidence": "high|medium|low",
      "score": number
    }
  ],
  "total_potential_uplift_usd": number
}
```

#### Acceptance Criteria (Req B.5.5):
- [ ] Allocation regret ≤15% vs oracle (optimal hindsight)
- [ ] Generate 2-3 specific budget moves with clear rationale
- [ ] Decision latency ≤300ms, RAM ≤512MB

**Current Gap**: `curiosity_market_service.py` focuses on market research and competitive analysis, NOT budget allocation decisions. Completely different use case.

**Implementation Effort**: **2-3 weeks**

---

### GAP 2.4: FACE Module - Single Intelligence Surface ⚠️ **CRITICAL**

**Status**: **NOT IMPLEMENTED** (existing face_experience_service is server-side UX optimization)

#### Required Features (Per Req B.6):

**Frontend Component Requirements**:
- [ ] ❌ NOT IMPLEMENTED: React/Next.js single-page dashboard component
- [ ] ❌ NOT IMPLEMENTED: Top Bar - Executive Summary Metrics (MER, Blended ROAS, LTV-ROAS, Global Risk Level)
- [ ] ❌ NOT IMPLEMENTED: MEMORY Card - Attribution truth table with winner/loser badges
- [ ] ❌ NOT IMPLEMENTED: ORACLE Card - Predictive alerts (7-14 day warnings)
- [ ] ❌ NOT IMPLEMENTED: CURIOSITY Card - Top 3 Actions with Accept/Reject buttons
- [ ] ❌ NOT IMPLEMENTED: Creative Snapshot - Visual thumbnails with fatigue probability

**Persona-Specific Views** (Req B.6.1.3):
- [ ] ❌ NOT IMPLEMENTED: CMO view (Sarah Martinez persona - executive summary focus)
- [ ] ❌ NOT IMPLEMENTED: VP Growth view (Jason Li persona - tactical metrics)
- [ ] ❌ NOT IMPLEMENTED: Director view (Emily Chen persona - action-first format)
- [ ] ❌ NOT IMPLEMENTED: Persona toggle selector

**UI/UX Requirements** (Req B.6.3):
- [ ] ❌ Desktop/laptop-first SPA, ≥1280px width
- [ ] ❌ NO backend required for MVP (static JSON loading)
- [ ] ❌ Charts, filters, narratives, badges
- [ ] ❌ Persona-specific microcopy

**Performance Requirements** (Req B.6.4):
- [ ] ❌ Lighthouse Performance Score ≥90
- [ ] ❌ Accessibility (a11y) Score ≥95
- [ ] ❌ Runs via `npm install && npm run dev`

**Current Gap**: `face_experience_service.py` is a backend service for UX analysis (user behavior, drop-off points), NOT a frontend dashboard component. No corresponding React component exists in `/workspace/frontend/src/components/`.

**Implementation Effort**: **2-3 weeks**

---

## SECTION 3: DATA & INFRASTRUCTURE GAPS

### GAP 3.1: Database Schema & Supabase Integration ⚠️ **CRITICAL**

**Requirement** (Req C.1):
- Supabase PostgreSQL database
- 5 specific tables: channels, campaigns, creatives, daily_metrics, cohorts

**Current Implementation**:
- MongoDB with 20+ collections
- No Supabase integration
- No matching schema

**Missing Tables**:
```sql
-- All 5 tables MISSING:
CREATE TABLE channels (...);        -- ❌ NOT EXISTS
CREATE TABLE campaigns (...);       -- ❌ NOT EXISTS (MongoDB has different schema)
CREATE TABLE creatives (...);       -- ❌ NOT EXISTS
CREATE TABLE daily_metrics (...);   -- ❌ NOT EXISTS
CREATE TABLE cohorts (...);         -- ❌ NOT EXISTS
```

**Impact**: MEMORY, ORACLE, and CURIOSITY modules cannot function without these tables.

**Implementation Effort**: **1 week** (schema + migrations + Supabase setup)

---

### GAP 3.2: Data Seeding & Demo Scenarios ⚠️ **HIGH**

**Requirement** (Req C.2):
- Sample data for $65M Beauty subscription brand
- Narrative alignment: Meta (hero), Google (solid), TikTok (problem child)
- Patterns that trigger ORACLE detection (Creative C12 fatigue, TikTok decay, LTV drift)
- Expected CURIOSITY outputs preset

**Current Implementation**:
- ❌ No data seeding scripts found
- ❌ No sample campaign data
- ❌ No preset scenarios for demo

**Missing Files**:
- `backend/data_seeds/beauty_brand_seed.sql` - ❌ NOT EXISTS
- `backend/data_seeds/demo_scenarios.json` - ❌ NOT EXISTS

**Impact**: Cannot demonstrate MVP or test modules without realistic data.

**Implementation Effort**: **3-5 days**

---

### GAP 3.3: Platform Integration Mismatch ⚠️ **MEDIUM**

**Requirement** (Req A.4):
- Focus: Meta Ads, Google Ads, TikTok Ads (ad performance metrics)
- Secondary: Shopify (orders/revenue), Klaviyo (email), HubSpot (CRM)

**Current Implementation**:
- ✅ AgentKit, GoHighLevel integrations exist
- ✅ Generic platform adapters (Google, Meta, LinkedIn)
- ❌ No specific ad performance metric extraction for MEMORY module
- ❌ No cohort/LTV data integration from commerce platforms

**Impact**: Existing integrations pull generic campaign data, NOT the specific daily_metrics schema needed for attribution/ROI calculation.

**Implementation Effort**: **1-2 weeks** (adapter layer for MEMORY module inputs)

---

## SECTION 4: DEMO & PRESENTATION GAPS

### GAP 4.1: 3-Minute Demo Script & Assets ⚠️ **HIGH**

**Requirement** (Req D.1):
- Exact 3-minute demo flow (15-second opening hook → 2:50 module walkthrough → 10-second close)
- Live browser demo with pre-populated scenario
- Click sequence scripted (MEMORY expand → ORACLE show → CURIOSITY reveal → Persona toggle)
- Preset scenario: "Beauty Brand - $150M - Week Summary"

**Current Implementation**:
- ❌ No demo script file
- ❌ No preset demo data
- ❌ No demo flow documentation

**Missing Files**:
- `docs/demo/3min_demo_script.md` - ❌ NOT EXISTS
- `docs/demo/live_demo_cue_sheet.md` - ❌ NOT EXISTS
- `frontend/src/demo/preset_scenarios.json` - ❌ NOT EXISTS

**Impact**: Cannot deliver consistent, compelling demo to investors/customers without scripted flow and preset data.

**Implementation Effort**: **1 week** (after FACE UI implementation)

---

### GAP 4.2: Demo Package Assets ⚠️ **MEDIUM**

**Requirement** (Req D.3):
- Slide 1: Problem Statement (6 conflicting dashboards visual)
- Slide 2: Omnify Solution (brain graphic)
- Slide 3: Module Overview (MEMORY → ORACLE → CURIOSITY → FACE flow)
- Slide 4: Live Demo Transition
- Slide 5: Impact & Differentiation (comparison table)
- Slide 6: Call to Action

**Current Implementation**:
- ❌ No slide deck assets
- ❌ No demo visuals

**Implementation Effort**: **3-5 days** (design + content)

---

## SECTION 5: PRICING & GTM GAPS

### GAP 5.1: Pricing Tier Mismatch ⚠️ **MEDIUM**

**Requirement** (Req F.1):
- Starter: $499/month (MEMORY + ORACLE + basic CURIOSITY + FACE)
- Growth: $799/month (Full features + EYES)
- Scale: $1,499/month (All modules + white-label)

**Current Implementation**:
- Existing OmnifyProduct pricing: Not aligned with DTC Intelligence Layer model
- No MEMORY/ORACLE/CURIOSITY-based feature gating
- No usage-based pricing (e.g., events/month limits)

**Impact**: Cannot price or sell "AI Marketing Intelligence Layer" as separate SKU from existing platform.

**Recommendation**: Create separate pricing/product SKU or bundle as "Intelligence Add-On."

**Implementation Effort**: **1-2 weeks** (billing logic + Stripe integration + feature gates)

---

### GAP 5.2: Target Persona Alignment ⚠️ **MEDIUM**

**Requirement** (Req A.3):
- Persona #1: Sarah Martinez, CMO - Focus on LTV-ROAS, executive summary, CEO-ready format
- Persona #2: Jason Li, VP Growth - Focus on fatigue alerts, tactical execution
- Persona #3: Emily Chen, Director Perf - Focus on action-first flags

**Current Implementation**:
- Generic B2B/mid-market personas
- No DTC/subscription-specific pain points documented
- No persona-driven UX customization

**Impact**: Messaging, onboarding, and UX not optimized for DTC decision-makers.

**Recommendation**: Create DTC-specific onboarding flow and persona-based dashboard views in FACE module.

**Implementation Effort**: **1 week** (UX/content)

---

## SECTION 6: DEFERRED FEATURES (PHASE 2/3)

### Explicitly OUT OF SCOPE for MVP (Per Req B.1.2):

- ✅ **EYES** - Customer Segmentation Module (Phase 2)
- ✅ **VOICE** - Creative Repurposing Studio (Phase 2)
- ✅ **REFLEXES** - Real-Time Anomaly Detection (Phase 3)

**Note**: Existing platform has advanced features (AgentKit workflows, multi-tenancy, GoHighLevel integration) that are NOT required for MVP and can be deprioritized.

---

## SECTION 7: COMPETITIVE POSITIONING GAPS

### GAP 7.1: Missing Differentiation Assets ⚠️ **LOW**

**Requirement** (Req E.1):
- Compound Learning Moat documentation (showing continuous improvement over time)
- 7-14 day predictive optimization proof (vs reactive competitors)
- Comparison table: Omnify vs Salesforce/HubSpot/Zoho/Microsoft (0-10 rankings)

**Current Implementation**:
- Generic competitive positioning
- No DTC-specific differentiation materials
- No predictive capability benchmarks

**Implementation Effort**: **1 week** (marketing/documentation)

---

## SECTION 8: TESTING & VALIDATION GAPS

### GAP 8.1: Module Acceptance Testing ⚠️ **HIGH**

**Requirement**:
- MEMORY: ROI MAPE ≤20%, CLV RMSE ≤25% (Req B.3.5)
- ORACLE: Fatigue prediction AUC ≥0.75, LTV prediction RMSE ≤25% (Req B.4.5)
- CURIOSITY: Allocation regret ≤15% vs oracle, latency ≤300ms (Req B.5.5)
- FACE: Lighthouse ≥90, a11y ≥95 (Req B.6.4)

**Current Implementation**:
- ❌ No acceptance test suites for marketing intelligence modules
- ❌ No performance benchmarks
- ❌ No accuracy validation against historical data

**Implementation Effort**: **1-2 weeks** (test infrastructure + data)

---

## SECTION 9: DOCUMENTATION GAPS

### GAP 9.1: MVP-Specific Documentation ⚠️ **MEDIUM**

**Missing Documentation**:
- [ ] `docs/MVP_ARCHITECTURE.md` - MEMORY→ORACLE→CURIOSITY→FACE flow diagram
- [ ] `docs/PERSONA_GUIDE.md` - Sarah/Jason/Emily use case walkthroughs
- [ ] `docs/DEMO_SETUP.md` - How to run 3-minute demo locally
- [ ] `docs/DATA_SEEDS.md` - How to load sample data
- [ ] `docs/MODULE_APIS.md` - JSON input/output specs for each module

**Implementation Effort**: **1 week**

---

## SECTION 10: SUMMARY & RECOMMENDATIONS

### 10.1 Critical Path Gaps (MUST FIX for MVP)

| # | Gap | Severity | Effort | Blocker For |
|---|-----|----------|--------|-------------|
| 1 | Database schema (Supabase + 5 tables) | CRITICAL | 1 week | All modules |
| 2 | MEMORY Module (attribution/ROI truth) | CRITICAL | 2-3 weeks | ORACLE, CURIOSITY |
| 3 | ORACLE Module (prediction engine) | CRITICAL | 2-3 weeks | CURIOSITY, FACE |
| 4 | CURIOSITY Module (action engine) | CRITICAL | 2-3 weeks | FACE demo |
| 5 | FACE UI Component (dashboard) | CRITICAL | 2-3 weeks | Demo, customer value |
| 6 | Data seeding (demo scenarios) | HIGH | 3-5 days | Testing, demo |
| 7 | Platform adapters (daily_metrics) | MEDIUM | 1-2 weeks | MEMORY module |
| 8 | 3-minute demo script | HIGH | 1 week | Customer demos |

**Total Estimated Effort**: **6-8 weeks** (with 2 developers working in parallel)

---

### 10.2 Recommended Implementation Roadmap

#### **Phase 1: Foundation (Week 1-2)**
1. **Week 1**: Database schema setup
   - [ ] Set up Supabase PostgreSQL instance
   - [ ] Create 5 required tables (channels, campaigns, creatives, daily_metrics, cohorts)
   - [ ] Write migration scripts
   - [ ] Create Python/Node.js Supabase client library

2. **Week 2**: Data seeding & platform adapters
   - [ ] Create sample data for $65M Beauty brand
   - [ ] Implement platform adapter layer (Meta/Google/TikTok → daily_metrics schema)
   - [ ] Write data validation tests

#### **Phase 2: Core Brain Modules (Week 3-6)**
3. **Week 3**: MEMORY Module
   - [ ] Implement attribution/ROI calculation engine
   - [ ] Implement LTV-ROAS computation
   - [ ] Implement winner/loser marking logic
   - [ ] Write unit tests (ROI MAPE ≤20% validation)

4. **Week 4**: ORACLE Module
   - [ ] Implement ENGINE 1: Creative Fatigue Detection
   - [ ] Implement ENGINE 2: ROI Decay Detection
   - [ ] Implement ENGINE 3: LTV Drift Detection
   - [ ] Implement Risk Aggregation (RED/YELLOW/GREEN)
   - [ ] Write unit tests (AUC ≥0.75 validation)

5. **Week 5**: CURIOSITY Module
   - [ ] Implement GENERATOR 1: Shift Budget Actions
   - [ ] Implement GENERATOR 2: Pause Creative Actions
   - [ ] Implement GENERATOR 3: Increase Budget Actions
   - [ ] Implement Action Ranking & Selection (Top 3)
   - [ ] Write unit tests (allocation regret ≤15% validation)

6. **Week 6**: Module integration & orchestration
   - [ ] Create orchestration harness (MEMORY → ORACLE → CURIOSITY pipeline)
   - [ ] Implement end-to-end data flow tests
   - [ ] Performance optimization (latency targets)

#### **Phase 3: FACE UI & Demo (Week 7-8)**
7. **Week 7**: FACE Dashboard Component
   - [ ] Implement Top Bar (Executive Summary Metrics)
   - [ ] Implement MEMORY Card (attribution truth table)
   - [ ] Implement ORACLE Card (predictive alerts)
   - [ ] Implement CURIOSITY Card (Top 3 Actions)
   - [ ] Implement Persona Toggle (Sarah/Jason/Emily views)
   - [ ] Lighthouse performance optimization (≥90 score)

8. **Week 8**: Demo & Documentation
   - [ ] Create 3-minute demo script & cue sheet
   - [ ] Create preset demo scenario loader
   - [ ] Create demo slide deck (6 slides)
   - [ ] Write MVP documentation (architecture, personas, API specs)
   - [ ] Final integration testing & bug fixes

#### **Phase 4: Launch Prep (Week 9-10)** - Optional
9. **Week 9**: Pricing & GTM setup
   - [ ] Implement tiered pricing logic ($499/$799/$1,499)
   - [ ] Create feature gates (Starter/Growth/Scale)
   - [ ] Stripe subscription integration
   - [ ] Usage tracking & quota enforcement

10. **Week 10**: Marketing assets & launch
    - [ ] Create competitive positioning materials
    - [ ] Create customer case study template
    - [ ] Create sales demo training materials
    - [ ] Soft launch to beta customers

---

### 10.3 Architecture Decision: Two-Track Approach

**Recommendation**: Maintain TWO SEPARATE PRODUCT TRACKS

#### **Track 1: Omnify Cloud Connect** (Existing)
- General marketing automation platform
- AgentKit-powered AI workflows
- Multi-vertical B2B/B2C focus
- GoHighLevel, LinkedIn, YouTube integrations
- Maintain existing MongoDB architecture

#### **Track 2: Omnify Marketing Intelligence Layer** (New - Per Requirements)
- DTC/subscription-specific intelligence layer
- MEMORY + ORACLE + CURIOSITY + FACE modules
- Beauty/Supplements/Health & Wellness vertical focus
- Meta/Google/TikTok optimization
- New Supabase PostgreSQL architecture

**Integration Point**: Track 2 can optionally integrate with Track 1 as a "module" or "add-on" for customers who want both general automation AND DTC intelligence.

**Rationale**:
1. Different target markets (general B2B vs DTC subscriptions)
2. Different technical architectures (MongoDB vs PostgreSQL)
3. Different value propositions (automation vs intelligence)
4. Minimizes risk to existing platform
5. Allows parallel development

---

### 10.4 Resource Requirements

**Team Structure**:
- 1x Full-Stack Engineer (Backend + Frontend lead)
- 1x Frontend Engineer (React/FACE UI specialist)
- 1x Data Engineer (Schema + Seeding + Platform adapters)
- 1x Product Designer (FACE UI/UX + Persona workflows)
- 1x QA Engineer (Testing + Demo validation)

**Technology Stack** (Additions):
- Supabase (PostgreSQL database)
- Next.js / React (FACE UI - can reuse existing frontend stack)
- Python FastAPI (Backend - can extend existing backend)
- scikit-learn (ML models for ORACLE)
- Recharts / Chart.js (FACE dashboard visualizations)

---

### 10.5 Risk Mitigation

**Risk 1**: Existing platform customers expect these features
- **Mitigation**: Position as separate "Intelligence Add-On" SKU with cross-sell opportunity

**Risk 2**: Name collision (existing MEMORY/ORACLE/CURIOSITY/FACE services)
- **Mitigation**: Rename existing services (e.g., ClientIntelligenceService) and create new namespace

**Risk 3**: Database migration complexity (MongoDB → Supabase)
- **Mitigation**: Add Supabase alongside MongoDB (no migration required), use adapter layer if cross-database queries needed

**Risk 4**: 6-8 week timeline underestimated
- **Mitigation**: Implement in phases, MVP can be delivered with 3 core modules (MEMORY + ORACLE + CURIOSITY) in 5-6 weeks, FACE UI can be added incrementally

---

## SECTION 11: CONCLUSION

### Key Findings:

1. **The existing Omnify Cloud Connect platform is NOT aligned with the Marketing Intelligence Layer requirements** - it's a general automation platform, not a DTC attribution/prediction system.

2. **All four core modules (MEMORY, ORACLE, CURIOSITY, FACE) need NEW implementations** - existing services with similar names solve different problems.

3. **Database architecture requires Supabase PostgreSQL** - current MongoDB schema cannot support attribution/ROI calculations without significant adapter complexity.

4. **Estimated 6-8 weeks for MVP implementation** with proper resourcing (2-3 developers + designer + QA).

5. **Two-track product strategy recommended** to maintain existing platform value while building new DTC intelligence layer.

---

### Next Steps:

1. **Decision**: Choose Option A (Supabase alongside MongoDB) or Option B (MongoDB schema extension)
2. **Kickoff**: Assemble development team (3 engineers + 1 designer + 1 QA)
3. **Sprint 0**: Set up Supabase, create schema, seed sample data (Week 1)
4. **Sprints 1-5**: Implement MEMORY → ORACLE → CURIOSITY → FACE (Weeks 2-7)
5. **Sprint 6**: Demo prep & documentation (Week 8)
6. **Beta Launch**: Soft launch to 10-20 DTC brands for validation

---

**Document Version**: 1.0  
**Status**: Ready for Leadership Review  
**Next Review**: Post-decision on two-track approach

