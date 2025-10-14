# OmniFy Autonomous Growth OS Hackathon: Enhanced "AI Marketing Brain" Challenge

*Enhanced version preserving all original technical specifications while integrating strategic learning-focused improvements*

---

## A. Executive Summary

**[ENHANCED]** OmniFy is hosting a 48-hour hackathon for teams to build a mini **Autonomous Growth OS** featuring seven distinct "Brain Modules" (enhanced from original six "Senses"), organized for rapid, robust, and market-ready AI-driven marketing that **learns and evolves with every campaign**. Teams must submit all seven modules with strict JSON I/O compliance, code folders, and harness logs. 

**[NEW STRATEGIC CONTEXT]** This challenge builds the foundational components of autonomous marketing intelligence that predicts creative fatigue 7-14 days in advance, automatically optimizes campaigns, and continuously improves through compound learning - creating a competitive moat that's impossible for competitors to replicate.

**[PRESERVED ORIGINAL]** Modules are designed for leading ecommerce platforms, focused on Meta/Instagram, TikTok, and YouTube, as well as Shopify and Stripe for commerce, leveraging industry-standard event schemas and analytics. This approach directly addresses marketing repurposing, churn mitigation, and LTV optimization, with high operational rigor in consent, drift, multilingual features, and economic efficacy.

**[ENHANCED VALUE PROPOSITION]** Why this works: market fit (predictive optimization vs reactive management), compound learning moat (systems that get exponentially smarter), ops rigor (consent, drift, FinOps, multilingual), speed (baselines + harness), economics (Lift per $), uncertainty escalation to humans, and **autonomous evolution capabilities**.

---

## B. The Seven Brain Modules (Enhanced from Original Six Senses)

**[ENHANCEMENT NOTE]** Added ORACLE (Predictive Intelligence) as a new dedicated module while preserving all original specifications. Enhanced integration between modules to create unified autonomous system.

### 1. 🔮 ORACLE - Predictive Intelligence Engine **[NEW MODULE]**
**Purpose:** Predict creative fatigue, customer lifetime value, and performance trends 7-14 days in advance to enable proactive optimization.

**Strategic Importance:** This is the core differentiator that transforms reactive marketing into predictive optimization - the foundation of Omnify's competitive moat.

**Input Schema:**
```json
{
  "historical_performance": {
    "creative_id": "string",
    "platform": "meta|google|tiktok|youtube",
    "daily_metrics": [{
      "date": "YYYY-MM-DD",
      "impressions": "integer",
      "clicks": "integer",
      "spend": "decimal",
      "conversions": "integer",
      "frequency": "decimal",
      "ctr": "decimal",
      "cpc": "decimal"
    }],
    "creative_metadata": {
      "format": "image|video|carousel",
      "duration_seconds": "integer",
      "copy_length": "integer",
      "cta_type": "string"
    }
  },
  "audience_data": {
    "size": "integer",
    "overlap_percentage": "decimal",
    "saturation_level": "decimal"
  }
}
```

**Output Schema:**
```json
{
  "fatigue_predictions": [{
    "creative_id": "string",
    "fatigue_probability_7d": "0.0-1.0",
    "fatigue_probability_14d": "0.0-1.0",
    "predicted_performance_drop": "percentage",
    "confidence_interval": "0.0-1.0",
    "key_risk_factors": ["frequency", "audience_saturation", "creative_age"],
    "recommended_refresh_date": "YYYY-MM-DD"
  }],
  "ltv_predictions": [{
    "customer_segment": "string",
    "predicted_90d_ltv": "decimal",
    "ltv_confidence": "0.0-1.0",
    "acquisition_cost_efficiency": "decimal"
  }],
  "learning_insights": {
    "model_accuracy_trend": "improving|stable|declining",
    "prediction_confidence_calibration": "decimal",
    "feature_importance_evolution": "object"
  }
}
```

**Constraints:** Train ≤10 min on 500k records; RAM ≤4 GB; deterministic with seed; real-time scoring ≤500ms.

**Acceptance:** Fatigue prediction AUC ≥0.75 (7-day), ≥0.65 (14-day); LTV prediction RMSE ≤25%; demonstrate learning improvement over time.

