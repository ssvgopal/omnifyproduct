# Environment Setup Guide

**Last Updated**: November 21, 2025  
**Purpose**: Step-by-step guide for setting up environment variables for Omnify Cloud Connect

---

## Quick Start

1. **Copy environment template files**:
   ```bash
   # Backend
   cp .env.production.example backend/.env
   
   # Frontend
   cp frontend/.env.production.example frontend/.env.production
   ```

2. **Edit the files** and fill in your values (see sections below)

3. **Validate configuration** (backend will validate on startup)

---

## Backend Environment Variables

### Core Configuration (REQUIRED)

#### `MONGO_URL`
- **Description**: MongoDB connection string
- **How to get**: 
  1. Sign up at https://www.mongodb.com/cloud/atlas
  2. Create a cluster
  3. Click "Connect" → "Connect your application"
  4. Copy the connection string
- **Example**: `mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority`
- **Required**: ✅ Yes

#### `DB_NAME`
- **Description**: Database name
- **Default**: `omnify_cloud`
- **Required**: ✅ Yes

#### `JWT_SECRET_KEY`
- **Description**: Secret key for JWT token signing
- **How to generate**: 
  ```bash
  openssl rand -base64 32
  ```
- **Required**: ✅ Yes
- **Security**: Must be unique and secret

#### `OPENAI_API_KEY`
- **Description**: OpenAI API key for AgentKit
- **How to get**: 
  1. Sign up at https://platform.openai.com/
  2. Go to API Keys section
  3. Create new secret key
- **Format**: `sk-...`
- **Required**: ✅ Yes

---

### Important Configuration (SHOULD HAVE)

#### `CORS_ORIGINS`
- **Description**: Allowed frontend origins (comma-separated)
- **Example**: `https://app.omnify.ai,https://omnify.ai`
- **Required**: ⚠️ Important for production

#### `SENTRY_DSN`
- **Description**: Sentry error tracking DSN
- **How to get**: 
  1. Sign up at https://sentry.io/
  2. Create a project
  3. Copy DSN from project settings
- **Format**: `https://...@sentry.io/...`
- **Required**: ⚠️ Recommended for production

#### `SENDGRID_API_KEY`
- **Description**: SendGrid API key for email
- **How to get**: 
  1. Sign up at https://sendgrid.com/
  2. Go to Settings → API Keys
  3. Create API key with "Mail Send" permissions
- **Format**: `SG....`
- **Required**: ⚠️ Required for email verification

---

### Platform Integrations (OPTIONAL)

#### Google Ads
1. **Get Developer Token**:
   - Apply at https://ads.google.com/nav/selectaccount
   - Go to Tools & Settings → API Center
   - Request developer token (may take 24-48 hours)

2. **Create OAuth2 Credentials**:
   - Go to Google Cloud Console
   - Create OAuth2 client ID
   - Add authorized redirect URI: `https://api.omnify.ai/api/integrations/google-ads/oauth/callback`

3. **Set Variables**:
   ```bash
   GOOGLE_ADS_DEVELOPER_TOKEN=...
   GOOGLE_ADS_CLIENT_ID=...
   GOOGLE_ADS_CLIENT_SECRET=...
   ```

#### Meta Ads (Facebook/Instagram)
1. **Create App**:
   - Go to https://developers.facebook.com/
   - Create new app
   - Add "Marketing API" product

2. **Get Credentials**:
   - App ID and App Secret from app settings
   - Generate access token with required permissions

3. **Set Variables**:
   ```bash
   META_APP_ID=...
   META_APP_SECRET=...
   META_ACCESS_TOKEN=...
   ```

#### TripleWhale
1. **Get API Key**:
   - Log in to TripleWhale dashboard
   - Go to Settings → API
   - Generate API key

2. **Set Variables**:
   ```bash
   TRIPLEWHALE_API_KEY=...
   TRIPLEWHALE_SHOP_ID=...
   ```

#### HubSpot
1. **Get API Key**:
   - Log in to HubSpot
   - Go to Settings → Integrations → Private Apps
   - Create private app with required scopes
   - Copy API key

2. **Set Variables**:
   ```bash
   HUBSPOT_API_KEY=...
   ```

#### Klaviyo
1. **Get API Key**:
   - Log in to Klaviyo
   - Go to Account → Settings → API Keys
   - Create API key

