# Multi-Panel Architecture - Omnify Brain

**Three-Panel SaaS Architecture**

---

## 🎯 Overview

Single Next.js application with **three distinct interfaces** based on user roles:

1. **User Panel** - End users from client companies
2. **Admin Panel** - Administrators from client companies
3. **Vendor Panel** - Super admins from Omnify (your team)

---

## 🏗️ Architecture Design

### Route Structure
```
src/app/
├── (public)/                  # Public routes (landing, login)
│   ├── page.tsx              # Landing page
│   └── login/                # Unified login
│
├── (user)/                    # USER PANEL - Client end users
│   ├── dashboard/
│   ├── campaigns/
│   ├── analytics/
│   └── settings/
│
├── (admin)/                   # ADMIN PANEL - Client admins
│   ├── overview/
│   ├── team/
│   ├── integrations/
│   ├── billing/
│   └── settings/
│
├── (vendor)/                  # VENDOR PANEL - Omnify super admins
│   ├── clients/              # Manage all clients
│   ├── monitoring/           # System health
│   ├── billing/              # All client billing
│   ├── security/             # Security monitoring
│   ├── quotas/               # Usage limits
│   └── settings/             # Global settings
│
└── api/
    ├── auth/                 # Authentication
    ├── brain/                # Brain APIs
    └── vendor/               # Vendor-only APIs
```

---

## 👥 Role Definitions

### 1. USER (End User)
**Who**: Regular employees at client companies (e.g., Sarah, Jason, Emily)

**Permissions**:
- ✅ View own organization's dashboard
- ✅ View analytics and insights
- ✅ View recommendations
- ❌ Cannot change integrations
- ❌ Cannot manage team
- ❌ Cannot view billing

**Use Cases**:
- Daily dashboard monitoring
- Campaign performance tracking
- AI-powered recommendations
- Export reports

**Routes**: `/dashboard`, `/analytics`, `/reports`, `/profile`

---

### 2. ADMIN (Client Admin)
**Who**: Administrators at client companies (IT managers, account owners)

**Permissions**:
- ✅ Everything USER can do
- ✅ Manage team members
- ✅ Connect/disconnect platforms (Meta, Google, etc.)
- ✅ Configure integrations
- ✅ View billing & usage
- ✅ Organization settings
- ❌ Cannot see other organizations
- ❌ Cannot change quotas/limits

**Use Cases**:
- Onboard new team members
- Connect marketing platforms
- Monitor usage and billing
- Configure organization settings
- Manage API credentials

**Routes**: `/admin/team`, `/admin/integrations`, `/admin/billing`, `/admin/settings`

---

### 3. VENDOR (Super Admin)
**Who**: Omnify team members (you and your team)

**Permissions**:
- ✅ View ALL client organizations
- ✅ Manage quotas and limits
- ✅ Monitor system health
- ✅ Configure billing plans
- ✅ Security monitoring
- ✅ Support interventions
- ✅ Feature flags
- ✅ Global analytics

**Use Cases**:
- Monitor all clients
- Troubleshoot client issues
- Adjust quotas/limits
- Manage billing plans
- Security incident response
- Feature rollouts
- System health monitoring

**Routes**: `/vendor/clients`, `/vendor/monitoring`, `/vendor/billing`, `/vendor/security`

---

## 🔐 Authentication & Authorization

### Database Schema Updates

```sql
-- Add role to users table
ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';
-- Possible values: 'user', 'admin', 'vendor'

-- Add vendor-specific table
CREATE TABLE vendor_users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) UNIQUE,
  permissions JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Add organization quotas
CREATE TABLE organization_quotas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) UNIQUE,
  plan VARCHAR(50) DEFAULT 'free', -- free, starter, growth, enterprise
  max_users INT DEFAULT 5,
  max_channels INT DEFAULT 3,
  max_api_calls INT DEFAULT 10000,
  features JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Add usage tracking
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id),
  resource_type VARCHAR(50), -- api_call, sync, brain_compute
  count INT DEFAULT 1,
  date DATE DEFAULT CURRENT_DATE,
  metadata JSONB DEFAULT '{}'
);
```

