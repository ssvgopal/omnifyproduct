# Quick Start Guide - Frontend Applications

**Date**: December 2024  
**Purpose**: Quick guide to start both frontend applications

---

## 🚀 Quick Start (Windows)

### Step 1: Install Dependencies

From the project root, run:

```powershell
npm install
```

This will install dependencies for all workspaces (frontend-user, frontend-admin, shared-ui).

### Step 2: Start User-Facing Frontend

**Option A: From root (using npm script)**
```powershell
npm run dev:user
```

**Option B: From frontend-user directory**
```powershell
cd frontend-user
npm start
```

**Access at**: http://localhost:4000

### Step 3: Start Admin Frontend (in a new terminal)

**Option A: From root (using npm script)**
```powershell
npm run dev:admin
```

**Option B: From frontend-admin directory**
```powershell
cd frontend-admin
npm start
```

**Access at**: http://localhost:4001

---

## 📋 What You'll See

### User-Facing Frontend (http://localhost:4000)
- **Landing Page** (`/`) - Marketing homepage
- **Demo** (`/demo`) - Interactive demo
- **Pricing** (`/pricing`) - Pricing tiers
- **Features** (`/features`) - Feature showcase
- **Dashboard** (`/dashboard`) - FACE module dashboard (requires auth)
- **Insights** (`/insights`) - Recommendations (requires auth)
- **Workflows** (`/workflows`) - Workflow management (requires auth)
- **Traces** (`/traces`) - Workflow traces (requires auth + subscription)
- **Settings** (`/settings`) - User settings (requires auth)
- **Profile** (`/profile`) - User profile (requires auth)

### Admin Frontend (http://localhost:4001)
- **Admin Dashboard** (`/`) - System overview (requires admin auth)
- **System Health** (`/health`) - Service monitoring
- **Logs** (`/logs`) - Log analysis and triaging
- **Workflows** (`/workflows`) - All workflows management
- **Performance** (`/performance`) - API performance metrics
- **Client Support** (`/support`) - Client issue analysis
- **User Management** (`/users`) - User accounts
- **Integration Management** (`/integrations`) - Platform integrations
- **Settings** (`/settings`) - System settings

---

## 🔧 Troubleshooting

### Issue: `@omnify/shared-ui` module not found

**Solution**: Make sure npm workspaces are set up correctly:
```powershell
# From root
npm install
```

If that doesn't work, manually link:
```powershell
cd packages\shared-ui
npm link
cd ..\..\frontend-user
npm link @omnify/shared-ui
cd ..\frontend-admin
npm link @omnify/shared-ui
```

### Issue: Port 4000 or 4001 already in use

**Solution**: Change the port in `craco.config.js`:
- User frontend: Edit `frontend-user/craco.config.js` → change port 4000
- Admin frontend: Edit `frontend-admin/craco.config.js` → change port 4001

### Issue: Components not rendering

**Solution**: Check that shared-ui components are properly imported. The import should be:
```javascript
import { Button, Card } from '@omnify/shared-ui';
```

If that fails, use relative imports temporarily:
```javascript
import { Button } from '../../../packages/shared-ui/components/button';
```

---

## 🐳 Alternative: Docker

If you prefer Docker:

```powershell
docker compose up --build
```

This starts both frontends:
- User frontend: http://localhost:4000
- Admin frontend: http://localhost:4001

---

## 📝 Notes

- Both frontends run independently
- They share the same backend API (http://localhost:8000)
- Authentication is currently placeholder (TODO: implement real auth)
- Shared components are imported from `@omnify/shared-ui`

---

**Ready to start!** Run `npm install` then `npm run dev:user` and `npm run dev:admin` in separate terminals.

