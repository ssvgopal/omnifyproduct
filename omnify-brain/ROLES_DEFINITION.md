# Role Definitions - Omnify Brain

**Three-tier role hierarchy for multi-tenant SaaS**

---

## 🎯 Role Hierarchy

```
VENDOR (Super Admin)
    ↓ Can manage everything
ADMIN (Organization Admin)
    ↓ Can manage their organization
USER (End User)
    ↓ Can view their organization's data
```

---

## 👤 ROLE 1: USER (End User / Team Member)

### Definition
Regular employees within a **client organization** who use the platform for their daily work.

### Who They Are
- **Marketing Managers** - Running campaigns, viewing performance
- **Data Analysts** - Analyzing metrics and trends
- **Campaign Coordinators** - Day-to-day campaign management
- **Content Creators** - Viewing creative performance

### Real-World Examples
- Sarah (CMO at "Demo Beauty Co") - Views dashboard daily
- Jason (Analyst at "Demo Beauty Co") - Analyzes ROI trends
- Emily (Marketing Manager at "Demo Beauty Co") - Reviews recommendations

### What They Can Do ✅
- ✅ View their organization's Brain dashboard (MEMORY, ORACLE, CURIOSITY)
- ✅ View analytics and historical trends
- ✅ View campaign performance
- ✅ View creative analysis
- ✅ Export reports (within limits)
- ✅ View their own profile settings
- ✅ Receive email notifications

### What They CANNOT Do ❌
- ❌ Invite or remove team members
- ❌ Change organization settings
- ❌ Connect or disconnect platforms (Meta, Google, etc.)
- ❌ View billing information
- ❌ View other organizations' data
- ❌ Change quotas or limits
- ❌ Access admin panel
- ❌ Access vendor panel

### Database Representation
```sql
role = 'user'
organization_id = '<their-company-uuid>'
```

### Routes They Access
- `/dashboard` - Main Brain dashboard
- `/analytics` - Historical trends and charts
- `/campaigns` - Campaign list and details
- `/profile` - Personal settings

