# User Registration Flow & Database Architecture

## Overview
This document explains how user registration works in Omnify, including the database architecture, data flow, and security measures.

## Database: MongoDB

**Primary Database**: **MongoDB** (NoSQL document database)

- **Database Name**: `omnify_cloud` (configurable via `DB_NAME` environment variable)
- **Connection**: Uses `motor` (async MongoDB driver) via `AsyncIOMotorClient`
- **Connection String**: Configured via `MONGO_URL` environment variable
- **Collections Used**:
  - `users` - Stores user accounts
  - `organizations` - Stores organization/tenant data
  - `usage_quotas` - Tracks resource usage limits
  - `team_invitations` - Manages team member invitations
  - `subscriptions` - Subscription and billing information

## Registration Flow

### 1. Frontend Request
**Location**: `frontend-user/src/pages/Register.jsx`

User fills out registration form with:
- Organization Name
- First Name, Last Name
- Email Address
- Password (min 8 characters)
- Confirm Password

### 2. API Endpoint
**Endpoint**: `POST /api/auth/register`
**Location**: `backend/api/multi_tenancy_routes.py:110`

**Request Body Structure**:
```json
{
  "org_data": {
    "name": "Company Name",
    "billing_email": "admin@company.com",
    "subscription_plan": "free"
  },
  "admin_data": {
    "email": "admin@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!",
    "role": "admin",
    "preferences": {}
  }
}
```

### 3. Service Layer Processing
**Location**: `backend/services/multi_tenancy_service.py:841`

The `create_organization_with_admin()` method performs these steps:

#### Step 3.1: Create Organization
**Method**: `OrganizationManager.create_organization()`

**Actions**:
1. Generate unique `organization_id` (UUID v4)
2. Determine subscription plan (defaults to "free")
3. Create Stripe customer (if not free plan)
4. Create organization document in MongoDB:

```javascript
{
  "organization_id": "uuid-here",
  "name": "Company Name",
  "domain": "",
  "subscription_plan": "free",
  "subscription_status": "active", // or "trial" for paid plans
  "max_users": 5,        // Based on plan
  "max_campaigns": 10,   // Based on plan
  "max_storage_gb": 1,   // Based on plan
  "features": ["basic_attribution", "basic_reports"],
  "billing_info": {
    "billing_email": "admin@company.com",
    "stripe_customer_id": null, // or Stripe ID for paid plans
    "payment_method": null,
    "billing_address": {}
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "settings": {}
}
```

**MongoDB Collection**: `organizations`
**Indexes**:
- `organization_id` (unique)
- `slug` (unique, if used)
- `owner_id`

#### Step 3.2: Create Admin User
**Method**: `UserManager.create_user()`

**Actions**:
1. Generate unique `user_id` (UUID v4)
2. Hash password using bcrypt
3. Set role to `ORG_ADMIN`
4. Link user to organization via `organization_id`
5. Create user document in MongoDB:

```javascript
{
  "user_id": "uuid-here",
  "email": "admin@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "password_hash": "$2b$12$...", // bcrypt hashed password
  "role": "org_admin",
  "organization_id": "org-uuid-here",
  "is_active": true,
  "is_verified": false, // Email verification pending
  "last_login": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "preferences": {},
  "permissions": ["read", "write", "admin"] // Based on role
}
```

**MongoDB Collection**: `users`
**Indexes**:
- `email` (unique)
- `organization_id`
- `created_at`
- `email_verified`

**Security**:
- Password hashed with bcrypt (cost factor 12)
- Never stored in plain text
- Original password discarded after hashing

#### Step 3.3: Initialize Usage Quotas
**Method**: `UsageQuotaManager._create_default_quota()`

Creates quota tracking documents for:
- Users (max_users limit)
- Campaigns (max_campaigns limit)
- Storage (max_storage_gb limit)

**MongoDB Collection**: `usage_quotas`

### 4. Generate JWT Token
**Location**: `backend/services/multi_tenancy_service.py:127`

After successful registration:
1. Generate JWT access token using `UserManager.generate_jwt_token()`
2. Token includes:
   - `user_id`
   - `email`
   - `organization_id`
   - `role`
   - `exp` (expiration: 24 hours)
   - `iat` (issued at)

**JWT Secret**: From `JWT_SECRET` environment variable

### 5. Response to Frontend
**Response Structure**:
```json
{
  "organization": {
    "organization_id": "uuid",
    "name": "Company Name",
    "subscription_plan": "free",
    "subscription_status": "active",
    "max_users": 5,
    "max_campaigns": 10,
    "max_storage_gb": 1,
    "features": ["basic_attribution", "basic_reports"],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "admin_user": {
    "user_id": "uuid",
    "email": "admin@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "org_admin",
    "organization_id": "org-uuid",
    "is_active": true,
    "is_verified": false
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "status": "created"
}
```

### 6. Frontend Processing
**Location**: `frontend-user/src/pages/Register.jsx`

1. Store tokens in localStorage:
   - `access_token` → `localStorage.getItem('access_token')`
   - `refresh_token` → `localStorage.getItem('refresh_token')` (if provided)

2. Store user data:
   - User object → `localStorage.getItem('user')`

3. Update AuthContext:
   - Set user state
   - Set `isAuthenticated = true`

4. Redirect:
   - Auto-redirect to `/dashboard`
   - Or redirect to `/login` if no auto-login

## Database Schema Details

