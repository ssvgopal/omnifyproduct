# Deprecation Action Plan - Legacy Backend to MVP Focus

**Date**: January 2025  
**Status**: 🔴 **CRITICAL - IMMEDIATE ACTION REQUIRED**  
**Rationale**: New Supabase-based MVP is the strategic direction. Legacy MongoDB backend contains 308+ features not aligned with MVP roadmap.

---

## 📊 Executive Summary

### **Current State**
- **Two Systems**: MongoDB backend (enterprise) + Supabase frontend (MVP)
- **Code Duplication**: Overlapping features, different implementations
- **Maintenance Burden**: Two databases, two auth systems, two codebases
- **Strategic Misalignment**: Legacy system targets wrong market/features

### **Target State**
- **Single System**: Supabase-based MVP only
- **Focused Scope**: 4 brain modules (MEMORY, ORACLE, CURIOSITY, FACE)
- **MVP Integrations**: Meta Ads, Google Ads, TikTok Ads, Shopify only
- **Clean Codebase**: Remove unused enterprise features

### **Impact**
- **Code Reduction**: ~60% reduction in backend codebase
- **Maintenance**: Single database, single auth system
- **Focus**: Align with validated MVP roadmap
- **Time Savings**: Faster development, clearer architecture

---

## 🎯 What the MVP Actually Needs

### **✅ Required for MVP (Keep)**

#### **Platform Integrations**
- ✅ **Meta Ads** - Primary ad platform
- ✅ **Google Ads** - Secondary ad platform
- ✅ **TikTok Ads** - Tertiary ad platform
- ✅ **Shopify** - For LTV/cohort data

#### **Brain Modules**
- ✅ **MEMORY** - Attribution & ROI truth layer
- ✅ **ORACLE** - Predictive risk detection
- ✅ **CURIOSITY** - Action recommendations
- ✅ **FACE** - Persona-specific UI

#### **Infrastructure**
- ✅ **Supabase (PostgreSQL)** - Primary database
- ✅ **NextAuth + Supabase Auth** - Authentication
- ✅ **Next.js** - Frontend framework
- ✅ **Vercel** - Deployment platform

#### **Features**
- ✅ Multi-tenant organizations
- ✅ Daily data sync (cron)
- ✅ Action execution (pause creative, shift budget)
- ✅ Brain cycle orchestration

---

## ❌ What Can Be Deprecated

### **🔴 Category 1: Not in MVP Roadmap (High Priority Deprecation)**

#### **1.1 AgentKit Integration** ❌ DEPRECATE
**Files to Deprecate**:
```
backend/services/agentkit_service.py
backend/services/real_agentkit_adapter.py
backend/services/agentkit_sdk_client*.py (all variants)
backend/api/agentkit_routes.py
backend/services/omnify_core_agents.py
backend/services/agentkit_agents/service.py
backend/database/mongodb_schema.py (agentkit_* collections)
```

**Rationale**:
- Not mentioned in MVP roadmap
- Not in Requirements V3
- Over-engineered for MVP validation
- Adds complexity without MVP value

**Impact**: ~15 files, ~200KB code

---

#### **1.2 GoHighLevel Integration** ❌ DEPRECATE
**Files to Deprecate**:
```
backend/integrations/gohighlevel/oauth2.py
backend/api/gohighlevel_oauth_routes.py
backend/services/*gohighlevel*.py (if any)
```

**Rationale**:
- Replaced by TripleWhale/HubSpot/Klaviyo in strategy
- Not in MVP roadmap (MVP focuses on ad platforms)
- Wrong market alignment (agency/SMB vs DTC brands)

**Impact**: ~3-5 files, ~50KB code

---

#### **1.3 MongoDB Backend Infrastructure** ❌ DEPRECATE
**Files to Deprecate**:
```
backend/database/mongodb_schema.py
backend/database/connection_manager.py
backend/database/production_mongodb_schema.py
backend/core/database_security.py
backend/core/database_transactions.py
backend/agentkit_server.py (MongoDB connection)
backend/agentkit_server_updated.py
```

**Rationale**:
- Supabase (PostgreSQL) is the new database
- No MongoDB usage in MVP
- Duplicate data layer maintenance

**Impact**: ~10 files, ~150KB code

---

#### **1.4 Advanced Brain Modules (Not in MVP)** ❌ DEPRECATE
**Files to Deprecate**:
```
backend/services/eyes_creative_service.py
backend/services/eyes_module.py
backend/api/eyes_routes.py
backend/services/voice_automation_service.py
backend/services/reflexes_performance_service.py
backend/api/brain_modules_routes.py (if references EYES/VOICE/REFLEXES)
```

