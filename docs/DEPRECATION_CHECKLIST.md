# Deprecation Execution Checklist

**Quick Reference** for executing the deprecation plan.

---

## ✅ Phase 1: Immediate Deprecation (Week 1)

### AgentKit Files
- [ ] `backend/services/agentkit_service.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/real_agentkit_adapter.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/agentkit_sdk_client*.py` (all) → `_archive/backend-deprecated/services/`
- [ ] `backend/api/agentkit_routes.py` → `_archive/backend-deprecated/api/`
- [ ] `backend/services/omnify_core_agents.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/agentkit_agents/` (entire dir) → `_archive/backend-deprecated/services/`

### GoHighLevel Files
- [ ] `backend/integrations/gohighlevel/` → `_archive/backend-deprecated/integrations/`
- [ ] `backend/api/gohighlevel_oauth_routes.py` → `_archive/backend-deprecated/api/`

### MongoDB Infrastructure
- [ ] `backend/database/mongodb_schema.py` → `_archive/backend-deprecated/database/`
- [ ] `backend/database/connection_manager.py` → `_archive/backend-deprecated/database/`
- [ ] `backend/database/production_mongodb_schema.py` → `_archive/backend-deprecated/database/`
- [ ] `backend/core/database_security.py` → `_archive/backend-deprecated/core/`
- [ ] `backend/core/database_transactions.py` → `_archive/backend-deprecated/core/`

### Non-MVP Brain Modules
- [ ] `backend/services/eyes_creative_service.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/eyes_module.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/api/eyes_routes.py` → `_archive/backend-deprecated/api/`
- [ ] `backend/services/voice_automation_service.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/reflexes_performance_service.py` → `_archive/backend-deprecated/services/`

### Magic Features
- [ ] `backend/services/critical_decision_hand_holding_system.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/human_expert_intervention_system.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/adaptive_client_learning_system.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/instant_value_delivery_system.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/services/magical_onboarding_wizard.py` → `_archive/backend-deprecated/services/`
- [ ] `backend/api/critical_decision_routes.py` → `_archive/backend-deprecated/api/`
- [ ] `backend/api/expert_intervention_routes.py` → `_archive/backend-deprecated/api/`
- [ ] `backend/api/adaptive_learning_routes.py` → `_archive/backend-deprecated/api/`
- [ ] `backend/api/instant_value_routes.py` → `_archive/backend-deprecated/api/`

### After Moving Files
- [ ] Search codebase for imports of moved files
- [ ] Remove/comment out broken imports
- [ ] Update `backend/agentkit_server.py` (remove MongoDB/AgentKit deps)
- [ ] Test that MVP still works
- [ ] Commit changes with message: "Deprecate: Phase 1 - AgentKit, GoHighLevel, MongoDB, Non-MVP modules"

---

## 📦 Phase 2: Archive Non-MVP Integrations (Week 2)

### HubSpot/TripleWhale/Klaviyo
- [ ] `backend/integrations/hubspot/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/hubspot_*` → `_archive/backend-phase2-integrations/`
- [ ] `backend/integrations/triplewhale/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/triplewhale_*` → `_archive/backend-phase2-integrations/`
- [ ] `backend/integrations/klaviyo/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/klaviyo_*` → `_archive/backend-phase2-integrations/`

### Other Platforms
- [ ] `backend/integrations/stripe/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/stripe_oauth_routes.py` → `_archive/backend-phase2-integrations/`
- [ ] `backend/integrations/linkedin_ads/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/linkedin_ads_oauth_routes.py` → `_archive/backend-phase2-integrations/`
- [ ] `backend/integrations/youtube_ads/` → `_archive/backend-phase2-integrations/`
- [ ] `backend/api/youtube_ads_oauth_routes.py` → `_archive/backend-phase2-integrations/`

### After Moving Files
- [ ] Update documentation to note these are Phase 2 features
- [ ] Commit changes: "Archive: Phase 2 - Non-MVP platform integrations"

---

## 📦 Phase 3: Archive Infrastructure (Week 3)

### Event/Orchestration
- [ ] `backend/services/kafka_eventing.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/api/kafka_routes.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/services/temporal_orchestration.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/api/temporal_routes.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/services/celery_app.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/services/celery_tasks.py` → `_archive/backend-phase2-infrastructure/`

### BI/ETL
- [ ] `backend/services/airbyte_etl.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/api/airbyte_routes.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/services/metabase_bi.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/api/metabase_routes.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/services/kong_gateway.py` → `_archive/backend-phase2-infrastructure/`
- [ ] `backend/api/kong_routes.py` → `_archive/backend-phase2-infrastructure/`

### After Moving Files
- [ ] Update documentation
- [ ] Commit changes: "Archive: Phase 3 - Advanced infrastructure"

---

## 📝 Phase 4: Documentation & Cleanup (Week 4)

### Documentation
- [ ] Update `README.md` to reflect MVP focus
- [ ] Update architecture diagrams
- [ ] Create migration guide (if needed)
- [ ] Document what was deprecated and why

### Environment Variables
- [ ] Remove MongoDB vars from `.env.example`
- [ ] Remove AgentKit vars from `.env.example`
- [ ] Remove GoHighLevel vars from `.env.example`
- [ ] Keep only Supabase + MVP platform vars

### CI/CD
- [ ] Remove MongoDB setup from CI/CD
- [ ] Remove AgentKit tests
- [ ] Focus on Supabase + MVP platform tests

### Final
- [ ] Review all changes
- [ ] Test MVP end-to-end
- [ ] Commit final documentation updates
- [ ] Tag release: `v1.0.0-mvp-focused`

---

## 🎯 Quick Commands

### Create Archive Directories
```bash
mkdir -p _archive/backend-deprecated/{services,api,integrations,database,core}
mkdir -p _archive/backend-phase2-integrations
mkdir -p _archive/backend-phase2-infrastructure
```

### Find All Imports (Before Moving)
```bash
# Find AgentKit imports
grep -r "agentkit" backend/ --include="*.py" | grep -i import

# Find MongoDB imports
grep -r "mongodb\|motor\|AsyncIOMotor" backend/ --include="*.py" | grep -i import

# Find GoHighLevel imports
grep -r "gohighlevel" backend/ --include="*.py" | grep -i import
```

### Test After Deprecation
```bash
# Test MVP frontend
cd omnify-brain
npm run build
npm run dev

# Check for import errors
cd backend
python -m py_compile **/*.py 2>&1 | grep -i "error\|import"
```

---

**Status**: Ready to Execute  
**Priority**: 🔴 CRITICAL - Start Phase 1 immediately