### Users Collection
```javascript
{
  _id: ObjectId,
  user_id: String (UUID, unique),
  email: String (unique, indexed),
  first_name: String,
  last_name: String,
  password_hash: String (bcrypt),
  role: String (enum: super_admin, org_admin, manager, analyst, viewer, guest),
  organization_id: String (indexed),
  is_active: Boolean,
  is_verified: Boolean,
  last_login: ISODate,
  created_at: ISODate,
  updated_at: ISODate,
  preferences: Object,
  permissions: Array[String]
}
```

### Organizations Collection
```javascript
{
  _id: ObjectId,
  organization_id: String (UUID, unique, indexed),
  name: String,
  domain: String,
  subscription_plan: String (enum: free, starter, professional, enterprise, custom),
  subscription_status: String (enum: active, trial, past_due, canceled, suspended),
  max_users: Number,
  max_campaigns: Number,
  max_storage_gb: Number,
  features: Array[String],
  billing_info: {
    billing_email: String,
    stripe_customer_id: String (nullable),
    payment_method: String (nullable),
    billing_address: Object
  },
  created_at: ISODate,
  updated_at: ISODate,
  settings: Object
}
```

## Security Measures

### 1. Password Security
- **Hashing**: bcrypt with cost factor 12
- **Storage**: Only hash stored, never plain text
- **Validation**: Minimum 8 characters (frontend validation)
- **Verification**: `PasswordManager.verify_password()` uses bcrypt comparison

### 2. Authentication
- **JWT Tokens**: Signed with secret key
- **Token Expiration**: 24 hours (86400 seconds)
- **Token Storage**: localStorage (consider httpOnly cookies for production)

### 3. Database Security
- **Indexes**: Unique constraints on email and organization_id
- **Validation**: Email format validation via Pydantic
- **Error Handling**: Exceptions caught and logged, no sensitive data exposed

### 4. Multi-Tenancy Isolation
- **Organization ID**: Every user linked to organization
- **Data Isolation**: Queries filtered by `organization_id`
- **Role-Based Access**: Permissions based on user role

## Subscription Plans

Default plan configurations (from `OrganizationManager.plan_configs`):

### Free Plan
- Max Users: 5
- Max Campaigns: 10
- Max Storage: 1 GB
- Features: Basic attribution, Basic reports
- Status: Active (no trial)

### Starter Plan
- Max Users: 10
- Max Campaigns: 50
- Max Storage: 10 GB
- Features: Multi-touch attribution, Advanced reports, API access
- Status: Trial (14 days)

### Professional Plan
- Max Users: 50
- Max Campaigns: 200
- Max Storage: 100 GB
- Features: All Starter + Predictive alerts, Custom dashboards, Priority support
- Status: Trial (14 days)

### Enterprise Plan
- Max Users: Unlimited
- Max Campaigns: Unlimited
- Max Storage: Unlimited
- Features: All Professional + Custom integrations, Dedicated support, SLA
- Status: Trial (30 days)

## Environment Variables Required

```bash
# MongoDB Connection
MONGO_URL=mongodb://localhost:27017
DB_NAME=omnify_cloud

# JWT Secret
JWT_SECRET=your-secret-key-here

# Stripe (for paid plans)
STRIPE_SECRET_KEY=sk_test_...

# Email Service (for verification emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Error Handling

### Common Errors

1. **Duplicate Email**:
   - MongoDB unique index on `email` prevents duplicates
   - Returns HTTP 400 with error message

2. **Invalid Email Format**:
   - Pydantic `EmailStr` validation
   - Returns HTTP 422 with validation error

3. **Weak Password**:
   - Frontend validation (min 8 chars)
   - Backend can add additional rules

4. **Database Connection Error**:
   - Logged and returns HTTP 500
   - User sees generic error message

## Post-Registration Steps

### 1. Email Verification (Optional)
- Verification token generated
- Email sent via SMTP
- User clicks link to verify
- `is_verified` set to `true`

### 2. Onboarding Flow
- Welcome email sent
- Initial setup wizard (optional)
- Integration setup prompts

### 3. Quota Initialization
- Usage quotas created for organization
- Tracks current usage vs. limits
- Enforced on API requests

## Testing Registration

### Manual Test Flow
1. Navigate to `/register`
2. Fill form with test data
3. Submit registration
4. Verify:
   - Organization created in MongoDB
   - User created in MongoDB
   - JWT token returned
   - Redirect to dashboard works
   - User can access protected routes

### Database Verification
```javascript
// Check organization
db.organizations.findOne({ organization_id: "..." })

// Check user
db.users.findOne({ email: "test@example.com" })

// Verify password hash
// Should be bcrypt hash starting with $2b$12$
```

## Future Enhancements

1. **Email Verification**: Implement email verification flow
2. **Password Reset**: Add forgot password functionality
3. **Two-Factor Authentication**: Add 2FA support
4. **Social Login**: OAuth integration (Google, GitHub, etc.)
5. **Invitation System**: Team member invitations
6. **Audit Logging**: Track registration events
7. **Rate Limiting**: Prevent registration spam
8. **CAPTCHA**: Add bot protection

## Related Files

- **Frontend**: `frontend-user/src/pages/Register.jsx`
- **API Route**: `backend/api/multi_tenancy_routes.py:110`
- **Service**: `backend/services/multi_tenancy_service.py:841`
- **User Manager**: `backend/services/multi_tenancy_service.py:117`
- **Organization Manager**: `backend/services/multi_tenancy_service.py:339`
- **Database Schema**: `backend/database/mongodb_schema.py`
- **API Service**: `frontend-user/src/services/api.js`