**Rationale**:
- MVP only needs: MEMORY, ORACLE, CURIOSITY, FACE
- EYES, VOICE, REFLEXES are Phase 2 features
- Over-engineered for MVP validation

**Impact**: ~5-7 files, ~100KB code

---

#### **1.5 Complex Enterprise Features** ❌ DEPRECATE
**Files to Deprecate**:
```
backend/services/critical_decision_hand_holding_system.py
backend/services/human_expert_intervention_system.py
backend/services/adaptive_client_learning_system.py
backend/services/instant_value_delivery_system.py
backend/services/magical_onboarding_wizard.py
backend/api/critical_decision_routes.py
backend/api/expert_intervention_routes.py
backend/api/adaptive_learning_routes.py
backend/api/instant_value_routes.py
```

**Rationale**:
- "Magic features" not in MVP roadmap
- Over-engineered for MVP validation
- Can be added in Phase 2 if needed

**Impact**: ~10 files, ~200KB code

---

### **🟡 Category 2: Platform Integrations Not in MVP (Medium Priority)**

#### **2.1 Non-MVP Platform Integrations** ⚠️ DEPRECATE (Keep Code for Future)
**Files to Archive**:
```
backend/integrations/hubspot/oauth2.py
backend/api/hubspot_oauth_routes.py
backend/api/hubspot_routes.py
backend/integrations/triplewhale/oauth2.py
backend/api/triplewhale_oauth_routes.py
backend/api/triplewhale_routes.py
backend/integrations/klaviyo/oauth2.py
backend/api/klaviyo_routes.py
backend/integrations/stripe/oauth2.py
backend/api/stripe_oauth_routes.py
backend/integrations/linkedin_ads/oauth2.py
backend/api/linkedin_ads_oauth_routes.py
backend/integrations/youtube_ads/oauth2.py
backend/api/youtube_ads_oauth_routes.py
```

**Rationale**:
- MVP only needs: Meta, Google, TikTok, Shopify
- HubSpot/TripleWhale/Klaviyo are Phase 2
- LinkedIn/YouTube/Stripe not in MVP roadmap

