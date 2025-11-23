# Omnify AI Marketing Brain - Implementation Roadmap

**Roadmap Date**: November 23, 2025  
**Target MVP Completion**: January 20, 2026 (8 weeks)  
**Team Size**: 5 FTE (2 Backend + 1 Frontend + 1 Data + 1 QA)

---

## EXECUTIVE OVERVIEW

### What We're Building

**Product**: AI Marketing Intelligence Layer for DTC brands ($50M-$350M revenue)

**Core Value Proposition**: 
- Solve the "6 conflicting dashboards" problem
- Answer 3 questions on one screen: "What happened?" / "What's breaking?" / "What to do?"
- 7-14 day advance warnings on creative fatigue, ROI decay, LTV drift

### Implementation Strategy

**Approach**: **Two-Track Architecture**
1. **Track 1 (Existing)**: Omnify Cloud Connect - general marketing automation
2. **Track 2 (New)**: Marketing Intelligence Layer - DTC-specific attribution/prediction

**Technology Stack Changes**:
```
Current:  MongoDB + AgentKit + React + FastAPI
New Add:  + Supabase (PostgreSQL) + scikit-learn + Recharts
```

---

## PHASE 0: PREPARATION & DECISION (Week 0 - Pre-Kickoff)

### DECISION POINT 1: Database Architecture ⚠️ **CRITICAL**

**Option A - Recommended**: Add Supabase alongside MongoDB
- **Pros**: Clean separation, no migration risk, PostgreSQL optimized for analytics
- **Cons**: Two databases to maintain
- **Effort**: 1 week setup
- **Cost**: $57/month (Supabase Pro plan)

**Option B**: Extend MongoDB with marketing intelligence collections
- **Pros**: Single database, no new infrastructure
- **Cons**: MongoDB not ideal for time-series analytics, complex adapter layer
- **Effort**: 1-2 weeks + ongoing complexity
- **Cost**: Increased MongoDB Atlas tier

**DECISION REQUIRED**: [   ] Option A   [   ] Option B

---

### DECISION POINT 2: Module Namespace Strategy

**Option A - Recommended**: Create separate namespace `backend/services/marketing_intelligence/`
- New modules: `memory_attribution_service.py`, `oracle_prediction_service.py`, etc.
- Rename existing: `memory_client_service.py` → `client_segmentation_service.py`

**Option B**: Keep existing names, merge functionality
- Higher coupling, harder to maintain two different use cases

**DECISION REQUIRED**: [   ] Option A   [   ] Option B

---

### DECISION POINT 3: Product Positioning

**Option A - Recommended**: Separate SKU "Omnify Intelligence Layer" ($499-$1,499/month)
- Independent pricing, DTC-focused marketing
- Can be bundled with Cloud Connect for discount

**Option B**: Feature add-on to existing Cloud Connect
- Lower perceived value, harder to position uniquely

**DECISION REQUIRED**: [   ] Option A   [   ] Option B

---

### Pre-Kickoff Tasks (Week 0)

- [ ] **Day 1-2**: Leadership decision on 3 decision points above
- [ ] **Day 3**: Team assembly (hire/allocate 5 FTE)
- [ ] **Day 4**: Development environment setup (Supabase account, repo branching)
- [ ] **Day 5**: Kick-off meeting + sprint planning

**Deliverable**: Approved architecture decisions + assembled team

---

## PHASE 1: FOUNDATION (Week 1-2)

### Week 1: Database Schema & Infrastructure

#### **SPRINT GOAL**: Supabase PostgreSQL database operational with 5 core tables

#### Monday (Day 1)
**Owner**: Data Engineer

**Tasks**:
- [ ] Create Supabase project (`omnify-marketing-intelligence`)
- [ ] Set up database connection pooling (max 100 connections)
- [ ] Create `.env.supabase` with credentials
- [ ] Install Supabase Python client: `pip install supabase`
- [ ] Create `backend/database/supabase_client.py` connection manager

**Deliverable**: Working Supabase connection from backend

---

#### Tuesday (Day 2)
**Owner**: Data Engineer