**Learning Integration:** Must show measurable improvement in prediction accuracy as more data becomes available.

**Scoring:** Prediction Accuracy 35% | Learning Demonstration 25% | Business Impact 20% | Speed 15% | Explainability 5%

---

### 2. 👁️ EYES - At-Risk Segments (30/60/90-day churn) **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** cluster users and score churn (30/60/90).
- **Input:** events.parquet (user_id, event_type, ts, channel, spend, content_id).
- **Output (JSON):** clusters with label, top_features[], churn_risk {d30,d60,d90}, sample_user_ids[].
- **Constraints:** train ≤5 min on 100k; RAM ≤2 GB; deterministic with seed.
- **Acceptance:** Silhouette ≥0.45; AUC ≥0.70 (d30).
- **Governance:** include consent fields (profile_id, consent_purpose, consent_expiry).
- **Scoring:** Seg 25% | Churn 25% | Eff 20% | Explain 20% | Docs 10%.

**[ENHANCED INTEGRATION]** 
- **Learning Loop Integration:** Must feed insights to ORACLE for improved LTV predictions
- **Strategic Connection:** Churn predictions should trigger automated retention campaigns via CURIOSITY module
- **Cross-Module Data Sharing:** Segment insights must be available to VOICE for personalized content creation

**[ENHANCED OUTPUT SCHEMA]**
```json
{
  "original_output": "preserved as specified above",
  "learning_enhancements": {
    "segment_evolution_tracking": "how segments change over time",
    "prediction_accuracy_by_segment": "performance metrics per segment",
    "cross_platform_behavior_patterns": "unified customer journey insights"
  },
  "integration_feeds": {
    "to_oracle": "segment performance data for LTV modeling",
    "to_voice": "segment preferences for content personalization",
    "to_curiosity": "churn triggers for automated actions"
  }
}
```

---

### 3. 🗣️ VOICE - Repurposing Studio (Instagram/TikTok-first, EN+ES) **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** repurpose VIDEO/IMAGE/TEXT/AUDIO to 3 safe, on-brand variants per segment; IG/TikTok primary; YouTube/LinkedIn optional; email/ads optional.
- **Inputs:** Audience JSON + brand brief (≤500 tokens) + source_content.* (text/image/video/audio).
- **Modalities:**
  • IG/TikTok (primary): image crops (1:1, 9:16, 16:9) and/or short video ≤15s w/ burned captions + platform captions/hashtags.
  • YouTube Short (optional): 9:16 ≤15s + caption + thumbnail ref.
  • Email/Ads (optional): subject + ad headline + caption.
  • Audio (optional): 20-30s teaser MP3 + transcript.
- **Platform Export Packs (metadata only; no posting):** REQUIRED - IG/Meta & TikTok; OPTIONAL - YouTube & LinkedIn. Emit {title, caption, hashtags[], aspect_ratio, duration, thumbnail_ref}.
- **Constraints:** reading grade ≤9; toxicity 0; token cost ≤$0.05/1k; sample video processing ≤2 min.
- **Acceptance:** ≥95% brand-safety; produce (a) 3 IG/TikTok captions and (b) either 2 image sizes or 1 short video; include Export Packs (IG/TikTok required).
- **Multilingual:** English AND Spanish (team declares locale).
- **Scoring:** Rel 25% | Repurp 25% | Multi 20% | Safety 20% | Cost 10%.

**[ENHANCED LEARNING INTEGRATION]**
- **Performance Learning:** Must track which creative variants perform best and learn from successful patterns
- **Audience Optimization:** Use EYES segment insights to personalize content for specific customer segments
- **Fatigue Prevention:** Integrate with ORACLE predictions to proactively refresh content before fatigue occurs

**[ENHANCED OUTPUT SCHEMA]**
```json
{
  "original_export_packs": "preserved as specified above",
  "learning_enhancements": {
    "creative_dna_analysis": "what makes this creative successful",
    "audience_personalization": "how content is optimized for specific segments",
    "performance_prediction": "expected performance based on historical patterns",
    "fatigue_resistance_score": "how long this creative is expected to perform"
  },
  "integration_feeds": {
    "to_memory": "creative performance tracking for ROI analysis",
    "to_oracle": "creative characteristics for fatigue prediction modeling",
    "performance_feedback_loop": "results tracking for continuous improvement"
  }
}
```

