# Frontend Split - Setup Guide

**Date**: December 2024  
**Purpose**: Guide for setting up and running the split frontends

---

## 📋 Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Docker (for containerized deployment)

---

## 🚀 Local Development Setup

### Step 1: Install Dependencies

Since we're using a local shared-ui package, you have two options:

#### Option A: Use npm workspaces (Recommended)

Update root `package.json`:
```json
{
  "name": "omnify-product",
  "workspaces": [
    "frontend-user",
    "frontend-admin",
    "packages/shared-ui"
  ]
}
```

Then run from root:
```bash
npm install
```

#### Option B: Manual Linking

1. **Install shared-ui dependencies:**
```bash
cd packages/shared-ui
npm install
```

2. **Link shared-ui package:**
```bash
cd packages/shared-ui
npm link
```

3. **Link in frontend-user:**
```bash
cd frontend-user
npm link @omnify/shared-ui
npm install
```

4. **Link in frontend-admin:**
```bash
cd frontend-admin
npm link @omnify/shared-ui
npm install
```

### Step 2: Start Development Servers

**User-Facing Frontend:**
```bash
cd frontend-user
npm start
```
Runs on: http://localhost:3000

**Admin Frontend:**
```bash
cd frontend-admin
npm start
```
Runs on: http://localhost:3001

---

## 🐳 Docker Setup

### Build and Run with Docker Compose

```bash
# From project root
docker compose up --build
```

This will start:
- `frontend-user` on port 3000
- `frontend-admin` on port 3001
- Backend API on port 8000
- All supporting services (MongoDB, Redis, etc.)

### Build Individual Services

**User Frontend:**
```bash
cd frontend-user
docker build -t omnify-frontend-user .
docker run -p 3000:80 omnify-frontend-user
```

**Admin Frontend:**
```bash
cd frontend-admin
docker build -t omnify-frontend-admin .
docker run -p 3001:80 omnify-frontend-admin
```

---

## 📁 Project Structure

```
omnifyproduct/
├── frontend-user/          # User-facing application
│   ├── src/
│   │   ├── pages/         # 10 pages
│   │   ├── components/    # User components
│   │   ├── routes/        # UserRoutes.js
│   │   └── services/      # API services
│   ├── package.json
│   └── Dockerfile
│
├── frontend-admin/         # Admin backoffice
│   ├── src/
│   │   ├── pages/         # 10 admin pages
│   │   ├── components/    # Admin components
│   │   ├── routes/        # AdminRoutes.js
│   │   └── services/      # Admin API services
│   ├── package.json
│   └── Dockerfile
│
└── packages/
    └── shared-ui/          # Shared components
        ├── components/     # 48 UI components
        ├── hooks/         # Shared hooks
        ├── utils/         # Shared utilities
        └── package.json
```

---

## 🔧 Configuration

### Environment Variables

**frontend-user/.env:**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

**frontend-admin/.env:**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=production
REACT_APP_ADMIN_MODE=true
```

---

## 🧪 Testing

### Run Tests

**User Frontend:**
```bash
cd frontend-user
npm test
```

**Admin Frontend:**
```bash
cd frontend-admin
npm test
```

### Build for Production

**User Frontend:**
```bash
cd frontend-user
npm run build
```

**Admin Frontend:**
```bash
cd frontend-admin
npm run build
```

---

## 🚨 Troubleshooting

### Issue: `@omnify/shared-ui` not found

**Solution**: Make sure you've linked the shared-ui package:
```bash
cd packages/shared-ui
npm link
cd ../../frontend-user
npm link @omnify/shared-ui
```

### Issue: Port already in use

**Solution**: Change ports in `craco.config.js`:
- User frontend: port 3000
- Admin frontend: port 3001

### Issue: Components not importing

**Solution**: Check that shared-ui package.json exports are correct and components are in the right directory.

---

## 📝 Next Steps

1. **Install Dependencies**: Follow Step 1 above
2. **Start Development**: Run both frontends
3. **Connect APIs**: Update API service files
4. **Add Authentication**: Implement auth flows
5. **Test**: Run unit and integration tests
6. **Deploy**: Follow deployment guide

---

**Status**: Ready for local development setup

