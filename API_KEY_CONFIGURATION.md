# API Key Configuration Guide

## 🔑 Overview

OmniFy Cloud Connect requires API keys for various platforms to function. This guide explains how to obtain and configure each API key securely.

## 🏗️ Architecture

### Storage & Encryption
- **Encryption**: Fernet symmetric encryption (AES-128)
- **Storage**: Supabase PostgreSQL with row-level security
- **Access**: Backend services only (never exposed to frontend)
- **Multi-Tenancy**: Organization-based isolation

### Configuration Methods
1. **UI Configuration** (Recommended): `/settings/api-keys`
2. **API Configuration**: Direct API calls
3. **Database Direct**: Manual SQL inserts (not recommended)

---

## 🤖 AI / LLM Provider Keys

### 1. OpenAI

**What it's used for:**
- AI recommendations
- Creative analysis (AIDA framework)
- Chat-based insights
- GPT-4o, GPT-4o-mini models

**How to obtain:**

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Click on your profile (top right) → "API keys"
4. Click "Create new secret key"
5. Name it: "OmniFy Cloud Connect"
6. Copy the key (starts with `sk-`)
7. **Important**: Save it immediately - you won't see it again!

**Configuration:**
```bash
# Via UI
1. Navigate to http://localhost:3000/settings/api-keys
2. Find "OpenAI" card
3. Paste API key in "API Key" field
4. Click "Save"
5. Click "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openai",
    "key_name": "api_key",
    "key_value": "sk-..."
  }'
```

**Pricing:**
- Pay-as-you-go
- GPT-4o-mini: ~$0.15 per 1M input tokens
- GPT-4o: ~$5 per 1M input tokens
- Start with $5-10 credit

---

### 2. Anthropic Claude

**What it's used for:**
- Alternative AI provider
- Advanced reasoning tasks
- Creative analysis
- Claude-3.5-Sonnet, Claude-3-Haiku models

**How to obtain:**

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Name it: "OmniFy Cloud Connect"
6. Copy the key (starts with `sk-ant-`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Anthropic Claude" card
3. Paste API key
4. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "anthropic",
    "key_name": "api_key",
    "key_value": "sk-ant-..."
  }'
```

**Pricing:**
- Pay-as-you-go
- Claude-3.5-Sonnet: ~$3 per 1M input tokens
- Claude-3-Haiku: ~$0.25 per 1M input tokens

---

### 3. Google Gemini

**What it's used for:**
- Multi-modal AI analysis
- Text and image understanding
- Fast responses with Gemini-Pro

**How to obtain:**

1. Go to https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Select or create a Google Cloud project
4. Click "Create API key in existing project"
5. Copy the key (starts with `AIza`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Google Gemini" card
3. Paste API key
4. (Optional) Add Project ID
5. Click "Save" and "Test Connection"

# Via API - API Key
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "gemini",
    "key_name": "api_key",
    "key_value": "AIza..."
  }'

# Via API - Project ID (optional)
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "gemini",
    "key_name": "project_id",
    "key_value": "your-project-id"
  }'
```

**Pricing:**
- Free tier: 60 requests/minute
- Paid: ~$0.35 per 1M input tokens (Gemini-Pro)

---

### 4. Grok (X.AI)

**What it's used for:**
- Real-time AI with X (Twitter) data access
- Alternative AI provider
- Grok-beta model

**How to obtain:**

1. Go to https://x.ai/
2. Sign up for API access (currently limited availability)
3. Once approved, navigate to API keys section
4. Generate new key
5. Copy the key (starts with `xai-`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Grok (X.AI)" card
3. Paste API key
4. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "grok",
    "key_name": "api_key",
    "key_value": "xai-..."
  }'
