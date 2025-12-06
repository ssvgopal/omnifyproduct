# Testing Guide - OmniFy Cloud Connect

## 🎯 Overview

This guide covers testing strategies, test execution, and validation procedures for OmniFy Cloud Connect.

## 📊 Testing Levels

### 1. Unit Testing
### 2. Integration Testing
### 3. End-to-End Testing
### 4. Performance Testing
### 5. Security Testing

---

## 🧑‍💻 Manual Testing

### Pre-Test Setup

```bash
# Start backend
cd /app/backend
python server.py

# Start frontend (in another terminal)
cd /app/omnify-brain
yarn dev

# Verify both running
curl http://localhost:8001/api/health
curl http://localhost:3000
```

---

## ✅ Test Cases

### Phase 1: API Key Management

#### TC-001: Save API Key via UI
**Priority**: High  
**Prerequisites**: Backend and frontend running

**Steps:**
1. Navigate to http://localhost:3000/settings/api-keys
2. Click on "AI / LLM Services" tab
3. Find "OpenAI" card
4. Enter API key: `sk-test123456789` (test key)
5. Click "Save" button
6. Observe loading spinner
7. Wait for success message

**Expected Result:**
- ✅ Success message appears
- ✅ "Configured" badge shows on card
- ✅ Test Connection button enabled

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-002: Test API Connection
**Priority**: High  
**Prerequisites**: TC-001 passed

**Steps:**
1. On OpenAI card, click "Test Connection" button
2. Observe loading spinner
3. Wait for response (5-10 seconds)

**Expected Result:**
- ✅ Green success banner appears
- ✅ Message: "OpenAI connection successful"
- ✅ Details show available models

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-003: List Configured Platforms via API
**Priority**: Medium

**Steps:**
```bash
curl -X GET "http://localhost:8001/api-keys/list/default-org-id"
```

**Expected Result:**
```json
{
  "organization_id": "default-org-id",
  "platforms": [
    {
      "platform": "openai",
      "keys": ["api_key"],
      "is_active": true,
      "updated_at": "2025-01-..."
    }
  ],
  "total": 1
}
```

**Status**: ☐ Pass / ☐ Fail

---

### Phase 2: Platform Integrations

#### TC-004: Fetch Meta Ads Summary
**Priority**: High  
**Prerequisites**: Meta Ads API keys configured

**Steps:**
```bash
curl -X POST "http://localhost:8001/platforms/meta-ads/summary" \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'
```

**Expected Result:**
```json
{
  "success": true,
  "platform": "meta_ads",
  "period": "30 days",
  "metrics": {
    "spend": 12450.50,
    "revenue": 49800.00,
    "roas": 4.0,
    "impressions": 1250000,
    "clicks": 31250,
    "conversions": 150,
    "ctr": 2.5,
    "cpc": 0.40,
    "cpm": 9.96
  }
}
```

**Status**: ☐ Pass / ☐ Fail

---

#### TC-005: Fetch Google Ads Campaigns
**Priority**: High  
**Prerequisites**: Google Ads API keys configured

**Steps:**
```bash
curl -X POST "http://localhost:8001/platforms/google-ads/campaigns" \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'
```

**Expected Result:**
```json
{
  "success": true,
  "campaigns": [
    {
      "id": "123456789",
      "name": "Summer Sale 2025",
      "status": "ENABLED",
      "type": "SEARCH",
      "bidding_strategy": "MAXIMIZE_CONVERSIONS"
    }
  ],
  "count": 1
}
```

**Status**: ☐ Pass / ☐ Fail

---

#### TC-006: Sync All Platforms
**Priority**: High  
**Prerequisites**: At least one platform configured

**Steps:**
```bash
curl -X POST "http://localhost:8001/platforms/sync/all" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "days": 7
  }'
```

**Expected Result:**
```json
{
  "success": true,
  "organization_id": "default-org-id",
  "platforms_synced": 2,
  "total_records": 14,
  "results": {
    "meta_ads": {"synced": 7, "errors": []},
    "google_ads": {"synced": 7, "errors": []}
  }
}
```

**Status**: ☐ Pass / ☐ Fail

---

#### TC-007: Get Unified Metrics
**Priority**: High  
**Prerequisites**: TC-006 passed (data synced)

