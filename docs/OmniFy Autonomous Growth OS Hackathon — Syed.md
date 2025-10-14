<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# OmniFy Autonomous Growth OS Hackathon — Final Enhanced Version

Note: This is the master, college-ready hackathon brief that preserves all original technical specs and governance while integrating the strategic Autonomous Growth OS enhancements. All changes are clearly marked as [PRESERVED], [ENHANCED], or [NEW]. Modules are presented as Seven Brain Modules (formerly “Six Senses”) for strategic alignment.

## Executive Summary

Build a mini Autonomous Growth OS in 48 hours featuring seven unified Brain Modules that predict 7–14 day creative fatigue, optimize proactively, and get smarter every cycle through compound learning. All original acceptance metrics, constraints, integrations, multilingual requirements, and governance are preserved. The enhanced framework adds an ORACLE predictive module, a system-wide learning/data plane, and cross-module intelligence to demonstrate measurable improvement over time and autonomous action readiness.

## A. Scope, Audience, and Program Rules

[PRESERVED]

- Duration: 48 hours. Prize pool: \$1,600. IST timezone. Audience: Program Directors, Faculty Mentors, Student Teams. Persona: Marketing Director (desktop-first 1280px, responsive down to mobile). Languages: English and Spanish (teams must declare locale).
- Six original modules and all acceptance criteria (AUC ≥0.70, Silhouette ≥0.45, bandit regret ≤15%, latency ≤1s, ROI/CLV accuracy thresholds), operational constraints, governance (consent, drift alerts with KL ≤0.1, FinOps), integrations (Meta/Instagram, TikTok, YouTube, Shopify, Stripe), adapters (mock only), and “no live posting” are preserved.

[ENHANCED]

- Renaming and expansion: “Six Senses” → “Seven Brain Modules” to add ORACLE predictive intelligence and unify everything under the Autonomous Growth OS vision.
- Compound Learning: Each module must show learning over time and feed the shared Brain Data Plane for cross-module intelligence, with an integration harness proving end-to-end operation and measurable improvement.

[NEW]

- ORACLE module for predictive fatigue and LTV forecasting as the strategic centerpiece of proactive marketing.


## B. The Seven Brain Modules

1) ORACLE — Predictive Intelligence Engine [NEW]

- Purpose: Predict creative fatigue 7–14 days ahead, forecast LTV, and surface pre-emptive optimization opportunities. Strategic differentiator enabling proactive vs. reactive marketing.
- Inputs (JSON): historical performance (creativeid, platform, date, impressions, clicks, spend, conversions, frequency, ctr, cpc), creative metadata (format, durationseconds, copylength, ctatype), audience stats (size, overlappercentage, saturationlevel).
- Outputs (JSON): fatiguepredictions (creativeid, fatigueprobability7d, fatigueprobability14d, predictedperformancedrop%, confidenceinterval, keyriskfactors, recommendedrefreshdate), ltvpredictions (customersegment, predicted90dltv, ltvconfidence, acquisitioncostefficiency), learninginsights (modelaccuracytrend, calibration, featureimportanceevolution).
- Constraints: Train ≤10 min on 500k records; RAM ≤4 GB; scoring ≤500 ms; deterministic with seed.
- Acceptance: Fatigue AUC ≥0.75 (7d), ≥0.65 (14d). LTV RMSE ≤25%. Must demonstrate improved accuracy after learning cycles.
- Scoring emphasis: Prediction Accuracy, Learning Demonstration, Business Impact, Speed, Explainability.