### Middleware Updates

```typescript
// src/middleware.ts
import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token;
    const path = req.nextUrl.pathname;

    // Vendor routes - requires vendor role
    if (path.startsWith('/vendor')) {
      if (token?.role !== 'vendor') {
        return NextResponse.redirect(new URL('/dashboard', req.url));
      }
    }

    // Admin routes - requires admin or vendor role
    if (path.startsWith('/admin')) {
      if (token?.role !== 'admin' && token?.role !== 'vendor') {
        return NextResponse.redirect(new URL('/dashboard', req.url));
      }
    }

    // User routes - all authenticated users
    if (path.startsWith('/dashboard') || path.startsWith('/analytics')) {
      if (!token) {
        return NextResponse.redirect(new URL('/login', req.url));
      }
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/vendor/:path*', '/analytics/:path*'],
};
```

---

## 🎨 UI/UX Design

### User Panel (Blue Theme)
- **Focus**: Simplicity, clarity, insights
- **Navigation**: Dashboard, Campaigns, Analytics, Profile
- **Colors**: Blue accents, clean white backgrounds
- **Widgets**: Brain cards (Memory, Oracle, Curiosity)

### Admin Panel (Purple Theme)
- **Focus**: Control, configuration, team management
- **Navigation**: Overview, Team, Integrations, Billing, Settings
- **Colors**: Purple accents, professional
- **Widgets**: Integration status, team list, usage charts

### Vendor Panel (Dark Theme)
- **Focus**: Power, monitoring, system control
- **Navigation**: Clients, Monitoring, Billing, Security, Quotas
- **Colors**: Dark mode with red/orange accents for alerts
- **Widgets**: System health, client list, revenue metrics, security alerts

---

## 📊 Feature Breakdown

### USER PANEL Features

#### Dashboard
- Brain state visualization (Memory, Oracle, Curiosity)
- Persona toggle (Sarah/Jason/Emily)
- Executive summary
- Key metrics (ROAS, Spend, Revenue)
- Quick actions

#### Analytics
- Historical trends (Recharts)
- Date range selector
- Channel performance
- Creative analysis
- Export functionality

#### Campaigns
- Campaign list
- Performance metrics
- Creative gallery
- Recommendations

#### Profile
- Personal settings
- Notification preferences
- Theme settings

---

### ADMIN PANEL Features

#### Team Management
- Invite team members
- Manage roles (user/admin)
- Deactivate users
- View activity logs

#### Integrations
- Connect platforms:
  - Meta Ads (OAuth)
  - Google Ads (OAuth)
  - TikTok Ads (OAuth)
  - Shopify (API key)
- Sync status & history
- Manual sync triggers
- Webhook management

#### Billing
- Current plan
- Usage metrics vs quotas
- Invoice history
- Payment method
- Upgrade/downgrade

#### Settings
- Organization profile
- API credentials (view only)
- Data retention policies
- Export settings

---

### VENDOR PANEL Features

#### Client Management
- List all organizations
- Search & filter
- Client details
- Usage overview
- Quick actions (suspend, delete, support)

#### Monitoring
- System health dashboard
- API response times
- Error rates
- Active users
- Sync job status
- Database metrics

#### Billing Management
- All client billing overview
- MRR/ARR metrics
- Plan distribution
- Revenue trends
- Dunning management
- Manual adjustments

#### Security
- Failed login attempts
- Suspicious activity
- API key usage
- Rate limit violations
- Security alerts
- Audit logs

#### Quota Management
- View all quotas
- Adjust limits per client
- Bulk updates
- Usage alerts
- Overage handling

#### Global Settings
- Feature flags
- System maintenance
- Email templates
- Notification settings
- Integration configs

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Update database schema
- [ ] Implement three-role authentication
- [ ] Update middleware for route protection
- [ ] Create base layouts for each panel