```

**Pricing:**
- TBD (limited availability)

---

### 5. OpenRouter

**What it's used for:**
- Unified access to multiple LLMs
- Fallback provider
- Access to OpenAI, Anthropic, Google models through one API

**How to obtain:**

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Navigate to "Keys" page
4. Click "Create Key"
5. Name it: "OmniFy Cloud Connect"
6. Copy the key (starts with `sk-or-`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "OpenRouter" card
3. Paste API key
4. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openrouter",
    "key_name": "api_key",
    "key_value": "sk-or-..."
  }'
```

**Pricing:**
- Varies by model used
- Typically 10-20% markup over direct provider pricing

---

## 📊 Marketing Platform Keys

### 6. Meta Ads (Facebook/Instagram)

**What it's used for:**
- Campaign performance data
- Ad creative insights
- Spend and ROAS tracking

**How to obtain:**

1. Go to https://developers.facebook.com/tools/explorer/
2. Select your ad account in the dropdown
3. Click "Generate Access Token"
4. Grant permissions:
   - `ads_read`
   - `ads_management`
   - `business_management`
5. Copy the access token (starts with `EAA`)
6. Get your Ad Account ID:
   - Go to https://business.facebook.com/
   - Navigate to "Ad Accounts"
   - Copy the ID (format: `act_123456789`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Meta Ads" card
3. Paste Access Token
4. Paste Ad Account ID (with 'act_' prefix)
5. Click "Save" and "Test Connection"

# Via API - Access Token
curl -X POST http://localhost:8001/api-keys/save-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "meta_ads",
    "keys": {
      "access_token": "EAA...",
      "account_id": "act_123456789"
    }
  }'
```

**Important Notes:**
- Access tokens expire (60 days default)
- Use "Exchange Token" to get long-lived token
- Store refresh token for automated renewal

**Pricing:**
- Free to use Meta Ads API
- Costs are your ad spend

---

### 7. Google Ads

**What it's used for:**
- Campaign performance data
- Keyword insights
- Spend and conversion tracking

**How to obtain:**

**Step 1: Enable Google Ads API**
1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable "Google Ads API"
4. Navigate to "Credentials"

**Step 2: Create OAuth2 Credentials**
1. Click "Create Credentials" → "OAuth client ID"
2. Application type: "Web application"
3. Add authorized redirect URIs:
   - `http://localhost:8001/auth/google/callback`
   - Your production URL
4. Copy Client ID and Client Secret

**Step 3: Get Refresh Token**
```bash
# Use OAuth2 flow to get refresh token
# Or use Google's OAuth Playground: https://developers.google.com/oauthplayground/

1. Go to OAuth Playground
2. Select "Google Ads API v14"
3. Authorize and get refresh token
```

**Step 4: Get Developer Token**
1. Go to https://ads.google.com/
2. Navigate to "Tools & Settings" → "API Center"
3. Apply for developer token
4. Wait for approval (can take 1-2 days)

**Step 5: Get Customer ID**
1. In Google Ads, look at top right
2. Copy the customer ID (format: `123-456-7890`)

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Google Ads" card
3. Fill in all 5 fields:
   - Client ID
   - Client Secret
   - Refresh Token
   - Customer ID
   - Developer Token
4. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "google_ads",
    "keys": {
      "client_id": "...",
      "client_secret": "...",
      "refresh_token": "...",
      "customer_id": "123-456-7890",
      "developer_token": "..."
    }
  }'
```

**Pricing:**
- Free to use Google Ads API
- Costs are your ad spend

---

### 8. TikTok Ads

**What it's used for:**
- TikTok campaign performance
- Ad creative insights
- Audience data

**How to obtain:**

1. Go to https://ads.tiktok.com/marketing_api/docs
2. Apply for API access
3. Create an app in TikTok for Business
4. Get Access Token and Advertiser ID

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "TikTok Ads" card
3. Paste Access Token and Advertiser ID
4. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "tiktok",
    "keys": {
      "access_token": "...",
      "advertiser_id": "..."
    }
  }'
```

---

### 9. Shopify

**What it's used for:**
- E-commerce sales data
- Order tracking
- Customer data

