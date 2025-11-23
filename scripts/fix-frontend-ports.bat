@echo off
REM Fix Frontend Port Conflicts (Windows)
REM This script updates the legacy frontends to use different ports

echo Fixing frontend port conflicts...

REM Create .env files for each frontend
echo Creating .env files with port assignments...

REM Frontend (port 3100)
echo PORT=3100> frontend\.env
echo BROWSER=none>> frontend\.env

REM Frontend Admin (port 3200)
echo PORT=3200> frontend-admin\.env
echo BROWSER=none>> frontend-admin\.env

REM Frontend User (port 3300)
echo PORT=3300> frontend-user\.env
echo BROWSER=none>> frontend-user\.env

echo.
echo ✅ Port assignments configured via .env files!
echo.
echo 📋 New port configuration:
echo   - frontend:        http://localhost:3100
echo   - frontend-admin:  http://localhost:3200
echo   - frontend-user:   http://localhost:3300
echo   - omnify-brain:    http://localhost:3000
echo   - brain demo:      http://localhost:3001
echo.
echo 🚀 To start each frontend:
echo   cd frontend ^&^& npm start        # Port 3100
echo   cd frontend-admin ^&^& npm start  # Port 3200
echo   cd frontend-user ^&^& npm start   # Port 3300
echo.
echo Note: Ports are configured via .env files
echo You can now run all frontends simultaneously!
