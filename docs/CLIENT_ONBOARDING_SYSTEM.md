# Client Onboarding System

## Overview

The Client Onboarding System provides a comprehensive solution for onboarding clients/users, storing their assets (logos, creatives, analysis documents, campaign ideas), managing API credentials securely, and connecting to platforms (social media, drives, etc.) to start planning next steps.

## Features

### 1. Client Profile Management
- Create and manage client profiles with company information
- Store contact details, branding information, and metadata
- Track onboarding progress and status

### 2. File Storage
- Upload and manage files in multiple categories:
  - **Logo**: Company logos
  - **Creative**: Marketing creatives and assets
  - **Analysis Document**: Analysis reports and documents
  - **Campaign Idea**: Campaign idea documents
  - **Brand Guide**: Brand guidelines
  - **Other**: Miscellaneous files
- Files are stored in organized directory structure: `storage/{organization_id}/{client_id}/{category}/{file}`
- File metadata stored in MongoDB

### 3. Secure Credential Management
- Store API credentials securely using `ProductionSecretsManager`
- Supports multiple platforms:
  - Google Ads
  - Meta Ads
  - LinkedIn Ads
  - TikTok Ads
  - YouTube Ads
  - TripleWhale
  - HubSpot
  - Klaviyo
  - Shopify
  - GoHighLevel
- Credentials stored in secrets manager (Vault/AWS Secrets Manager/local encrypted)
- Only metadata stored in MongoDB (no sensitive data)

### 4. Platform Connection Testing
- Test platform connections using stored credentials
- Update connection status automatically
- Track connection errors and last verification time

### 5. Campaign Ideas Management
- Create and manage campaign ideas
- Store campaign details, target audience, platforms, budget estimates
- Track campaign idea status

### 6. Onboarding Status & Next Steps
- Track onboarding progress (0.0 to 1.0)
- Identify completed and pending steps
- Provide recommendations for next steps
- Calculate estimated completion time

## API Endpoints

### Client Profile Endpoints

#### `POST /api/client-onboarding/profiles`
Create a new client profile.

**Request Body:**
```json
{
  "company_name": "Acme Corp",
  "industry": "Technology",
  "website": "https://acme.com",
  "description": "Leading tech company",
  "primary_contact_name": "John Doe",
  "primary_contact_email": "john@acme.com",
  "primary_contact_phone": "+1234567890"
}
```

#### `GET /api/client-onboarding/profiles/{client_id}`
Get client profile by ID.

#### `PUT /api/client-onboarding/profiles/{client_id}`
Update client profile.

#### `GET /api/client-onboarding/profiles`
List all client profiles for the organization.

### File Upload Endpoints

#### `POST /api/client-onboarding/files/upload`
Upload a file for a client.

**Form Data:**
- `client_id`: Client ID
- `file`: File to upload
- `file_category`: One of: `logo`, `creative`, `analysis_document`, `campaign_idea`, `brand_guide`, `other`

**Response:**
```json
{
  "file_id": "file_abc123",
  "file_name": "logo.png",
  "file_url": "/storage/org123/client123/logo/file_abc123.png",
  "file_size": 102400,
  "file_category": "logo",
  "uploaded_at": "2025-11-21T12:00:00Z"
}
```

#### `GET /api/client-onboarding/files`
List files for a client.

**Query Parameters:**
- `client_id`: Client ID (required)
- `file_category`: Optional category filter

#### `DELETE /api/client-onboarding/files/{file_id}`
Delete a file.

**Query Parameters:**
- `client_id`: Client ID (required)

### Credentials Endpoints

#### `POST /api/client-onboarding/credentials`
Store platform credentials securely.

**Query Parameters:**
- `client_id`: Client ID (required)

**Request Body:**
```json
{
  "platform": "google_ads",
  "access_token": "ya29.abc123...",
  "refresh_token": "1//abc123...",
  "client_id": "123456789",
  "client_secret": "secret123",
  "account_id": "account123",
  "expires_at": "2025-12-21T12:00:00Z",
  "additional_config": {}
}
```

#### `POST /api/client-onboarding/credentials/test`
Test platform connection using stored credentials.

**Query Parameters:**
- `client_id`: Client ID (required)
- `platform`: Platform name (required)

### Campaign Ideas Endpoints

#### `POST /api/client-onboarding/campaign-ideas`
Create a campaign idea.

**Query Parameters:**
- `client_id`: Client ID (required)

**Request Body:**
```json
{
  "title": "Summer Sale Campaign",
  "description": "Promote summer products with special discounts",
  "target_audience": "Ages 25-45, interested in fashion",
  "platforms": ["meta_ads", "google_ads"],
  "budget_estimate": 10000.0,
  "timeline": "30 days"
}
```

#### `GET /api/client-onboarding/campaign-ideas`
List campaign ideas for a client.

**Query Parameters:**
- `client_id`: Client ID (required)

### Onboarding Status Endpoints

#### `GET /api/client-onboarding/status`
Get onboarding status and progress.

**Query Parameters:**
- `client_id`: Client ID (required)