2) EYES — At-Risk Segments (30/60/90-day churn) [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve original clustering + churn scoring with consent fields; train ≤5 min/100k; RAM ≤2 GB; Silhouette ≥0.45; AUC ≥0.70 (30d).
- ENHANCED: Learning loop fields for segmentevolutiontracking, per-segment predictionaccuracy, crossplatformbehaviorpatterns; feeds to ORACLE (improve LTV), VOICE (personalize content), CURIOSITY (trigger retention).

3) VOICE — Repurposing Studio (Instagram/TikTok-first, EN+ES) [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve original repurposing with brand-safety ≥95%, reading grade ≤9, toxicity 0, token cost cap, video processing ≤2 min, IG/TikTok Export Packs required, multilingual EN+ES.
- ENHANCED: Track creativeDNA, audiencepersonalization, performanceprediction, fatigueresistancescore; integrate ORACLE (refresh before fatigue), EYES (segment personalization), MEMORY (performance tracking).

4) CURIOSITY — Budgeted Bandit with Uncertainty Gate [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve real-time allocation under budget with uncertainty escalation; decision ≤300 ms; RAM ≤512 MB; regret ≤15% vs. oracle.
- ENHANCED: Proactive reallocation using ORACLE fatigue predictions; segment-weighted allocation via EYES LTV/segment value; log learningtrajectory and compoundoptimization.

5) MEMORY — Channel ROI and 90-Day CLV Comparator [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve ROI reporting and CLV prediction; 5M events ≤2 min; RAM ≤2 GB; ROI MAPE ≤20%; CLV RMSE ≤25%; drift alerts (KL ≥0.1) with retrain suggestion; leaderboard and budget moves with rationale.
- ENHANCED: Attributionmodelevolution, crossplatformcustomerjourney, predictiveroiforecasting, learningattributionconfidence; feeds ROI, journey, and evolution signals to ORACLE and CURIOSITY.

6) REFLEXES — Minute-Level Anomalies and Two Actions [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve precision ≥0.80, recall ≥0.80, latency ≤1s, FP ≤3%, FinOps table with 3 reducers.
- ENHANCED: Classify predicted changes vs. real anomalies using ORACLE; intelligentactionselection leveraging MEMORY and EYES; learninganomalypatterns and optional automatedexecutioncapability.

7) FACE — Single-Page Insights (Director Persona) [PRESERVED + ENHANCED]

- Purpose and Specs: Preserve desktop-first SPA (1280px), Lighthouse ≥90, a11y ≥95, no backend; npm run dev; badges for consent, drift, safety, export readiness.
- ENHANCED: Learningprogress indicators, predictivealertspanel (7–14 day fatigue), autonomousactiontimeline, compoundlearningvisualization, integrationhealthmonitor for all seven modules.


## C. Deliverables and Eligibility

[PRESERVED]

- Seven module folders (code, README, .env.example, strict JSON IO), harness pass logs, Creative Knowledge Graph (JSONL: contentid, audiences, variants, outcomes CTR/CVR/ROI, repurposedfrom; IDs only, no PII), 3-minute demo video, 1-page PDF summary.

[ENHANCED]

- Learning Demonstration: Show measurable improvement over time for predictions and/or allocation outcomes.
- Integration Harness: Prove all seven modules operate together and exchange intelligence.
- Autonomous Capability: Demonstrate uncertainty gating and at least one proactive, ORACLE-driven optimization in CURIOSITY or REFLEXES.
- Compound Metrics: Quantify cumulative improvement (e.g., higher lift, reduced regret, better AUC/CLV RMSE after N cycles).


## D. Connectors, Adapters, and Mock Interfaces

[PRESERVED]

- Social Ads: Meta/Instagram, TikTok, YouTube, X, LinkedIn (mocks only). Commerce/Payments: Shopify, Stripe. Analytics: first-party event schema; warehouse export stubs (JSON/CSV/Parquet). No live posting. Adapters must handle mock rate-limits, retries/backoff, auth stubs, metric mapping, with unit tests (2 happy, 1 throttled).

[API references: official docs]

- Meta/Instagram Marketing API endpoints and scopes
- TikTok Business API endpoints and scopes
- YouTube Data API v3 endpoints and scopes
- Shopify Admin API endpoints and scopes
- Stripe API core resources and permissions model


## E. Brain Data Plane and Knowledge Base

[PRESERVED]

- Data plane: Parquet/CSV, optional DuckDB; modules output JSON/assets; schemas enforced by harness; brain.config.yaml for paths, seeds, cost caps, locales. Production references: Postgres/pgvector, Timescale/ClickHouse, S3, Snowflake/BigQuery/dbt, optional Kafka/Kinesis, Feast, MLflow, Vault/KMS, audit logs. Knowledge Base: Creative Knowledge Graph (required), optional embeddings index (FAISS/pgvector) for retrieval, optional feature store for outfeatures.

[ENHANCED]

- Learning Pipeline: Automated feedback loop across all modules with model/version tracking.
- Performance Tracking: Continuous monitoring of AUC, RMSE, regret, precision/recall, and ROI metrics by cohort and over time.
- Model Evolution Storage: Versioned artifacts, calibration metrics, and feature-importance evolution.
- Cross-Module Sharing: Unified knowledge base accessible to all modules for compound learning.


## F. Judging (100 points) — Harness-First

[PRESERVED STRUCTURE]