**Steps:**
```bash
curl -X POST "http://localhost:8001/platforms/unified-metrics" \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'
```

**Expected Result:**
```json
{
  "success": true,
  "blended_metrics": {
    "spend": 25000.00,
    "revenue": 100000.00,
    "roas": 4.0,
    "impressions": 2500000,
    "clicks": 62500,
    "conversions": 300,
    "ctr": 2.5,
    "cpc": 0.40
  },
  "platform_breakdown": {
    "meta_ads": {...},
    "google_ads": {...}
  }
}
```

**Status**: ☐ Pass / ☐ Fail

---

### Phase 3: AI Services

#### TC-008: AI Chat Completion
**Priority**: High  
**Prerequisites**: OpenAI API key configured

**Steps:**
```bash
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "messages": [
      {"role": "user", "content": "What is ROAS?"}
    ],
    "provider": "openai"
  }'
```

**Expected Result:**
```json
{
  "success": true,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "content": "ROAS stands for Return on Ad Spend...",
  "usage": {"prompt_tokens": 10, "completion_tokens": 50}
}
```

**Status**: ☐ Pass / ☐ Fail

---

#### TC-009: Creative Analysis
**Priority**: High  
**Prerequisites**: AI provider configured

**Steps:**
```bash
curl -X POST "http://localhost:8001/ai/analyze-creative" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "creative_text": "Get 50% off today! Limited time offer. Shop now and save big!",
    "provider": "openai"
  }'
```

**Expected Result:**
```json
{
  "success": true,
  "analysis": {
    "attention": 85,
    "interest": 75,
    "desire": 80,
    "action": 90,
    "overall_score": 82.5,
    "strengths": ["Clear discount", "Urgency created"],
    "weaknesses": ["Generic messaging"],
    "recommendations": ["Add specific product benefits"]
  },
  "provider": "openai"
}
```

**Status**: ☐ Pass / ☐ Fail

---

#### TC-010: Generate Recommendations
**Priority**: High  
**Prerequisites**: Performance data available

**Steps:**
```bash
curl -X POST "http://localhost:8001/ai/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "performance_data": {
      "spend": 10000,
      "revenue": 40000,
      "roas": 4.0,
      "ctr": 2.5
    },
    "provider": "openai"
  }'
```

**Expected Result:**
```json
{
  "success": true,
  "recommendations": [
    {
      "title": "Scale winning campaigns",
      "description": "Increase budget by 20% on campaigns with ROAS > 3.5",
      "impact": "high",
      "effort": "low",
      "category": "budget"
    }
  ],
  "provider": "openai"
}
```

**Status**: ☐ Pass / ☐ Fail

---

### Phase 4: Frontend E2E

#### TC-011: Dashboard Load
**Priority**: High

**Steps:**
1. Navigate to http://localhost:3000/dashboard
2. Wait for page to load completely
3. Observe all three brain modules

**Expected Result:**
- ✅ Memory card shows real metrics (not $0)
- ✅ Oracle card shows risk score
- ✅ Curiosity card shows recommendations
- ✅ Loading completes in < 5 seconds
- ✅ No error messages

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-012: Sync Data Button
**Priority**: High  
**Prerequisites**: TC-011 passed

**Steps:**
1. On dashboard, click "Sync Data" button
2. Observe button state change to "Syncing..."
3. Wait for completion (10-30 seconds)
4. Observe metrics update

**Expected Result:**
- ✅ Button shows loading spinner
- ✅ Button text: "Syncing..."
- ✅ After completion, metrics refresh
- ✅ Success indication (no errors)

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-013: Navigate to Campaigns
**Priority**: Medium

**Steps:**
1. On dashboard, click "Campaigns" quick action card
2. Wait for campaigns page to load
3. Observe campaign list

**Expected Result:**
- ✅ Redirects to /campaigns
- ✅ Campaign list displayed
- ✅ Shows campaigns from all platforms
- ✅ Search bar functional
- ✅ Platform filter works

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-014: Campaign Search & Filter
**Priority**: Medium  
**Prerequisites**: TC-013 passed

**Steps:**
1. In search bar, type a campaign name
2. Observe filtered results
3. Clear search
4. Select platform filter (e.g., "Meta Ads")
5. Observe filtered results