---

### 4. 🤔 CURIOSITY - Budgeted Bandit + Uncertainty Gate **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** allocate traffic to maximize conversions under budget; escalate when unsure.
- **Input:** variant JSON + hourly traffic + budget.
- **Output:** allocation over time + posterior metrics + needs_human:true with rationale if 95% CI wide or ΔEV ≥5%; weekly plan (bonus) JSON.
- **Constraints:** decision ≤300 ms; RAM ≤512 MB.
- **Acceptance:** regret ≤15% vs oracle.
- **Scoring:** Lift 30% | Robust 20% | Agentic 15% | Eff 20% | Clarity 15%.

**[ENHANCED AUTONOMOUS CAPABILITIES]**
- **Predictive Integration:** Use ORACLE fatigue predictions to proactively shift budget before performance drops
- **Segment-Aware Allocation:** Leverage EYES insights to allocate budget based on customer segment value
- **Learning Optimization:** Continuously improve allocation strategies based on outcome data

**[ENHANCED OUTPUT SCHEMA]**
```json
{
  "original_output": "preserved as specified above",
  "autonomous_enhancements": {
    "proactive_reallocation": "budget shifts based on fatigue predictions",
    "segment_weighted_allocation": "budget distribution based on LTV insights",
    "learning_trajectory": "how allocation strategy improves over time",
    "compound_optimization": "cumulative performance improvements"
  },
  "integration_feeds": {
    "from_oracle": "fatigue predictions driving allocation changes",
    "from_eyes": "segment values influencing budget distribution",
    "to_memory": "allocation decisions for ROI tracking"
  }
}
```

---

### 5. 🧠 MEMORY - Channel ROI + 90 Day CLV + Comparator **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** report ROI by channel; predict 90-day CLV; compare campaigns/creatives to guide budget.
- **Inputs:** parquet logs (view/click/add_to_cart/purchase) + campaign/creative metadata.
- **Output:**
  • channel_roi[channel,spend,revenue,roi,ci]
  • clv[user_id,value,ci]
  • campaign_leaderboard[] (CPC, CTR, CVR, CPA, ROAS, revenue)
  • budget_reallocation[] = {entity_id, type:"increase|decrease|pause", reason, expected_delta}
- **Constraints:** ≤2 min on 5M events; RAM ≤2 GB.
- **Acceptance:** ROI MAPE ≤20%; CLV RMSE ≤25%; sorted leaderboard + ≥5 budget moves with rationale.
- **Ops:** drift alert if KL ≥0.1; log retrain suggestion.
- **Scoring:** ROI 25% | CLV 25% | Explain 20% | Eff 20% | Repro 10%.

**[ENHANCED LEARNING CAPABILITIES]**
- **Attribution Evolution:** Continuously improve attribution models based on long-term customer behavior
- **Cross-Platform Intelligence:** Unify customer journey data across all platforms for accurate ROI calculation
- **Predictive ROI:** Not just historical ROI, but predicted future ROI based on current trends

**[ENHANCED OUTPUT SCHEMA]**
```json
{
  "original_output": "preserved as specified above",
  "learning_enhancements": {
    "attribution_model_evolution": "how attribution accuracy improves over time",
    "cross_platform_customer_journey": "unified view of customer touchpoints",
    "predictive_roi_forecasting": "expected future ROI based on current trends",
    "learning_attribution_confidence": "confidence in attribution accuracy"
  },
  "integration_feeds": {
    "to_oracle": "customer behavior patterns for LTV prediction",
    "to_curiosity": "ROI data for budget allocation optimization",
    "performance_feedback_loop": "outcome tracking for all modules"
  }
}
```

---