- Impact 20, Technical Excellence 20, Efficiency 15, Economics (Lift per \$) 10, Safety/Governance 10, UX 15, Reproducibility 10. Harness run contributes up to 30 points.

[ENHANCED CRITERIA]

- Autonomous Intelligence 20: Learning loops, proactive decisions, uncertainty gating.
- Predictive Accuracy 15: Early fatigue warnings and LTV forecasting quality.
- Economics/Compound Lift 10: Demonstrated ROI improvement over time.
- Bonus: Learning Demonstration (+15), Autonomous Execution (+10), Cross-Module Intelligence (+5).


## G. Timeline (IST)

- Fri 6:00 PM kickoff; Sat 11:00 AM and 6:00 PM checkpoints; Sun 3:00 PM final submission; Sun 6:00 PM demos and awards.


## H. Governance and Ops Minimums

- Data contracts: profileid, consentpurpose, consentexpiry. Drift alerts at KL ≥0.1. FinOps: include cost table and list 3 reducers (compression, batching, caching, etc.). Multilingual: EN and ES. Channel adapters ready for email/SMS/ads. Agentic weekly plan bonus with human approval. Mock audit log required.


## I. Rules and IP

- Code of Conduct. No scraping. No real user data. Brand-safety gate. Teams own their code; OmniFy receives a non-exclusive, royalty-free evaluation license. Winners may receive integration contracts or internships.


## J. Submission Checklist

[PRESERVED]

- Seven module folders, strict JSON IO, harness pass logs, Creative Knowledge Graph JSONL (IDs only), 3-min demo video, 1-page PDF, team roster + contact.

[ENHANCED]

- Evidence of learning improvement, integration harness results, autonomous capability proof, and compound improvement metrics included in demo and PDF.


## K. Flyers

Flyer A — Recruiting Essentials [ENHANCED]

- Challenge: Build an Autonomous Growth OS — seven learning modules that predict fatigue weeks ahead, optimize proactively, and improve every cycle. Deliver code, prove with harness, and demo in 48 hours.
- Modules: ORACLE, EYES, VOICE, CURIOSITY, MEMORY, REFLEXES, FACE.
- Deliverables: Seven code folders, logs, Creative Graph, 3-min video, 1-pager.
- Connectors: Meta/IG, TikTok, YouTube, Shopify, Stripe (mock only).
- Judging: Autonomous Intelligence, Predictive Accuracy, ROI lift, Tech Excellence, UX, Safety, Integration.
- Timeline: Fri 6 PM → Sun 6 PM (IST). Prizes: \$1,600.

Flyer B — Pro Track Acceptance Gates [ENHANCED]

- Key Gates: AUC ≥0.70 (churn), CLV RMSE ≤25%, regret ≤15%, precision/recall ≥0.80, latency ≤1s, cost controls logged.
- Adapter Readiness: Mock rate-limits, retries, auth stubs, acceptance tests.
- Language: EN + ES (declared locale).
- UX: Desktop-first 1280px, responsive; a11y ≥95; Lighthouse ≥90.
- Learning: Evidence required; proactive optimizations; unified system integration proved via harness.


## L. Confidential Internal Backlog (for OmniFy use)

- 30/60/90 plan for live OAuth: IG/Meta, TikTok, YouTube, Shopify, Stripe; identity/CDP/data contracts and consent audit; model governance, A/B + holdout, deliverability checks; agentic planner + marketplace; production data plane; security/privacy; FinOps; knowledge moat; KPIs + risks; roles; GA evaluation and go/no-go.
- Learning Roadmap: MLOps for continuous model improvement; compound intelligence via cross-client patterns; autonomous scaling architecture; predictive moat reinforcement.


## M. Developer Aids (from FACE SPA and Harness sections)

- Harness Test Plan: Schema checks, functional acceptance, constraints, metrics validation, ops/governance, negative cases, adapter throttling. PASS/FAIL example logs with timestamps, module, inputs, result, reason.
- FACE SPA Build: React SPA desktop-first with scripts for dev/build/test/lint; folder structure for components/widgets/pages/services/domain; deploy recipes for Vercel/Netlify with SPA routing and environment-variable guidance. No secrets in repo.


## Enhanced Elevator Pitch

Build the next wave of autonomous marketing intelligence with seven unified modules that predict 7–14 day creative fatigue, auto-optimize budgets and actions, and get exponentially smarter with every dollar spent — all in 48 hours. Preserve rigorous acceptance metrics and governance while proving learning, integration, and autonomous decision-making that form Omnify’s compound learning moat.