**Action**: **Archive** (don't delete) - may need in Phase 2

**Impact**: ~15-20 files, ~300KB code

---

### **🟢 Category 3: Infrastructure Not Needed for MVP (Low Priority)**

#### **3.1 Advanced Infrastructure** ⚠️ DEPRECATE (Keep for Future)
**Files to Archive**:
```
backend/services/kafka_eventing.py
backend/api/kafka_routes.py
backend/services/temporal_orchestration.py
backend/api/temporal_routes.py
backend/services/kong_gateway.py
backend/api/kong_routes.py
backend/services/airbyte_etl.py
backend/api/airbyte_routes.py
backend/services/metabase_bi.py
backend/api/metabase_routes.py
backend/services/celery_app.py
backend/services/celery_tasks.py
```

**Rationale**:
- MVP uses Vercel Cron (not Celery)
- No Kafka/Temporal/Kong needed for MVP
- Airbyte/Metabase are Phase 2 features

**Action**: **Archive** (don't delete) - may need for scale

**Impact**: ~12 files, ~200KB code

---

#### **3.2 Advanced Security/Compliance** ⚠️ KEEP (But Not MVP Priority)
**Files to Keep** (but mark as Phase 2):
```
backend/services/advanced_security_service.py
backend/services/oidc_auth.py
backend/services/opa_policy_engine.py
backend/services/security_compliance_service.py
backend/api/advanced_security_routes.py
backend/api/security_compliance_routes.py
```

**Rationale**:
- MVP uses NextAuth + Supabase Auth (simpler)
- Advanced security needed for enterprise (Phase 2)
- Keep for future but not MVP focus

**Action**: **Keep but document as Phase 2**

---

## 📋 Deprecation Action Plan

### **Phase 1: Immediate Deprecation (Week 1)** 🔴

**Goal**: Remove code that's definitely not in MVP roadmap

#### **Step 1.1: Create Archive Directory**
```bash
mkdir -p _archive/backend-deprecated
mkdir -p _archive/backend-deprecated/services
mkdir -p _archive/backend-deprecated/api
mkdir -p _archive/backend-deprecated/integrations
mkdir -p _archive/backend-deprecated/database
```

#### **Step 1.2: Move AgentKit Files**
```bash
# Move AgentKit files to archive
mv backend/services/agentkit_service.py _archive/backend-deprecated/services/
mv backend/services/real_agentkit_adapter.py _archive/backend-deprecated/services/
mv backend/services/agentkit_sdk_client*.py _archive/backend-deprecated/services/
mv backend/api/agentkit_routes.py _archive/backend-deprecated/api/
mv backend/services/omnify_core_agents.py _archive/backend-deprecated/services/
mv backend/services/agentkit_agents/ _archive/backend-deprecated/services/
```

#### **Step 1.3: Move GoHighLevel Files**
```bash
mv backend/integrations/gohighlevel/ _archive/backend-deprecated/integrations/
mv backend/api/gohighlevel_oauth_routes.py _archive/backend-deprecated/api/
```

#### **Step 1.4: Move MongoDB Infrastructure**
```bash
mv backend/database/mongodb_schema.py _archive/backend-deprecated/database/
mv backend/database/connection_manager.py _archive/backend-deprecated/database/
mv backend/database/production_mongodb_schema.py _archive/backend-deprecated/database/
mv backend/core/database_security.py _archive/backend-deprecated/core/
mv backend/core/database_transactions.py _archive/backend-deprecated/core/
```

#### **Step 1.5: Move Non-MVP Brain Modules**
```bash
mv backend/services/eyes_creative_service.py _archive/backend-deprecated/services/
mv backend/services/eyes_module.py _archive/backend-deprecated/services/
mv backend/api/eyes_routes.py _archive/backend-deprecated/api/
mv backend/services/voice_automation_service.py _archive/backend-deprecated/services/
mv backend/services/reflexes_performance_service.py _archive/backend-deprecated/services/
```

#### **Step 1.6: Move Magic Features**
```bash
mv backend/services/critical_decision_hand_holding_system.py _archive/backend-deprecated/services/
mv backend/services/human_expert_intervention_system.py _archive/backend-deprecated/services/
mv backend/services/adaptive_client_learning_system.py _archive/backend-deprecated/services/
mv backend/services/instant_value_delivery_system.py _archive/backend-deprecated/services/
mv backend/services/magical_onboarding_wizard.py _archive/backend-deprecated/services/
mv backend/api/critical_decision_routes.py _archive/backend-deprecated/api/
mv backend/api/expert_intervention_routes.py _archive/backend-deprecated/api/
mv backend/api/adaptive_learning_routes.py _archive/backend-deprecated/api/
mv backend/api/instant_value_routes.py _archive/backend-deprecated/api/
```

#### **Step 1.7: Update Imports**
- Search for imports of deprecated modules
- Remove or comment out references
- Update `backend/agentkit_server.py` to remove MongoDB/AgentKit dependencies

---

### **Phase 2: Archive Non-MVP Integrations (Week 2)** 🟡

**Goal**: Archive platform integrations not in MVP (keep for Phase 2)

#### **Step 2.1: Archive HubSpot/TripleWhale/Klaviyo**
```bash
mkdir -p _archive/backend-phase2-integrations
mv backend/integrations/hubspot/ _archive/backend-phase2-integrations/
mv backend/integrations/triplewhale/ _archive/backend-phase2-integrations/
mv backend/integrations/klaviyo/ _archive/backend-phase2-integrations/
mv backend/api/hubspot_* _archive/backend-phase2-integrations/
mv backend/api/triplewhale_* _archive/backend-phase2-integrations/
mv backend/api/klaviyo_* _archive/backend-phase2-integrations/
```

#### **Step 2.2: Archive Other Platforms**
```bash
mv backend/integrations/stripe/ _archive/backend-phase2-integrations/
mv backend/integrations/linkedin_ads/ _archive/backend-phase2-integrations/
mv backend/integrations/youtube_ads/ _archive/backend-phase2-integrations/
mv backend/api/stripe_oauth_routes.py _archive/backend-phase2-integrations/
mv backend/api/linkedin_ads_oauth_routes.py _archive/backend-phase2-integrations/
mv backend/api/youtube_ads_oauth_routes.py _archive/backend-phase2-integrations/
```

---

### **Phase 3: Archive Infrastructure (Week 3)** 🟢

**Goal**: Archive advanced infrastructure not needed for MVP

#### **Step 3.1: Archive Event/Orchestration**
```bash
mkdir -p _archive/backend-phase2-infrastructure
mv backend/services/kafka_eventing.py _archive/backend-phase2-infrastructure/
mv backend/api/kafka_routes.py _archive/backend-phase2-infrastructure/
mv backend/services/temporal_orchestration.py _archive/backend-phase2-infrastructure/
mv backend/api/temporal_routes.py _archive/backend-phase2-infrastructure/
mv backend/services/celery_app.py _archive/backend-phase2-infrastructure/
mv backend/services/celery_tasks.py _archive/backend-phase2-infrastructure/
```

#### **Step 3.2: Archive BI/ETL**
```bash
mv backend/services/airbyte_etl.py _archive/backend-phase2-infrastructure/
mv backend/api/airbyte_routes.py _archive/backend-phase2-infrastructure/
mv backend/services/metabase_bi.py _archive/backend-phase2-infrastructure/
mv backend/api/metabase_routes.py _archive/backend-phase2-infrastructure/
mv backend/services/kong_gateway.py _archive/backend-phase2-infrastructure/
mv backend/api/kong_routes.py _archive/backend-phase2-infrastructure/
```

---

### **Phase 4: Documentation & Cleanup (Week 4)** 📝

#### **Step 4.1: Create Deprecation Documentation**
- Document what was deprecated and why
- Create migration guide for any data that needs moving
- Update architecture diagrams

#### **Step 4.2: Update README Files**
- Remove references to deprecated features
- Update architecture diagrams
- Clarify MVP vs Phase 2 features

#### **Step 4.3: Update Environment Variables**
- Remove MongoDB-related env vars from `.env.example`
- Remove AgentKit-related env vars
- Remove GoHighLevel env vars
- Keep only Supabase + MVP platform env vars

#### **Step 4.4: Update CI/CD**
- Remove MongoDB setup from CI/CD
- Remove AgentKit tests
- Focus on Supabase + MVP platform tests

---

## 📊 Impact Summary

### **Code Reduction**

| Category | Files | Estimated Size | Action |
|----------|-------|----------------|--------|
| **AgentKit** | ~15 | ~200KB | ❌ Delete |
| **GoHighLevel** | ~5 | ~50KB | ❌ Delete |
| **MongoDB Infrastructure** | ~10 | ~150KB | ❌ Delete |
| **Non-MVP Brain Modules** | ~7 | ~100KB | ❌ Delete |
| **Magic Features** | ~10 | ~200KB | ❌ Delete |
| **Non-MVP Integrations** | ~20 | ~300KB | 📦 Archive |
| **Advanced Infrastructure** | ~12 | ~200KB | 📦 Archive |
| **TOTAL** | **~79 files** | **~1.2MB** | |

### **Maintenance Reduction**
- **Single Database**: Supabase only (no MongoDB maintenance)
- **Single Auth**: NextAuth + Supabase Auth (no OIDC/OPA complexity)
- **Focused Scope**: 4 brain modules vs 7
- **Clear Roadmap**: MVP features only

---

## ⚠️ Risks & Mitigation

### **Risk 1: Breaking Existing Functionality**
**Mitigation**:
- Archive (don't delete) in Phase 2/3
- Keep archived code for 3 months
- Test MVP thoroughly before permanent deletion

### **Risk 2: Losing Useful Code**
**Mitigation**:
- Archive (don't delete) non-MVP integrations
- Document what's archived and why
- Can restore from archive if needed in Phase 2

### **Risk 3: Team Confusion**
**Mitigation**:
- Clear documentation of what's deprecated
- Update all README files
- Communicate changes to team

---

## ✅ Success Criteria

### **Phase 1 Complete When**:
- [ ] AgentKit files moved to archive
- [ ] GoHighLevel files moved to archive
- [ ] MongoDB infrastructure files moved to archive
- [ ] Non-MVP brain modules moved to archive
- [ ] Magic features moved to archive
- [ ] No import errors in remaining code
- [ ] MVP still works after deprecation

### **Phase 2 Complete When**:
- [ ] Non-MVP integrations archived
- [ ] Documentation updated
- [ ] Environment variables cleaned up

### **Phase 3 Complete When**:
- [ ] Advanced infrastructure archived
- [ ] CI/CD updated
- [ ] All documentation reflects MVP focus

---

## 📚 Related Documentation

- **MVP Roadmap**: `UNIFIED_GAP_ANALYSIS_AND_STRATEGIC_ROADMAP.md`
- **Implementation Summary**: `omnify-brain/docs/IMPLEMENTATION_SUMMARY.md`
- **Database Architecture**: `docs/DATABASE_ARCHITECTURE_EXPLAINED.md`
- **GoHighLevel Replacement**: `docs/GOHIGHLEVEL_REPLACEMENT_ANALYSIS.md`

---

**Last Updated**: January 2025  
**Status**: Ready for Execution  
**Priority**: 🔴 CRITICAL - Start Phase 1 immediately