**Response:**
```json
{
  "client_id": "client_abc123",
  "onboarding_status": "in_progress",
  "onboarding_progress": 0.6,
  "completed_steps": ["company_info", "logo_upload"],
  "pending_steps": ["platform_google_ads", "assets_upload"],
  "platform_connections": {
    "google_ads": {
      "status": "pending",
      "account_id": "account123",
      "connected_at": "2025-11-21T12:00:00Z"
    }
  },
  "connected_platforms": [],
  "next_steps": [
    "Connect at least one platform (e.g., Google Ads, Meta Ads)",
    "Upload brand assets and creatives"
  ],
  "recommendations": [
    "Ensure all brand assets are uploaded",
    "Connect primary advertising platforms",
    "Review and approve campaign ideas"
  ]
}
```

#### `GET /api/client-onboarding/next-steps`
Get next steps for client onboarding.

**Query Parameters:**
- `client_id`: Client ID (required)

## Architecture

### Components

1. **Models** (`backend/models/client_onboarding_models.py`)
   - Data models for client profiles, files, credentials, campaign ideas
   - Enums for onboarding status, file categories, platform connection status

2. **Service** (`backend/services/client_onboarding_service.py`)
   - Business logic for client onboarding
   - File storage management
   - Credential management using `ProductionSecretsManager`
   - Platform connection testing
   - Onboarding status calculation

3. **API Routes** (`backend/api/client_onboarding_routes.py`)
   - RESTful API endpoints
   - Authentication and authorization
   - Request/response handling

### Database Collections

- `client_profiles`: Client profile data
- `uploaded_files`: File metadata
- `platform_credentials`: Credential metadata (sensitive data in secrets manager)
- `campaign_ideas`: Campaign idea data

### File Storage

Files are stored in the local filesystem (configurable via `FILE_STORAGE_ROOT` environment variable):
```
storage/
  {organization_id}/
    {client_id}/
      logo/
        {file_id}.{ext}
      creative/
        {file_id}.{ext}
      analysis_document/
        {file_id}.{ext}
      ...
```

### Security

- **Credentials**: Stored in `ProductionSecretsManager` (supports Vault, AWS Secrets Manager, or local encrypted storage)
- **File Access**: Files are scoped to organization and client
- **Authentication**: All endpoints require JWT authentication
- **Authorization**: Users can only access their organization's data

## Usage Flow

1. **Create Client Profile**
   - POST `/api/client-onboarding/profiles`
   - Store company information and contact details

2. **Upload Assets**
   - POST `/api/client-onboarding/files/upload`
   - Upload logo, creatives, documents, etc.

3. **Store Platform Credentials**
   - POST `/api/client-onboarding/credentials`
   - Securely store API keys/tokens for platforms

4. **Test Platform Connections**
   - POST `/api/client-onboarding/credentials/test`
   - Verify credentials work and update connection status

5. **Create Campaign Ideas**
   - POST `/api/client-onboarding/campaign-ideas`
   - Document campaign ideas and plans

6. **Check Onboarding Status**
   - GET `/api/client-onboarding/status`
   - Get progress and next steps

7. **Get Next Steps**
   - GET `/api/client-onboarding/next-steps`
   - Get actionable recommendations

## Environment Variables

- `FILE_STORAGE_ROOT`: Root directory for file storage (default: `./storage`)
- `SECRETS_BACKEND`: Secrets manager backend (`vault`, `aws`, or `local`)
- `VAULT_URL`: HashiCorp Vault URL (if using Vault)
- `VAULT_TOKEN`: Vault authentication token
- `AWS_REGION`: AWS region (if using AWS Secrets Manager)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

## Next Steps

1. **Platform Integration**: Enhance platform connection testing to actually verify API access
2. **File Storage**: Consider migrating to cloud storage (S3, Azure Blob, etc.) for production
3. **Onboarding Workflow**: Add workflow automation for onboarding steps
4. **Notifications**: Add email/notification system for onboarding milestones
5. **Analytics**: Track onboarding completion rates and time-to-value metrics

## Testing

Example test flow:

```bash
# 1. Create client profile
curl -X POST http://localhost:8000/api/client-onboarding/profiles \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "primary_contact_name": "Test User",
    "primary_contact_email": "test@test.com"
  }'

# 2. Upload logo
curl -X POST http://localhost:8000/api/client-onboarding/files/upload \
  -H "Authorization: Bearer {token}" \
  -F "client_id=client_abc123" \
  -F "file=@logo.png" \
  -F "file_category=logo"

# 3. Store credentials
curl -X POST "http://localhost:8000/api/client-onboarding/credentials?client_id=client_abc123" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "google_ads",
    "access_token": "token123",
    "account_id": "account123"
  }'

# 4. Test connection
curl -X POST "http://localhost:8000/api/client-onboarding/credentials/test?client_id=client_abc123&platform=google_ads" \
  -H "Authorization: Bearer {token}"

# 5. Get status
curl -X GET "http://localhost:8000/api/client-onboarding/status?client_id=client_abc123" \
  -H "Authorization: Bearer {token}"
```