2. **Set Variables**:
   ```bash
   KLAVIYO_API_KEY=...
   KLAVIYO_ACCOUNT_ID=...
   ```

---

### Payment & Billing (Week 3+)

#### Stripe
1. **Create Account**:
   - Sign up at https://stripe.com/
   - Complete account setup

2. **Get API Keys**:
   - Go to Developers → API Keys
   - Copy Secret Key and Publishable Key
   - Use test keys for development, live keys for production

3. **Set Up Webhook**:
   - Go to Developers → Webhooks
   - Add endpoint: `https://api.omnify.ai/api/stripe/webhook`
   - Copy webhook secret

4. **Set Variables**:
   ```bash
   STRIPE_SECRET_KEY=sk_live_...  # or sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...  # or pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

---

### Storage Configuration

#### AWS S3
1. **Create S3 Bucket**:
   - Go to AWS Console → S3
   - Create bucket (e.g., `omnify-uploads`)
   - Configure CORS and permissions

2. **Create IAM User**:
   - Create IAM user with S3 access
   - Generate access keys

3. **Set Variables**:
   ```bash
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   AWS_S3_BUCKET=omnify-uploads
   AWS_S3_REGION=us-east-1
   ```

#### Alternative: Azure Blob Storage
- Use Azure Storage Account connection string
- Set `FILE_STORAGE_ROOT=azure://account/container/`

#### Alternative: Google Cloud Storage
- Use GCS service account credentials
- Set `GCS_BUCKET=omnify-uploads`
- Set `GCS_CREDENTIALS_PATH=/path/to/credentials.json`

---

## Frontend Environment Variables

### Required

#### `REACT_APP_BACKEND_URL`
- **Description**: Backend API URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.omnify.ai`
- **Required**: ✅ Yes

#### `REACT_APP_ENVIRONMENT`
- **Description**: Environment name
- **Values**: `development`, `staging`, `production`
- **Required**: ✅ Yes

---

### Optional

#### `REACT_APP_GA_TRACKING_ID`
- **Description**: Google Analytics tracking ID
- **Format**: `UA-...` or `G-...`
- **Required**: ❌ Optional

#### `REACT_APP_SENTRY_DSN`
- **Description**: Sentry DSN for frontend error tracking
- **Required**: ❌ Optional

#### `REACT_APP_STRIPE_PUBLISHABLE_KEY`
- **Description**: Stripe publishable key (safe to expose)
- **Required**: ❌ Optional (Week 3+)

---

## Validation

### Backend Validation

The backend automatically validates environment variables on startup:

```bash
# Start backend
python -m uvicorn backend.agentkit_server:app --reload

# You'll see validation output:
✅ Configuration validation passed
# OR
❌ CRITICAL: Missing required environment variables:
   - MONGO_URL
   - OPENAI_API_KEY
```

### Manual Validation

Check if all required variables are set:

```bash
# Backend
python -c "from backend.core.config_validator import ConfigValidator; ConfigValidator.validate_and_exit()"
```

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use secrets manager** in production (AWS Secrets Manager, Vault)
3. **Rotate keys regularly** (especially JWT_SECRET_KEY)
4. **Use different keys** for development, staging, and production
5. **Limit API key permissions** to minimum required
6. **Monitor key usage** for suspicious activity

---

## Troubleshooting

### "Missing required environment variables"
- Check that all CRITICAL variables are set
- Verify variable names match exactly (case-sensitive)
- Check for typos or extra spaces

### "Connection refused" errors
- Verify `MONGO_URL` is correct
- Check MongoDB Atlas network access (whitelist IP)
- Verify database user has correct permissions

### "Invalid API key" errors
- Verify API key is correct (no extra spaces)
- Check if key has expired
- Verify key has required permissions/scopes

### Frontend can't connect to backend
- Verify `REACT_APP_BACKEND_URL` is correct
- Check CORS settings in backend
- Verify backend is running and accessible

---

## Next Steps

1. ✅ Set up all required variables
2. ✅ Test backend startup (should validate successfully)
3. ✅ Test frontend connection to backend
4. ✅ Set up platform integrations (one at a time)
5. ✅ Test end-to-end flow (signup → login → integration)

---

## Support

For help with environment setup:

- **Email**: support@omnify.ai
- **Documentation**: See `docs/` directory
- **Issues**: Check error logs for specific problems

---

**Last Updated**: November 21, 2025