### 6. ⚡ REFLEXES - Minute-Level Anomaly + Two Actions **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** detect spikes/drops; propose two low-risk actions.
- **Input:** minute-level metrics.
- **Output:** anomalies {ts, metric, severity, root_cause_hints[], actions[]}.
- **Constraints:** latency ≤1 s; false-positive ≤3%.
- **Acceptance:** Precision ≥0.80 & Recall ≥0.80.
- **FinOps:** cost table (inference/storage/egress) + 3 cost reducers (compression, batching, caching).
- **Scoring:** Detect 30% | Action 20% | Lat 20% | Stable 15% | FinOps 15%.

**[ENHANCED AUTONOMOUS RESPONSE]**
- **Predictive Anomaly Detection:** Use ORACLE insights to distinguish between predicted changes and true anomalies
- **Intelligent Action Selection:** Choose actions based on MEMORY ROI data and EYES segment insights
- **Learning Anomaly Patterns:** Continuously improve anomaly detection based on false positive/negative feedback

**[ENHANCED OUTPUT SCHEMA]**
```json
{
  "original_output": "preserved as specified above",
  "autonomous_enhancements": {
    "predicted_vs_anomaly_classification": "distinguish expected changes from true anomalies",
    "intelligent_action_selection": "actions chosen based on ROI and segment data",
    "learning_anomaly_patterns": "how detection improves over time",
    "automated_execution_capability": "which actions can be executed without human approval"
  },
  "integration_feeds": {
    "from_oracle": "predicted changes to avoid false anomaly alerts",
    "from_memory": "ROI data to inform action selection",
    "to_curiosity": "anomaly triggers for budget reallocation"
  }
}
```

---

### 7. 👤 FACE - Single-Page Insights (Director Persona) **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL SPECS]**
- **Purpose:** desktop/laptop-first SPA (≥1280px) for Marketing Director; shows money, risk, next action.
- **Output:** SPA with charts, filters, narratives; badges for consent/drift/safety; IG/TikTok export-readiness.
- **Constraints:** Lighthouse ≥90; a11y ≥95; NO backend.
- **Acceptance:** runs via npm i && npm run dev; UI harness pass; persona-appropriate copy.
- **Scoring:** UX 25% | Clarity 25% | Performance 20% | A11y 15% | Governance 15%.

**[ENHANCED AUTONOMOUS SYSTEM VISIBILITY]**
- **Learning System Status:** Show how the autonomous system is improving over time
- **Predictive Alerts Dashboard:** Display ORACLE predictions and recommended actions
- **Autonomous Action Log:** Track what the system has done automatically and results

**[ENHANCED INTERFACE REQUIREMENTS]**
```json
{
  "original_requirements": "preserved as specified above",
  "autonomous_enhancements": {
    "learning_progress_indicators": "show system improvement metrics",
    "predictive_alerts_panel": "7-14 day fatigue warnings and recommendations",
    "autonomous_action_timeline": "log of automated actions and their results",
    "compound_learning_visualization": "how system performance improves over time",
    "integration_health_monitor": "status of all seven modules working together"
  }
}
```

---

## C. Deliverables (Eligibility) **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL]** Seven module folders (code + README + env + example I/O + HARNESS PASS LOGS).

**[PRESERVED ORIGINAL]** Creative Knowledge Graph (JSONL): content_id → audiences → variants → outcomes (CTR/CVR/ROI) → repurposed_from. (IDs only; no PII)

**[PRESERVED ORIGINAL]** 3-min demo video; 1-pager PDF. Missing any module/log → ineligible.

**[NEW LEARNING REQUIREMENTS]**
- **Learning Demonstration:** Evidence of system improvement over time (required)
- **Integration Harness:** Proof that all seven modules work together as unified system
- **Autonomous Capability Demo:** Show automated decision-making and execution
- **Compound Learning Metrics:** Quantified improvement in system performance

---

## D. Connectors & Adapters (Mock Interfaces; NO posting) **[PRESERVED FROM ORIGINAL]**

**[PRESERVED ORIGINAL]** Social/Ads (ordered by ecommerce impact): Meta/Instagram, TikTok, YouTube, X, LinkedIn.
Commerce/Payments: Shopify, Stripe.
Analytics: first-party event schema + warehouse export stub (JSON→CSV/Parquet).