**Expected Result:**
- ✅ Search filters campaigns correctly
- ✅ Platform filter shows only selected platform
- ✅ "Showing X campaigns" count updates
- ✅ No campaigns shows helpful message

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

### Phase 5: Error Handling

#### TC-015: Invalid API Key
**Priority**: High

**Steps:**
1. Go to settings/api-keys
2. Enter invalid OpenAI key: `sk-invalid123`
3. Click "Save"
4. Click "Test Connection"

**Expected Result:**
- ✅ Save succeeds (encryption works)
- ✅ Test fails with error message
- ✅ Red error banner shows
- ✅ Message: "OpenAI connection failed"

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

#### TC-016: Backend Offline
**Priority**: High

**Steps:**
1. Stop backend server
2. Try to load dashboard
3. Observe error handling

**Expected Result:**
- ✅ Error message displays
- ✅ User-friendly message (not technical error)
- ✅ Retry button available
- ✅ No app crash

**Actual Result**: _____________

**Status**: ☐ Pass / ☐ Fail

---

## 🧑‍💻 Automated Testing

### Backend Unit Tests

```bash
cd /app/backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api_key_service.py -v

# Run with coverage
pytest tests/ --cov=services --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Frontend Component Tests

```bash
cd /app/omnify-brain

# Run Jest tests
yarn test

# Run with coverage
yarn test --coverage

# Run specific test
yarn test Dashboard
```

---

## 🚀 Performance Testing

### Load Testing with Apache Bench

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8001/api/health

# Expected:
# - Requests per second: > 500
# - 99th percentile: < 100ms
# - No failed requests

# Test API key endpoint
ab -n 100 -c 5 -p test_payload.json -T application/json \
  http://localhost:8001/api-keys/list/default-org-id
```

### Frontend Performance

```bash
# Using Lighthouse
npx lighthouse http://localhost:3000/dashboard --view

# Target scores:
# - Performance: > 90
# - Accessibility: > 95
# - Best Practices: > 90
# - SEO: > 90
```

---

## 🔒 Security Testing

### SQL Injection Test

```bash
# Try to inject SQL in API
curl -X POST "http://localhost:8001/api-keys/list/'; DROP TABLE api_keys; --" \
  -H "Content-Type: application/json"

# Expected: 404 or validation error (not SQL error)
```

### XSS Test

```bash
# Try to inject script
curl -X POST "http://localhost:8001/api-keys/save" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "<script>alert(1)</script>",
    "platform": "test",
    "key_name": "test",
    "key_value": "test"
  }'

# Expected: Input sanitized, no script execution
```

### Encryption Verification

```sql
-- Connect to Supabase and query
SELECT key_value_encrypted FROM api_keys LIMIT 1;

-- Expected: Encrypted string (not plaintext)
-- Format: gAAAAABl... (Fernet encrypted)
```

---

## 📋 Test Report Template

```markdown
# Test Execution Report

**Date**: _____________  
**Tester**: _____________  
**Environment**: Development / Staging / Production  
**Build Version**: _____________

## Summary

| Category | Total | Passed | Failed | Blocked | Pass Rate |
|----------|-------|--------|--------|---------|----------|
| API Keys | 3 | __ | __ | __ | __% |
| Platforms | 4 | __ | __ | __ | __% |
| AI Services | 3 | __ | __ | __ | __% |
| Frontend | 4 | __ | __ | __ | __% |
| Error Handling | 2 | __ | __ | __ | __% |
| **Total** | **16** | __ | __ | __ | __% |

## Failed Tests

| Test ID | Test Name | Error | Priority |
|---------|-----------|-------|----------|
| TC-XXX | ... | ... | High |

## Issues Found

1. **Issue #1**: Description
   - Severity: High / Medium / Low
   - Steps to reproduce: ...
   - Expected: ...
   - Actual: ...

## Recommendations

- ...

## Sign-off

- [ ] All critical tests passed
- [ ] All high priority issues resolved
- [ ] Ready for deployment

**Tester Signature**: _____________  
**Date**: _____________
```

---

## 🔧 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd omnify-brain
          yarn install
      - name: Run tests
        run: |
          cd omnify-brain
          yarn test
```

---

**Last Updated**: January 2025