**How to obtain:**

1. Log into your Shopify admin
2. Go to "Apps" → "Develop apps"
3. Click "Create an app"
4. Name it: "OmniFy Cloud Connect"
5. Configure API scopes:
   - `read_orders`
   - `read_customers`
   - `read_products`
6. Install the app
7. Get Access Token

**Configuration:**
```bash
# Via UI
1. Go to /settings/api-keys
2. Find "Shopify" card
3. Enter Shop URL (format: yourstore.myshopify.com)
4. Paste Access Token
5. Click "Save" and "Test Connection"

# Via API
curl -X POST http://localhost:8001/api-keys/save-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "shopify",
    "keys": {
      "shop_url": "yourstore.myshopify.com",
      "access_token": "shpat_..."
    }
  }'
```

---

## ✅ Testing Connections

### Via UI
1. After saving keys, click "Test Connection" button
2. Wait for response (5-10 seconds)
3. See result:
   - ✅ Green: Connection successful
   - ❌ Red: Connection failed (check error message)

### Via API
```bash
# Test any platform
curl -X POST http://localhost:8001/api-keys/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openai"
  }'

# Response for success:
{
  "success": true,
  "connected": true,
  "message": "OpenAI connection successful",
  "details": {"models_available": 10}
}

# Response for failure:
{
  "success": false,
  "connected": false,
  "error": "Invalid API key",
  "message": "OpenAI connection failed"
}
```

---

## 🔒 Security Best Practices

### 1. Key Rotation
```bash
# Rotate keys every 90 days
# Steps:
1. Generate new key from provider
2. Update in OmniFy settings
3. Test connection
4. Delete old key from provider
```

### 2. Access Control
- Limit API key permissions to minimum required
- Use separate keys for dev/staging/production
- Never commit keys to version control

### 3. Monitoring
```bash
# Check key usage
curl http://localhost:8001/api-keys/list/default-org-id

# Response shows last_used_at for each key
```

### 4. Backup
```sql
-- Backup encrypted keys (database only)
SELECT platform, key_name, updated_at 
FROM api_keys 
WHERE organization_id = 'your-org-id';

-- Do NOT backup decrypted keys
```

---

## 🔧 Troubleshooting

### "Connection failed" Error

**OpenAI:**
- Verify key format: `sk-...`
- Check billing: https://platform.openai.com/account/billing
- Verify key is not revoked

**Meta Ads:**
- Token expired? Generate new long-lived token
- Account ID format: `act_123456789`
- Check permissions: need `ads_read` scope

**Google Ads:**
- Developer token approved?
- Refresh token valid?
- Customer ID format: `123-456-7890`

### "Key not found" Error
- Verify organization ID is correct
- Check platform name spelling (use lowercase)
- Ensure key was saved successfully

### "Encryption error"
- Verify ENCRYPTION_KEY in backend .env
- Key should be 44 characters (Fernet key)
- Regenerate if corrupted

---

## 📄 API Key Summary Table

| Platform | Required Fields | Where to Get | Cost | Priority |
|----------|----------------|--------------|------|----------|
| OpenAI | api_key | platform.openai.com | Pay-as-you-go | HIGH |
| Anthropic | api_key | console.anthropic.com | Pay-as-you-go | MEDIUM |
| Gemini | api_key, project_id | makersuite.google.com | Free tier | MEDIUM |
| Grok | api_key | x.ai | TBD | LOW |
| OpenRouter | api_key | openrouter.ai | Pay-as-you-go | LOW |
| Meta Ads | access_token, account_id | developers.facebook.com | Free | HIGH |
| Google Ads | client_id, secret, token, customer_id, dev_token | ads.google.com | Free | HIGH |
| TikTok | access_token, advertiser_id | ads.tiktok.com | Free | MEDIUM |
| Shopify | shop_url, access_token | yourstore/admin | Free | MEDIUM |

---

**Last Updated**: January 2025