### Phase 2: User Panel (Week 2)
- [ ] Dashboard page (existing, enhance)
- [ ] Analytics page with charts
- [ ] Campaigns page
- [ ] Profile page
- [ ] Mobile responsive

### Phase 3: Admin Panel (Week 3)
- [ ] Team management UI
- [ ] Integrations page (OAuth flows)
- [ ] Billing page
- [ ] Settings page
- [ ] Sync management UI

### Phase 4: Vendor Panel (Week 4)
- [ ] Client list & details
- [ ] Monitoring dashboard
- [ ] Billing overview
- [ ] Security dashboard
- [ ] Quota management
- [ ] Global settings

### Phase 5: Polish (Week 5)
- [ ] Unified design system
- [ ] Dark mode for vendor
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Deployment

---

## 🔧 Technical Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: TailwindCSS
- **Components**: shadcn/ui + Radix UI
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod
- **State**: React Context + SWR

### Backend
- **Database**: Supabase (PostgreSQL)
- **Auth**: NextAuth.js
- **API**: Next.js API routes
- **Caching**: React Cache + SWR
- **Queue**: (Future: BullMQ for jobs)

### Infrastructure
- **Hosting**: Vercel
- **Database**: Supabase
- **Storage**: Supabase Storage (for exports, etc.)
- **Email**: (Future: Resend or SendGrid)
- **Monitoring**: Sentry + LogRocket

---

## 📝 Directory Structure

```
src/
├── app/
│   ├── (public)/
│   │   ├── layout.tsx        # Public layout
│   │   ├── page.tsx          # Landing
│   │   └── login/
│   │
│   ├── (user)/
│   │   ├── layout.tsx        # User layout (blue theme)
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── campaigns/
│   │   └── profile/
│   │
│   ├── (admin)/
│   │   ├── layout.tsx        # Admin layout (purple theme)
│   │   ├── team/
│   │   ├── integrations/
│   │   ├── billing/
│   │   └── settings/
│   │
│   ├── (vendor)/
│   │   ├── layout.tsx        # Vendor layout (dark theme)
│   │   ├── clients/
│   │   ├── monitoring/
│   │   ├── billing/
│   │   ├── security/
│   │   └── quotas/
│   │
│   └── api/
│       ├── auth/
│       ├── brain/
│       ├── admin/            # Admin-only APIs
│       └── vendor/           # Vendor-only APIs
│
├── components/
│   ├── user/                 # User panel components
│   ├── admin/                # Admin panel components
│   ├── vendor/               # Vendor panel components
│   ├── shared/               # Shared components
│   └── ui/                   # Base UI components
│
├── lib/
│   ├── auth/
│   ├── db/
│   ├── hooks/
│   ├── services/
│   └── utils/
│
└── middleware.ts
```

---

## 🎯 Next Steps

1. **Review & Approve** this architecture
2. **Update database schema** (new tables, roles)
3. **Implement authentication updates** (three roles)
4. **Build layouts** for each panel
5. **Start with User Panel** (enhance existing dashboard)
6. **Add Admin Panel** (team, integrations)
7. **Build Vendor Panel** (client management, monitoring)

---

## 🚨 Security Considerations

### Role Isolation
- Strict middleware checks
- API-level permission validation
- No client-side role checks only

### Vendor Access Logging
- Log all vendor actions
- Audit trail for client data access
- Alert on suspicious vendor activity

### Data Protection
- Vendor cannot see sensitive data by default
- Support mode requires audit log
- API keys encrypted at rest

### Rate Limiting
- Per-role rate limits
- Vendor has higher limits
- Client-specific quotas enforced

---

## 📊 Success Metrics

### User Panel
- Time to insights < 5 seconds
- Dashboard load time < 2 seconds
- User engagement rate > 70%

### Admin Panel
- Team onboarding time < 5 minutes
- Integration success rate > 95%
- Self-service resolution > 80%

### Vendor Panel
- Client issue resolution time < 1 hour
- System uptime > 99.9%
- Alert response time < 5 minutes

---

**Ready to build? Let's start with database schema updates and authentication!** 🚀