**Tasks**:
- [ ] Create migration file: `migrations/001_create_core_schema.sql`
- [ ] Implement `channels` table schema (per Req C.1.1)
  ```sql
  CREATE TABLE channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_id VARCHAR(50) UNIQUE NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Implement `campaigns` table schema (per Req C.1.2)
- [ ] Implement `creatives` table schema (per Req C.1.3)
- [ ] Add foreign key constraints
- [ ] Create indexes for performance

**Deliverable**: Database schema script ready

---

#### Wednesday (Day 3)
**Owner**: Data Engineer

**Tasks**:
- [ ] Implement `daily_metrics` table (per Req C.1.4) - CRITICAL for MEMORY
  ```sql
  CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    channel_id VARCHAR(50) REFERENCES channels(channel_id),
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
    creative_id VARCHAR(50) REFERENCES creatives(creative_id),
    impressions INTEGER,
    clicks INTEGER,
    spend DECIMAL(10,2),
    conversions INTEGER,
    revenue DECIMAL(10,2),
    frequency DECIMAL(4,2),
    ctr DECIMAL(5,4),
    cpc DECIMAL(5,2),
    cvr DECIMAL(5,4),
    cpa DECIMAL(7,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, channel_id, campaign_id, creative_id)
  );
  ```
- [ ] Implement `cohorts` table (per Req C.1.5) - CRITICAL for LTV
- [ ] Add composite indexes for query optimization
- [ ] Run migration on Supabase dev environment

**Deliverable**: All 5 tables created and indexed

---

#### Thursday (Day 4)
**Owner**: Data Engineer + Backend Engineer #1

**Tasks**:
- [ ] Create Supabase Python ORM models (`backend/models/marketing_intelligence_models.py`)
- [ ] Implement CRUD operations for each table
- [ ] Write connection pool management logic
- [ ] Write unit tests for database operations
- [ ] Test connection pooling under load (100 concurrent queries)

**Deliverable**: Supabase ORM layer with passing tests

---

#### Friday (Day 5)
**Owner**: Data Engineer

**Tasks**:
- [ ] Create data seeding script: `backend/data_seeds/beauty_brand_seed.py`
- [ ] Implement $65M Beauty brand sample data (per Req C.2.1):
  - 3 channels: Meta (META_001), Google (GOOGLE_001), TikTok (TIKTOK_001)
  - 10 campaigns per channel (30 total)
  - 5 creatives per campaign (150 total)
  - 90 days of daily_metrics (13,500 records)
  - 12 months of cohorts data (12 records)
- [ ] Implement narrative patterns (per Req C.2.3-C.2.5):
  - Meta: ROAS stable 3.5-3.8 (winner)
  - Google: ROAS stable 2.2-2.5 (solid)
  - TikTok: ROAS declining 2.8→1.9 (problem child)
  - Creative C12: CVR declining 0.08→0.05 (fatigue signal)
  - Cohorts: LTV softening 128→112 (drift signal)

**Deliverable**: Realistic sample data loaded into Supabase

---

### Week 2: Platform Adapters & Data Pipeline

#### **SPRINT GOAL**: Real-time data ingestion from Meta/Google/TikTok APIs → daily_metrics table

#### Monday (Day 6)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Create adapter interface: `backend/integrations/marketing_intelligence_adapter.py`
- [ ] Define abstract `PlatformAdapter` base class:
  ```python
  class PlatformAdapter:
      def fetch_campaign_performance(start_date, end_date) -> List[DailyMetric]
      def fetch_creative_performance(campaign_id) -> List[DailyMetric]
      def fetch_cohort_data(cohort_month) -> CohortData
  ```
- [ ] Write unit tests for adapter interface

**Deliverable**: Platform adapter interface defined

---

#### Tuesday (Day 7)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Implement `MetaAdsAdapter` (extends PlatformAdapter)
  - [ ] Connect to existing Meta API integration (reuse `platform_adapters/meta_ads.py`)
  - [ ] Map Facebook Ads Insights API → daily_metrics schema
  - [ ] Handle rate limiting (200 requests/hour)
  - [ ] Implement data normalization (currency conversion, timezone handling)

**Deliverable**: Meta Ads adapter functional with tests

---

#### Wednesday (Day 8)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Implement `GoogleAdsAdapter`
  - [ ] Connect to existing Google Ads API integration
  - [ ] Map Google Ads Report API → daily_metrics schema
  - [ ] Handle API quotas
  - [ ] Implement data normalization
- [ ] Implement `TikTokAdsAdapter`
  - [ ] Connect to TikTok Ads Manager API
  - [ ] Map TikTok metrics → daily_metrics schema

**Deliverable**: Google + TikTok adapters functional

---

#### Thursday (Day 9)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Create data ingestion orchestrator: `backend/services/marketing_intelligence/data_ingestion_service.py`
- [ ] Implement daily sync job:
  ```python
  async def sync_daily_metrics(organization_id, date_range):
      # Fetch from all platforms in parallel
      # Transform to daily_metrics schema
      # Batch insert to Supabase
      # Handle conflicts (upsert logic)
  ```
- [ ] Implement incremental sync (only new data since last sync)
- [ ] Add error handling and retry logic

**Deliverable**: Automated data sync pipeline

---

#### Friday (Day 10)
**Owner**: Backend Engineer #1 + QA Engineer

**Tasks**:
- [ ] Write integration tests for data pipeline
- [ ] Test data quality validation (completeness, accuracy)
- [ ] Test sync performance (1000 records in < 30 seconds)
- [ ] Document data pipeline architecture
- [ ] **PHASE 1 CHECKPOINT**: Review with team

**Deliverable**: End-to-end data flow validated (Platform APIs → Supabase)

---

## PHASE 2: CORE BRAIN MODULES (Week 3-6)

### Week 3: MEMORY Module - Attribution & ROI Truth Layer

#### **SPRINT GOAL**: MEMORY module answering "What actually happened?" with LTV-adjusted ROAS

#### Monday (Day 11)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Create module: `backend/services/marketing_intelligence/memory_attribution_service.py`
- [ ] Implement input data fetching:
  ```python
  async def fetch_memory_input_data(organization_id, date_range):
      # Query daily_metrics aggregated by channel
      # Query cohorts for LTV factors
      # Return MemoryInputData object
  ```
- [ ] Define data models: `MemoryInputData`, `MemoryOutput` (per Req B.3.4)

**Deliverable**: MEMORY module skeleton + input fetching

---

#### Tuesday (Day 12)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Implement ROAS calculation (per Req B.3.3.1):
  ```python
  def calculate_roas(channel_data):
      return total_revenue / total_spend
  ```
- [ ] Implement LTV-adjusted ROAS (per Req B.3.3.1):
  ```python
  def calculate_ltv_roas(channel_data, cohorts):
      ltv_factor = cohorts.ltv_90d / cohorts.ltv_30d
      return (total_revenue * ltv_factor) / total_spend
  ```
- [ ] Implement blended metrics (per Req B.3.3.2):
  - Blended ROAS (all channels combined)
  - MER (Marketing Efficiency Ratio)

**Deliverable**: Core ROI calculation logic

---

#### Wednesday (Day 13)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Implement winner/loser marking (per Req B.3.3.3):
  ```python
  def mark_channel_status(channel_roas, blended_roas):
      if channel_roas > blended_roas * 1.15:
          return "winner"
      elif channel_roas < blended_roas * 0.85:
          return "loser"
      else:
          return "neutral"
  ```
- [ ] Implement output serialization to JSON schema (per Req B.3.4)
- [ ] Write unit tests (target: ROI MAPE ≤20% per Req B.3.5.1)

**Deliverable**: Complete MEMORY module with tests

---

#### Thursday (Day 14)
**Owner**: Backend Engineer #1 + QA Engineer

**Tasks**:
- [ ] Test MEMORY with sample data (Beauty brand seed)
- [ ] Validate output:
  - Meta marked as "winner" (ROAS 3.5-3.8)
  - Google marked as "neutral" (ROAS 2.2-2.5)
  - TikTok marked as "loser" (ROAS 1.9)
- [ ] Test edge cases (zero spend, missing data, negative revenue)
- [ ] Performance testing (100K daily_metrics in < 2 minutes per Req G.3.1)

**Deliverable**: MEMORY module validated against acceptance criteria

---

#### Friday (Day 15)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Create API endpoint: `POST /api/v1/marketing-intelligence/memory`
- [ ] Implement request/response handling
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Write API integration tests
- [ ] **WEEK 3 CHECKPOINT**: Demo MEMORY module to team

**Deliverable**: MEMORY module API-ready

---

### Week 4: ORACLE Module - Prediction & Risk Engine

#### **SPRINT GOAL**: ORACLE module predicting creative fatigue, ROI decay, LTV drift 7-14 days in advance

#### Monday (Day 16)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Create module: `backend/services/marketing_intelligence/oracle_prediction_service.py`
- [ ] Implement ENGINE 1 skeleton: `predict_creative_fatigue()`
- [ ] Implement time-series data extraction from daily_metrics
- [ ] Calculate performance baselines (7-day vs 14-21 day comparison)

**Deliverable**: ORACLE module skeleton + data preparation

---

#### Tuesday (Day 17)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Implement ENGINE 1 - Creative Fatigue Detection (per Req B.4.2.1):
  ```python
  def detect_creative_fatigue(creative_id, daily_metrics):
      recent_perf = last_7_days_metrics
      baseline_perf = prior_14_21_days_metrics
      
      cvr_drop = (baseline_cvr - recent_cvr) / baseline_cvr
      cpa_increase = (recent_cpa - baseline_cpa) / baseline_cpa
      frequency = recent_frequency
      
      if cvr_drop > 0.20 or cpa_increase > 0.25 or frequency > 3.5:
          return {
              "fatigued": True,
              "fatigue_probability_7d": 0.8,
              "predicted_performance_drop": cvr_drop * 100
          }
  ```
- [ ] Implement fatigue probability calculation (0.0-1.0)
- [ ] Write unit tests for ENGINE 1

**Deliverable**: Creative fatigue detection functional

---

#### Wednesday (Day 18)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Implement ENGINE 2 - ROI Decay Detection (per Req B.4.2.2):
  ```python
  def detect_roi_decay(channel_id, daily_metrics):
      recent_roas = last_7_days_avg_roas
      baseline_roas = prior_14_21_days_avg_roas
      roas_drop = (baseline_roas - recent_roas) / baseline_roas
      
      if roas_drop > 0.15:
          return {
              "decaying": True,
              "decay_severity": "high" if roas_drop > 0.25 else "medium",
              "roas_trend": "declining"
          }
  ```
- [ ] Implement ENGINE 3 - LTV Drift Detection (per Req B.4.2.3):
  ```python
  def detect_ltv_drift(cohorts):
      recent_cohorts = last_3_months
      baseline_cohorts = prior_3_6_months
      
      recent_avg_ltv = mean(recent_cohorts.ltv_90d)
      baseline_avg_ltv = mean(baseline_cohorts.ltv_90d)
      drift_pct = (baseline_avg_ltv - recent_avg_ltv) / baseline_avg_ltv
      
      if drift_pct > 0.10:
          return {
              "status": "drifting",
              "severity": "high" if drift_pct > 0.15 else "medium"
          }
  ```

**Deliverable**: ROI decay + LTV drift detection functional

---

#### Thursday (Day 19)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Implement Risk Aggregation (per Req B.4.3):
  ```python
  def calculate_global_risk_level(fatigue_list, decay_list, ltv_drift):
      high_severity_count = count_high_severity_risks()
      
      if high_severity_count >= 3:
          return "red"
      elif high_severity_count >= 1:
          return "yellow"
      else:
          return "green"
  ```
- [ ] Implement output serialization (per Req B.4.4 JSON schema)
- [ ] Write comprehensive unit tests
- [ ] Test with Beauty brand seed data (validate Creative C12 flagged, TikTok decay detected)

**Deliverable**: Complete ORACLE module with risk aggregation

---

#### Friday (Day 20)
**Owner**: Backend Engineer #2 + QA Engineer

**Tasks**:
- [ ] Test ORACLE accuracy (target: Fatigue AUC ≥0.75 per Req B.4.5.1)
- [ ] Create API endpoint: `POST /api/v1/marketing-intelligence/oracle`
- [ ] API documentation
- [ ] Integration tests
- [ ] **WEEK 4 CHECKPOINT**: Demo ORACLE predictions to team

**Deliverable**: ORACLE module API-ready

---

### Week 5: CURIOSITY Module - Decision & Recommendation Engine

#### **SPRINT GOAL**: CURIOSITY module generating Top 3 actionable recommendations

#### Monday (Day 21)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Create module: `backend/services/marketing_intelligence/curiosity_action_service.py`
- [ ] Implement action data models: `Action`, `ActionScore`, `CuriosityOutput`
- [ ] Implement action scoring function (per Req B.5.3.1):
  ```python
  def score_action(action):
      return (
          action.estimated_impact_usd * 0.4 +
          severity_weight * 0.3 +
          confidence_weight * 0.2 +
          urgency_weight * 0.1
      )
  ```

**Deliverable**: CURIOSITY module skeleton + scoring logic

---

#### Tuesday (Day 22)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Implement GENERATOR 1 - Shift Budget Actions (per Req B.5.2.1):
  ```python
  def generate_shift_budget_actions(memory_output, oracle_output):
      losers = [ch for ch in memory_output if ch.status == "loser"]
      decaying = oracle_output.roi_decay_channels
      winners = [ch for ch in memory_output if ch.status == "winner"]
      
      actions = []
      for source_channel in (losers + decaying):
          target_channel = highest_roas_winner()
          shift_amount = source_channel.spend * 0.10
          impact = shift_amount * (target_channel.roas - source_channel.roas)
          
          actions.append(Action(
              action_type="shift_budget",
              target={"from": source_channel.id, "to": target_channel.id},
              estimated_impact_usd=impact,
              urgency="high"
          ))
      
      return actions
  ```

**Deliverable**: Shift budget action generator functional

---

#### Wednesday (Day 23)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Implement GENERATOR 2 - Pause Creative Actions (per Req B.5.2.2):
  ```python
  def generate_pause_creative_actions(oracle_output):
      actions = []
      for creative in oracle_output.creative_fatigue:
          if creative.fatigue_probability_7d > 0.6:
              impact = creative.daily_spend * creative.predicted_performance_drop * 7
              urgency = "high" if creative.fatigue_probability_7d > 0.8 else "medium"
              
              actions.append(Action(
                  action_type="pause_creative",
                  target={"from": creative.creative_id},
                  estimated_impact_usd=impact,
                  urgency=urgency
              ))
      
      return actions
  ```
- [ ] Implement GENERATOR 3 - Increase Budget Actions (per Req B.5.2.3)

**Deliverable**: Pause + increase budget generators functional

---

#### Thursday (Day 24)
**Owner**: Backend Engineer #1

**Tasks**:
- [ ] Implement action ranking and Top 3 selection (per Req B.5.3.2):
  ```python
  def select_top_3_actions(all_actions):
      scored_actions = [score_action(a) for a in all_actions]
      sorted_actions = sorted(scored_actions, key=lambda x: x.score, reverse=True)
      
      # Ensure diversity (max 1 increase_budget)
      top_3 = diversify_actions(sorted_actions[:5])
      
      return top_3
  ```
- [ ] Implement output serialization (per Req B.5.4 JSON schema)
- [ ] Calculate `total_potential_uplift_usd` across all 3 actions
- [ ] Write unit tests

**Deliverable**: Complete CURIOSITY module with Top 3 selection

---

#### Friday (Day 25)
**Owner**: Backend Engineer #1 + QA Engineer

**Tasks**:
- [ ] Test CURIOSITY with Beauty brand seed data
- [ ] Validate expected outputs (per Req C.2.6):
  1. "Shift 10% from TikTok → Meta" (detected due to TikTok decay + Meta winner)
  2. "Pause Creative C12" (detected due to fatigue)
  3. "Increase Google Brand +6%" (detected due to solid performance)
- [ ] Test allocation regret ≤15% (per Req B.5.5.1)
- [ ] Test decision latency ≤300ms (per Req B.5.5 - Performance)
- [ ] Create API endpoint: `POST /api/v1/marketing-intelligence/curiosity`
- [ ] **WEEK 5 CHECKPOINT**: Demo full MEMORY→ORACLE→CURIOSITY pipeline

**Deliverable**: CURIOSITY module validated and API-ready

---

### Week 6: Module Integration & Orchestration

#### **SPRINT GOAL**: End-to-end pipeline from raw data to Top 3 actions

#### Monday-Wednesday (Day 26-28)
**Owner**: Backend Engineer #1 + Backend Engineer #2

**Tasks**:
- [ ] Create orchestration harness: `backend/services/marketing_intelligence/intelligence_orchestrator.py`
- [ ] Implement sequential pipeline:
  ```python
  async def run_intelligence_pipeline(organization_id, date_range):
      # Step 1: Fetch raw data from Supabase
      raw_data = await fetch_daily_metrics(organization_id, date_range)
      
      # Step 2: Run MEMORY
      memory_output = await MemoryService.process(raw_data)
      
      # Step 3: Run ORACLE (depends on MEMORY)
      oracle_output = await OracleService.process(raw_data, memory_output)
      
      # Step 4: Run CURIOSITY (depends on MEMORY + ORACLE)
      curiosity_output = await CuriosityService.process(memory_output, oracle_output)
      
      # Step 5: Return combined output
      return {
          "memory": memory_output,
          "oracle": oracle_output,
          "curiosity": curiosity_output,
          "timestamp": utcnow()
      }
  ```
- [ ] Implement error handling and fallback logic
- [ ] Implement caching layer (Redis) to avoid recomputation
- [ ] Write end-to-end integration tests

**Deliverable**: Orchestration pipeline functional

---

#### Thursday (Day 29)
**Owner**: Backend Engineer #2

**Tasks**:
- [ ] Create unified API endpoint: `POST /api/v1/marketing-intelligence/analyze`
  - Input: `organization_id`, `date_range`
  - Output: Combined MEMORY + ORACLE + CURIOSITY JSON
- [ ] Implement API authentication (JWT + organization scoping)
- [ ] Add rate limiting (10 requests/minute per organization)
- [ ] OpenAPI documentation

**Deliverable**: Unified intelligence API endpoint

---

#### Friday (Day 30)
**Owner**: QA Engineer + All Engineers

**Tasks**:
- [ ] Performance testing (end-to-end pipeline < 5 seconds)
- [ ] Load testing (100 concurrent organizations)
- [ ] Accuracy validation against historical data (if available)
- [ ] Bug fixing sprint
- [ ] **PHASE 2 CHECKPOINT**: Backend modules complete and validated

**Deliverable**: Production-ready backend API

---

## PHASE 3: FACE UI & DEMO (Week 7-8)

### Week 7: FACE Dashboard Component

#### **SPRINT GOAL**: Single-page intelligence dashboard rendering MEMORY/ORACLE/CURIOSITY data

#### Monday (Day 31)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Create component: `frontend/src/components/MarketingIntelligence/FaceDashboard.jsx`
- [ ] Set up layout structure (per Req B.6.2):
  - Top Bar (executive summary)
  - 3-column layout (MEMORY / ORACLE / CURIOSITY cards)
  - Creative Snapshot section
- [ ] Implement static data loading (JSON files for MVP, no backend required per Req B.6.3.3)
- [ ] Create sample JSON: `frontend/src/demo/beauty_brand_scenario.json`

**Deliverable**: FACE UI skeleton

---

#### Tuesday (Day 32)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Implement Top Bar Component (per Req B.6.2.1):
  ```jsx
  <TopBar>
    <MetricCard label="MER" value="2.8x" trend="+5%" />
    <MetricCard label="Blended ROAS" value="2.4x" trend="+12%" />
    <MetricCard label="LTV-ROAS" value="3.1x" trend="+8%" />
    <RiskIndicator level={globalRiskLevel} /> {/* RED/YELLOW/GREEN */}
    <NarrativeSummary text="Here's what changed this week..." />
  </TopBar>
  ```
- [ ] Implement responsive design (≥1280px width per Req B.6.3.1)
- [ ] Add metric tooltips with explanations

**Deliverable**: Top Bar functional

---

#### Wednesday (Day 33)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Implement MEMORY Card (per Req B.6.2.2):
  ```jsx
  <MemoryCard>
    <ChannelTable>
      {channels.map(ch => (
        <ChannelRow 
          name={ch.name}
          spend={ch.spend}
          revenue={ch.revenue}
          roas={ch.roas}
          ltvRoas={ch.ltv_roas}
          status={ch.status} /* winner/loser badge */
        />
      ))}
    </ChannelTable>
  </MemoryCard>
  ```
- [ ] Implement sortable columns (click to sort by ROAS, spend, etc.)
- [ ] Add winner/loser badges with visual indicators (green/red)

**Deliverable**: MEMORY Card functional

---

#### Thursday (Day 34)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Implement ORACLE Card (per Req B.6.2.3):
  ```jsx
  <OracleCard>
    <AlertSection>
      <Alert severity="high" icon="⚠️">
        Creative C12 will fatigue in 3 days (80% probability)
      </Alert>
      <Alert severity="medium" icon="📉">
        TikTok ROI declining 15% over last 7 days
      </Alert>
      <Alert severity="low" icon="📊">
        LTV drifting -8% (recent cohorts vs baseline)
      </Alert>
    </AlertSection>
    <RiskSummary level={globalRiskLevel} />
  </OracleCard>
  ```
- [ ] Implement urgency color coding (red/yellow/green)
- [ ] Add confidence score display

**Deliverable**: ORACLE Card functional

---

#### Friday (Day 35)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Implement CURIOSITY Card (per Req B.6.2.4):
  ```jsx
  <CuriosityCard>
    <ActionList>
      {top3Actions.map((action, idx) => (
        <ActionCard priority={idx + 1}>
          <ActionIcon type={action.action_type} />
          <ActionDescription>{action.rationale}</ActionDescription>
          <ImpactBadge amount={action.estimated_impact_usd} />
          <UrgencyBadge level={action.urgency} />
          <ActionButtons>
            <AcceptButton />
            <RejectButton />
          </ActionButtons>
        </ActionCard>
      ))}
    </ActionList>
  </CuriosityCard>
  ```
- [ ] Implement action type icons (shift/pause/increase)
- [ ] Add Accept/Reject button handlers (MVP: log only, future: execute actions)

**Deliverable**: CURIOSITY Card functional

---

### Week 8: Persona Views & Demo Polish

#### **SPRINT GOAL**: Persona-specific views + 3-minute demo script ready

#### Monday (Day 36)
**Owner**: Frontend Engineer

**Tasks**:
- [ ] Implement Persona Toggle (per Req B.6.3.2):
  ```jsx
  <PersonaSelector>
    <PersonaButton persona="cmo" label="Sarah (CMO)" />
    <PersonaButton persona="vp_growth" label="Jason (VP Growth)" />
    <PersonaButton persona="director" label="Emily (Director)" />
  </PersonaSelector>
  ```
- [ ] Create persona-specific microcopy mappings:
  - **CMO**: "Here's the truth - not what Meta thinks, what actually happened"
  - **VP Growth**: "Creative C12 will fatigue in 3 days"
  - **Director**: "Pause Creative C12 now"
- [ ] Implement context-aware text rendering based on selected persona

**Deliverable**: Persona toggle functional

---

#### Tuesday (Day 37)
**Owner**: Frontend Engineer + QA Engineer

**Tasks**:
- [ ] Lighthouse performance testing (target: ≥90 per Req B.6.4.1)
- [ ] Accessibility audit (target: a11y ≥95 per Req B.6.4.2)
- [ ] Performance optimization:
  - Lazy load charts
  - Code splitting
  - Image optimization
  - Minify CSS/JS
- [ ] Fix accessibility issues (keyboard navigation, screen reader support)

**Deliverable**: Performance and a11y scores meet targets

---

#### Wednesday (Day 38)
**Owner**: Data Engineer + Frontend Engineer

**Tasks**:
- [ ] Create preset demo scenarios (per Req D.2):
  - `frontend/src/demo/beauty_brand_scenario.json` (default)
  - `frontend/src/demo/supplements_brand_scenario.json`
  - `frontend/src/demo/wellness_brand_scenario.json`
- [ ] Implement scenario loader dropdown
- [ ] Test scenario switching (reload all cards with new data)

**Deliverable**: Demo scenarios switchable

---

#### Thursday (Day 39)
**Owner**: Product Designer + Frontend Engineer

**Tasks**:
- [ ] Write 3-minute demo script (per Req D.1.1):
  - 00:00-00:15: Opening hook
  - 00:15-00:45: MEMORY card walkthrough
  - 00:45-01:15: ORACLE card walkthrough
  - 01:15-01:45: CURIOSITY card walkthrough
  - 01:45-02:15: FACE unified view
  - 02:15-02:50: Persona toggle demonstration
  - 02:50-03:00: Closing statement
- [ ] Create live demo cue sheet (per Req D.2):
  - Browser setup instructions
  - Click sequence
  - Talking points
  - Zoom level (110%)
- [ ] Record practice demo video

**Deliverable**: Demo script + cue sheet documented

---

#### Friday (Day 40)
**Owner**: All Team

**Tasks**:
- [ ] Final integration testing (frontend + backend)
- [ ] Bug fixing sprint
- [ ] Demo rehearsal (entire team)
- [ ] Prepare demo slide deck (6 slides per Req D.3):
  1. Problem Statement
  2. Omnify Solution
  3. Module Overview
  4. Live Demo Transition
  5. Impact & Differentiation
  6. Call to Action
- [ ] **PHASE 3 CHECKPOINT**: MVP COMPLETE

**Deliverable**: MVP ready for beta launch

---

## POST-MVP: PHASE 4 - LAUNCH PREP (Week 9-10) - Optional

### Week 9: Pricing & GTM Setup

- [ ] Implement tiered pricing ($499/$799/$1,499)
- [ ] Stripe subscription integration
- [ ] Feature gates (Starter/Growth/Scale)
- [ ] Usage tracking & quota enforcement

### Week 10: Marketing & Beta Launch

- [ ] Create competitive positioning materials
- [ ] Customer case study templates
- [ ] Sales demo training
- [ ] Beta customer onboarding (10-20 DTC brands)

---

## SUCCESS METRICS

### Technical Metrics (MVP Completion)
- [ ] MEMORY: ROI MAPE ≤20%
- [ ] ORACLE: Fatigue prediction AUC ≥0.75
- [ ] CURIOSITY: Allocation regret ≤15%
- [ ] FACE: Lighthouse ≥90, a11y ≥95
- [ ] API latency: ≤5 seconds end-to-end
- [ ] Database: 100K daily_metrics processed in < 2 minutes

### Business Metrics (Post-Launch)
- [ ] 10-20 beta customers onboarded (Week 10-12)
- [ ] 90%+ NPS score from beta customers
- [ ] 3+ customer testimonials
- [ ] 1+ published case study
- [ ] $100K ARR pipeline (Week 12-16)

---

## RISK MANAGEMENT

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Supabase performance issues | Medium | High | Pre-launch load testing, query optimization |
| ORACLE accuracy below threshold | Medium | High | Fallback to rule-based predictions, continuous training |
| Integration complexity with existing platform | Low | Medium | Clean separation, separate namespace |
| Data quality issues (missing metrics) | Medium | High | Robust validation, graceful degradation |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Team availability (holidays, sick days) | High | Medium | 20% buffer in estimates, cross-training |
| Scope creep (feature requests) | Medium | High | Strict MVP definition, defer non-critical features |
| Integration delays | Low | Medium | Parallel development, clear interfaces |
| Third-party API changes | Low | High | Adapter pattern, regular monitoring |

---

## APPENDIX: DELIVERABLES CHECKLIST

### Code Deliverables
- [ ] `backend/database/supabase_client.py` - Supabase connection manager
- [ ] `backend/services/marketing_intelligence/memory_attribution_service.py` - MEMORY module
- [ ] `backend/services/marketing_intelligence/oracle_prediction_service.py` - ORACLE module
- [ ] `backend/services/marketing_intelligence/curiosity_action_service.py` - CURIOSITY module
- [ ] `backend/services/marketing_intelligence/intelligence_orchestrator.py` - Pipeline orchestrator
- [ ] `backend/data_seeds/beauty_brand_seed.py` - Sample data loader
- [ ] `frontend/src/components/MarketingIntelligence/FaceDashboard.jsx` - FACE UI
- [ ] `migrations/001_create_core_schema.sql` - Database schema

### Documentation Deliverables
- [ ] `docs/MVP_ARCHITECTURE.md` - Technical architecture
- [ ] `docs/API_REFERENCE.md` - API endpoint documentation
- [ ] `docs/PERSONA_GUIDE.md` - Sarah/Jason/Emily use cases
- [ ] `docs/DEMO_SETUP.md` - How to run 3-minute demo
- [ ] `docs/DATA_SEEDS.md` - Sample data documentation
- [ ] `docs/demo/3min_demo_script.md` - Demo script
- [ ] `docs/demo/live_demo_cue_sheet.md` - Demo execution guide
- [ ] `docs/demo/demo_slide_deck.pptx` - Presentation slides

### Test Deliverables
- [ ] Unit tests for all 3 modules (≥80% coverage)
- [ ] Integration tests (end-to-end pipeline)
- [ ] API tests (Postman collection)
- [ ] Performance tests (load testing scripts)
- [ ] Accuracy validation tests (against historical data)

---

**Roadmap Version**: 1.0  
**Status**: Ready for Team Assignment  
**Next Steps**: Leadership approval → Team kickoff → Sprint 0 execution