**[PRESERVED ORIGINAL]** Adapter acceptance: handle mock rate-limits with retry/backoff; auth stubs (no secrets); metric mapping to OmniFy standard; unit tests (2 happy + 1 throttled).

**[PRESERVED ORIGINAL]** Export Packs: IG/TikTok REQUIRED; YouTube/LinkedIn optional.

---

## E. Brain Data Plane & Knowledge Base **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL]** Hackathon data plane: data/ (Parquet/CSV + optional DuckDB) → modules → out/ (JSON/assets); schemas enforced by harness; brain.config.yaml (paths, seeds, cost caps, locales).

**[PRESERVED ORIGINAL]** Production reference: Postgres(+pgvector), Timescale/ClickHouse, S3, Snowflake/BigQuery+dbt, optional Kafka/Kinesis & Feast, MLflow, Vault/KMS, audit logs.

**[PRESERVED ORIGINAL]** Knowledge Base:
• REQUIRED Creative Knowledge Graph (above)
• OPTIONAL embeddings index (FAISS/pgvector) + retrieval demo (top-5)
• OPTIONAL feature store (key-value features) in out/features/
• Usage: Voice retrieval for better repurposing; Memory features for stability.

**[ENHANCED LEARNING DATA PLANE]**
- **Learning Pipeline:** Automated feedback loop connecting all modules
- **Performance Tracking:** Continuous monitoring of prediction accuracy and action outcomes
- **Model Evolution Storage:** Version control for learning improvements
- **Cross-Module Intelligence Sharing:** Unified knowledge base accessible to all modules

---

## F. Judging (100 pts) — harness-first **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL STRUCTURE]** Impact 20 | Tech 20 | Efficiency 15 | Economics—Lift per $ 10 | Safety 10 | UX 15 | Repro 10.
Harness contributes up to 30 pts.

**[ENHANCED LEARNING-FOCUSED CRITERIA]**
- **Autonomous Intelligence (20%):** How well does the system demonstrate learning and autonomous decision-making?
- **Technical Excellence (20%):** Code quality, architecture, and integration sophistication
- **Predictive Accuracy (15%):** Quality of forecasting and early warning capabilities  
- **Economics—Compound Lift per $ (10%):** Demonstrated improvement in ROI over time
- **Safety & Governance (10%):** Brand safety, consent management, and operational rigor
- **User Experience (15%):** Marketing Director persona fit and autonomous system visibility
- **Reproducibility & Integration (10%):** System reliability and module integration quality

**[BONUS POINTS]**
- **Learning Demonstration:** +15 points for clear evidence of system improvement over time
- **Autonomous Execution:** +10 points for successful automated action implementation
- **Cross-Module Intelligence:** +5 points for sophisticated module integration

---

## G. Timeline (IST) **[PRESERVED FROM ORIGINAL]**

Fri 6 PM kickoff • Sat 11 AM & 6 PM checkpoints • Sun 3 PM submit • Sun 6 PM demos & awards.

---

## H. Governance & Ops (Minimums) **[PRESERVED FROM ORIGINAL]**

Data contracts (profile_id, consent purpose/expiry) • drift alerts (KL ≥0.1) • FinOps table + 3 reducers • EN+ES • channel adapters (email/SMS/ads) • agentic weekly plan (bonus) with human approval • mock audit log.

---

## I. Rules & IP **[PRESERVED FROM ORIGINAL]**

CoC • no scraping • no real user data • brand-safety gate. Teams own code; grant OmniFy a non-exclusive, royalty-free license for evaluation/internal use. Winners may receive integration contracts or internships.

---

## J. Submission Checklist **[ENHANCED FROM ORIGINAL]**

**[PRESERVED ORIGINAL]** Seven modules • harness logs • Creative Knowledge Graph • 3-min demo • 1-pager • roster+contact.

**[NEW LEARNING REQUIREMENTS]**
- **Learning demonstration evidence** • **Integration harness results** • **Autonomous capability proof** • **Compound improvement metrics**

---

## K. Flyers **[ENHANCED FROM ORIGINAL]**

