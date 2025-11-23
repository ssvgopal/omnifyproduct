#!/bin/bash

# Fix Frontend Port Conflicts
# This script updates the legacy frontends to use different ports

set -e

echo "🔧 Fixing frontend port conflicts..."

# Backup package.json files
echo "📦 Creating backups..."
cp frontend/package.json frontend/package.json.backup
cp frontend-admin/package.json frontend-admin/package.json.backup
cp frontend-user/package.json frontend-user/package.json.backup

# Fix frontend (port 3100)
echo "🔨 Setting frontend to port 3100..."
cd frontend
npm pkg set scripts.start="PORT=3100 craco start"
cd ..

# Fix frontend-admin (port 3200)
echo "🔨 Setting frontend-admin to port 3200..."
cd frontend-admin
npm pkg set scripts.start="PORT=3200 craco start"
cd ..

# Fix frontend-user (port 3300)
echo "🔨 Setting frontend-user to port 3300..."
cd frontend-user
npm pkg set scripts.start="PORT=3300 craco start"
cd ..

echo ""
echo "✅ Port assignments updated!"
echo ""
echo "📋 New port configuration:"
echo "  - frontend:        http://localhost:3100"
echo "  - frontend-admin:  http://localhost:3200"
echo "  - frontend-user:   http://localhost:3300"
echo "  - omnify-brain:    http://localhost:3000"
echo "  - brain demo:      http://localhost:3001"
echo ""
echo "🚀 To start each frontend:"
echo "  cd frontend && npm start        # Port 3100"
echo "  cd frontend-admin && npm start  # Port 3200"
echo "  cd frontend-user && npm start   # Port 3300"