### UI Theme
- **Color**: Blue (#3B82F6)
- **Focus**: Clarity, insights, actionable data
- **Layout**: Simple, clean, focused on content

---

## 👨‍💼 ROLE 2: ADMIN (Organization Administrator)

### Definition
Administrators within a **client organization** who manage the account, team, and integrations.

### Who They Are
- **Account Owner** - Person who signed up for Omnify
- **IT Manager** - Manages technical integrations
- **Team Lead** - Manages team access
- **Finance Manager** - Handles billing

### Real-World Examples
- John (CTO at "Demo Beauty Co") - Manages integrations and API keys
- Lisa (HR at "Demo Beauty Co") - Onboards new team members
- Mike (CFO at "Demo Beauty Co") - Reviews billing and usage

### What They Can Do ✅
- ✅ **Everything a USER can do**, PLUS:
- ✅ Invite and remove team members
- ✅ Assign roles (promote users to admin)
- ✅ Connect marketing platforms (Meta, Google, TikTok, Shopify)
- ✅ Configure OAuth integrations
- ✅ Manage API credentials
- ✅ Trigger manual data syncs
- ✅ View sync history and errors
- ✅ View billing and usage information
- ✅ Update payment methods
- ✅ Upgrade/downgrade plans
- ✅ Configure organization settings
- ✅ Set data retention policies
- ✅ Manage webhooks

### What They CANNOT Do ❌
- ❌ View other organizations' data
- ❌ Change quotas or limits (set by vendor)
- ❌ Access vendor panel
- ❌ View system-wide metrics
- ❌ Manage other organizations
- ❌ Adjust billing plans (only select from available plans)

### Database Representation
```sql
role = 'admin'
organization_id = '<their-company-uuid>'
```

### Routes They Access
- `/dashboard` - Brain dashboard (same as user)
- `/analytics` - Analytics (same as user)
- `/admin/team` - Team management
- `/admin/integrations` - Platform connections
- `/admin/billing` - Billing and usage
- `/admin/settings` - Organization settings

### UI Theme
- **Color**: Purple (#9333EA)
- **Focus**: Control, management, configuration
- **Layout**: Professional, organized, comprehensive

---

## 🔧 ROLE 3: VENDOR (Super Administrator)

### Definition
**Your team** at Omnify - the company providing the SaaS platform. Super administrators who manage the entire system and all client organizations.

### Who They Are
- **You** (Founder/Owner of Omnify)
- **Your Engineering Team** - DevOps, Backend engineers
- **Support Team** - Customer support engineers
- **Operations Team** - Business operations, billing management

### Real-World Examples
- You (Omnify CEO) - Oversees all clients, revenue, system health
- Alex (Omnify DevOps) - Monitors system performance, deploys updates
- Jordan (Omnify Support) - Helps clients troubleshoot issues
- Taylor (Omnify Ops) - Manages billing, quotas, client relationships

### What They Can Do ✅
- ✅ **Everything an ADMIN can do for ANY organization**, PLUS:
- ✅ View ALL client organizations
- ✅ Search and filter all clients
- ✅ View aggregated metrics (MRR, ARR, total users)
- ✅ Monitor system health (API response times, error rates)
- ✅ View and manage quotas for any organization
- ✅ Adjust limits (API calls, users, channels)
- ✅ View all billing across all clients
- ✅ Manual billing adjustments
- ✅ View security events and audit logs
- ✅ Manage feature flags (enable/disable features)
- ✅ Suspend or terminate accounts
- ✅ Access client data for support (with audit trail)
- ✅ View system-wide analytics
- ✅ Configure global settings
- ✅ Manage email templates
- ✅ View infrastructure metrics

### What They CANNOT Do ❌
- ❌ None - Full system access (with audit logging)

### Database Representation
```sql
role = 'vendor'
organization_id = NULL  -- Not tied to a specific organization
```

### Special Table
```sql
vendor_users (
  user_id UUID REFERENCES users(id),
  can_access_all_orgs BOOLEAN DEFAULT true,
  can_manage_billing BOOLEAN DEFAULT true,
  can_manage_quotas BOOLEAN DEFAULT true,
  can_view_security BOOLEAN DEFAULT true
)
```

### Routes They Access
- `/vendor/clients` - All client organizations
- `/vendor/monitoring` - System health and performance
- `/vendor/billing` - Revenue tracking across all clients
- `/vendor/security` - Security events and audit logs
- `/vendor/quotas` - Manage quotas for all clients
- `/vendor/settings` - Global system settings
- **Can also access**: Any `/dashboard` or `/admin` route for support purposes

### UI Theme
- **Color**: Dark slate (#0F172A) with amber/red accents
- **Focus**: Power, control, system-wide visibility
- **Layout**: Dark mode, dense information, professional

---

## 🔐 Permission Matrix

| Feature | USER | ADMIN | VENDOR |
|---------|------|-------|--------|
| **View own org dashboard** | ✅ | ✅ | ✅ |
| **View analytics** | ✅ | ✅ | ✅ |
| **Export reports** | ✅ | ✅ | ✅ |
| **Invite team members** | ❌ | ✅ | ✅ |
| **Remove team members** | ❌ | ✅ | ✅ |
| **Connect platforms** | ❌ | ✅ | ✅ |
| **View billing** | ❌ | ✅ | ✅ |
| **Change payment method** | ❌ | ✅ | ✅ |
| **Upgrade/downgrade plan** | ❌ | ✅ | ✅ |
| **View other organizations** | ❌ | ❌ | ✅ |
| **Adjust quotas** | ❌ | ❌ | ✅ |
| **View system metrics** | ❌ | ❌ | ✅ |
| **Manage feature flags** | ❌ | ❌ | ✅ |
| **View security events** | ❌ | ❌ | ✅ |
| **Access audit logs** | ❌ | ❌ | ✅ |

---

## 📊 Real-World Scenario

### Scenario: "Demo Beauty Co" subscribes to Omnify Brain

**Organization**: Demo Beauty Co (e-commerce beauty brand)

#### Their Team Structure
```
ADMINS (can manage everything for Demo Beauty Co)
├── John (CTO) - role: 'admin'
│   └── Manages integrations, API keys
└── Lisa (HR Manager) - role: 'admin'
    └── Manages team members

USERS (can view data only)
├── Sarah (CMO) - role: 'user'
│   └── Views dashboard daily, strategic decisions
├── Jason (Analyst) - role: 'user'
│   └── Analyzes trends, creates reports
└── Emily (Marketing Manager) - role: 'user'
    └── Reviews campaign performance
```

#### Your Team (Omnify)
```
VENDOR (manages all clients including Demo Beauty Co)
├── You (CEO) - role: 'vendor'
│   └── Views revenue, client health
├── Alex (DevOps) - role: 'vendor'
│   └── Monitors system performance
└── Jordan (Support) - role: 'vendor'
    └── Helps clients troubleshoot
```

### Access Examples

**User (Sarah) tries to access**:
- `/dashboard` → ✅ Allowed (sees Demo Beauty Co data)
- `/admin/team` → ❌ Redirected to `/dashboard`
- `/vendor/clients` → ❌ Redirected to `/dashboard`

**Admin (John) tries to access**:
- `/dashboard` → ✅ Allowed (sees Demo Beauty Co data)
- `/admin/team` → ✅ Allowed (manages Demo Beauty Co team)
- `/admin/integrations` → ✅ Allowed (connects Meta/Google)
- `/vendor/clients` → ❌ Redirected to `/dashboard`

**Vendor (You) tries to access**:
- `/dashboard` → ✅ Allowed (can view any org's dashboard)
- `/admin/team` → ✅ Allowed (can manage any org's team)
- `/vendor/clients` → ✅ Allowed (sees all clients)
- `/vendor/monitoring` → ✅ Allowed (system-wide health)

---

## 🎯 Key Principles

### 1. Organization Isolation
- **USER** and **ADMIN** can ONLY see their own organization
- **VENDOR** can see ALL organizations

### 2. Hierarchical Permissions
- **VENDOR** > **ADMIN** > **USER**
- Each level includes all permissions of levels below

### 3. Single Organization per User/Admin
- Users and Admins belong to ONE organization
- Tied via `organization_id` foreign key

### 4. Vendor Has No Organization
- `organization_id = NULL` for vendors
- Can access any organization for support

### 5. Audit Trail for Vendors
- All vendor actions logged in `audit_logs`
- IP address and user agent tracked
- Ensures accountability

---

## 🔤 Terminology Guidelines

### ✅ Correct Terms to Use

**For "user" role**:
- "End User"
- "Team Member"
- "User"
- "Regular User"

**For "admin" role**:
- "Admin"
- "Administrator"
- "Organization Admin"
- "Account Admin"
- "Team Admin"

**For "vendor" role**:
- "Vendor"
- "Super Admin"
- "System Administrator"
- "Omnify Team"
- "Platform Administrator"

### ❌ Avoid These Terms

**Don't say**:
- "Client" (ambiguous - client organization or end user?)
- "Customer" (ambiguous - the organization or the user?)
- "Owner" (confusing with organization ownership)
- "Manager" (confusing with Admin)
- "Root" or "Superuser" (too technical)

---

## 💡 Summary

| Role | Term | Who | Scope | Organization ID |
|------|------|-----|-------|-----------------|
| **user** | End User | Client company employee | Own org only | Required |
| **admin** | Administrator | Client company admin | Own org + management | Required |
| **vendor** | Super Admin | Your company (Omnify) | All orgs + system | NULL |

**Simple Rule**:
- **USER** = Can VIEW
- **ADMIN** = Can VIEW + MANAGE
- **VENDOR** = Can VIEW + MANAGE + CONTROL EVERYTHING

---

## 🚀 Implementation Checklist

- [x] Database column: `users.role` (VARCHAR)
- [x] Valid values: 'user', 'admin', 'vendor'
- [x] Middleware checks role for route access
- [x] Three separate UI layouts with distinct themes
- [x] Vendor has `organization_id = NULL`
- [x] Users/Admins have `organization_id = <uuid>`
- [ ] UI consistently uses correct terminology
- [ ] Error messages use correct role names
- [ ] Documentation uses consistent terminology

**This document is the source of truth for role definitions!** 📋