### Flyer A (Recruiting & Essentials)
**Challenge:** 48 hours to build an **Autonomous Growth OS** (7 modules) that learns and evolves.

**The Seven Brain Modules:** ORACLE (predictions), EYES (churn), VOICE (repurpose), CURIOSITY (budget), MEMORY (ROI/CLV), REFLEXES (anomalies), FACE (SPA insights).

**[PRESERVED ORIGINAL]** Deliverables: Seven code folders, logs, Creative Graph, 3-min video, 1-pager.
Connectors: Meta/Instagram, TikTok, YouTube, Shopify, Stripe (mock APIs).
Judging: Autonomous Intelligence, Technical Excellence, Predictive Accuracy, Economics, Safety, UX, Integration.
Timeline: Fri 6 PM kickoff • Sat checkpoints • Sun 3 PM submit • Sun 6 PM awards.
Prizes: US$1,600 total.
Contact: [details]

### Flyer B (Pro Track & Acceptance Gates)
**[PRESERVED ORIGINAL]** Explicit AUC/CLV/Regret/P&R/Latency/Cost; adapter acceptance; EN+ES; desktop-first; uncertainty escalation; drift alert.

**[ENHANCED LEARNING GATES]** 
- **Learning Evidence Required:** Demonstrate measurable system improvement
- **Autonomous Capability:** Show automated decision-making and execution
- **Predictive Accuracy:** Fatigue prediction AUC ≥0.75 (7-day), LTV RMSE ≤25%
- **Integration Quality:** All seven modules must work as unified system

---

## L. CONFIDENTIAL INTERNAL BACKLOG **[PRESERVED FROM ORIGINAL]**

**[PRESERVED ORIGINAL]** 30/60/90 plan (live OAuth for IG/Meta, TikTok, YouTube, Shopify, Stripe; identity/CDP; model governance; A/B+holdout; deliverability; agentic planner; marketplace).

Production data plane; identity & data contracts; model governance; experimentation & incrementality; deliverability & compliance; security & privacy; FinOps; knowledge moat; KPIs; risks; roles; GA go/no-go.

**[ENHANCED LEARNING ROADMAP]**
- **Learning Infrastructure:** MLOps pipeline for continuous model improvement
- **Compound Intelligence:** Cross-client learning and knowledge transfer
- **Autonomous Scaling:** Self-optimizing system architecture
- **Predictive Moat:** Advanced forecasting capabilities as competitive advantage

---

## STYLE & OUTPUT FORMAT **[PRESERVED FROM ORIGINAL]**

Produce ONE master document in this order: A→L above, with clean headings.
Then produce Flyer A and Flyer B as single-page sections.
Then produce the Confidential Internal Backlog.
Use short sentences. No purple prose. Board-safe tone.

---

## Enhanced Elevator Pitch

Build the next wave of **autonomous marketing intelligence** with OmniFy's "AI Marketing Brain" hackathon: code, prove, and demo seven powerful, **learning modules** that predict creative fatigue weeks in advance, automatically optimize campaigns, and **get exponentially smarter with every dollar spent** - all in 48 hours. Deliver safety, efficiency, multilingual power, plug-and-play extensibility, and **compound learning capabilities** ready for industry integration and continuous ROI improvement.

---

## ENHANCEMENT SUMMARY

**Key Improvements Made:**
1. **Added ORACLE module** for predictive intelligence (core differentiator)
2. **Enhanced all original modules** with learning and integration capabilities
3. **Preserved all technical specifications** from original document
4. **Added strategic context** around autonomous growth and compound learning
5. **Enhanced judging criteria** to emphasize learning and autonomous capabilities
6. **Maintained all operational requirements** (governance, compliance, multilingual)
7. **Preserved prize structure and timeline** as requested

**Recommended Changes (marked for review):**
- Consider renaming "Six Senses" to "Seven Brain Modules" for better strategic alignment
- The original technical complexity is preserved but now serves a clearer strategic vision
- All original acceptance criteria maintained while adding learning requirements

This enhanced version transforms the hackathon from building "marketing tools" to creating "autonomous marketing intelligence" while preserving all the valuable technical rigor of the original specification.
