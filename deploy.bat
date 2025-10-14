@echo off
REM OmniFy Cloud Connect - Windows Deployment Script
REM This script provides easy deployment options for Windows environments

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch, but we'll use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

echo.
echo ================================
echo OmniFy Cloud Connect Deployment
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Docker is not installed or not in PATH
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Docker Compose is not available
    echo Please ensure Docker Compose is installed
    pause
    exit /b 1
)

echo %SUCCESS% Docker and Docker Compose are available

REM Check if .env file exists
if not exist .env (
    if exist env.example (
        echo %INFO% Creating .env file from env.example...
        copy env.example .env
        echo %WARNING% Please edit .env file with your actual API keys and credentials
        echo You can use the following command to edit:
        echo   notepad .env
        echo.
        echo Press any key when you're ready to continue...
        pause >nul
    ) else (
        echo %ERROR% No env.example file found. Please create a .env file manually.
        pause
        exit /b 1
    )
) else (
    echo %SUCCESS% .env file already exists
)

REM Generate secure passwords if needed
echo %INFO% Checking password configuration...

REM Check if MongoDB password needs to be generated
findstr /C:"MONGO_ROOT_PASSWORD=your_secure_password_here" .env >nul
if %errorlevel% equ 0 (
    echo %INFO% Generating secure MongoDB password...
    REM Note: Windows doesn't have openssl by default, so we'll use a simple approach
    set "MONGO_PASS=OmniFy%RANDOM%%RANDOM%%RANDOM%"
    powershell -Command "(Get-Content .env) -replace 'MONGO_ROOT_PASSWORD=your_secure_password_here', 'MONGO_ROOT_PASSWORD=%MONGO_PASS%' | Set-Content .env"
    echo %SUCCESS% Generated secure MongoDB password
)

REM Check if Redis password needs to be generated
findstr /C:"REDIS_PASSWORD=your_redis_password_here" .env >nul
if %errorlevel% equ 0 (
    echo %INFO% Generating secure Redis password...
    set "REDIS_PASS=OmniFy%RANDOM%%RANDOM%%RANDOM%"
    powershell -Command "(Get-Content .env) -replace 'REDIS_PASSWORD=your_redis_password_here', 'REDIS_PASSWORD=%REDIS_PASS%' | Set-Content .env"
    echo %SUCCESS% Generated secure Redis password
)

REM Check if JWT secret needs to be generated
findstr /C:"JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters_long" .env >nul
if %errorlevel% equ 0 (
    echo %INFO% Generating secure JWT secret...
    set "JWT_SECRET=OmniFy%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%"
    powershell -Command "(Get-Content .env) -replace 'JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters_long', 'JWT_SECRET_KEY=%JWT_SECRET%' | Set-Content .env"
    echo %SUCCESS% Generated secure JWT secret
)

:menu
echo.
echo ================================
echo OmniFy Cloud Connect Deployment
echo ================================
echo.
echo 1) Deploy Development Environment
echo 2) Deploy Production Environment
echo 3) Show Service Status
echo 4) Show Logs
echo 5) Stop Services
echo 6) Cleanup (Remove All)
echo 0) Exit
echo.

set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" goto dev_deploy
if "%choice%"=="2" goto prod_deploy
if "%choice%"=="3" goto show_status
if "%choice%"=="4" goto show_logs
if "%choice%"=="5" goto stop_services
if "%choice%"=="6" goto cleanup
if "%choice%"=="0" goto exit
echo %ERROR% Invalid choice. Please try again.
goto menu

:dev_deploy
echo.
echo ================================
echo Deploying Development Environment
echo ================================
echo.

echo %INFO% Building and starting services...
docker-compose up --build -d

echo %INFO% Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

REM Check service health
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% Backend service is healthy
) else (
    echo %WARNING% Backend service may still be starting up
)

curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% Frontend service is healthy
) else (
    echo %WARNING% Frontend service may still be starting up
)

echo.
echo %SUCCESS% Development environment deployed successfully!
echo %INFO% Access your application at:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo   Grafana: http://localhost:3001 (admin/admin)
echo   Prometheus: http://localhost:9090
echo.
pause
goto menu

:prod_deploy
echo.
echo ================================
echo Deploying Production Environment
echo ================================
echo.

echo %WARNING% Production deployment requires additional configuration:
echo 1. SSL certificates
echo 2. Domain configuration
echo 3. Production API keys
echo 4. Database backups
echo 5. Monitoring setup
echo.

set /p confirm="Do you want to continue with production deployment? (y/N): "
if /i not "%confirm%"=="y" (
    echo %INFO% Production deployment cancelled
    goto menu
)

echo %INFO% Building production images...
docker-compose -f docker-compose.prod.yml build

echo %INFO% Starting production services...
docker-compose -f docker-compose.prod.yml up -d

echo %SUCCESS% Production environment deployed!
echo %INFO% Make sure to configure your reverse proxy and SSL certificates
echo.
pause
goto menu

:show_status
echo.
echo ================================
echo Service Status
echo ================================
echo.

docker-compose ps

echo.
echo %INFO% Service Health Checks:

REM Check backend
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% ✓ Backend API (http://localhost:8000)
) else (
    echo %ERROR% ✗ Backend API (http://localhost:8000)
)

REM Check frontend
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% ✓ Frontend (http://localhost:3000)
) else (
    echo %ERROR% ✗ Frontend (http://localhost:3000)
)

echo.
pause
goto menu

:show_logs
echo.
echo ================================
echo Showing Service Logs
echo ================================
echo.

echo Select service to view logs:
echo 1) Backend
echo 2) Frontend
echo 3) MongoDB
echo 4) Redis
echo 5) All services

set /p log_choice="Enter your choice (1-5): "

if "%log_choice%"=="1" (
    docker-compose logs -f backend
) else if "%log_choice%"=="2" (
    docker-compose logs -f frontend
) else if "%log_choice%"=="3" (
    docker-compose logs -f mongodb
) else if "%log_choice%"=="4" (
    docker-compose logs -f redis
) else if "%log_choice%"=="5" (
    docker-compose logs -f
) else (
    echo %ERROR% Invalid choice
)

echo.
pause
goto menu

:stop_services
echo.
echo ================================
echo Stopping Services
echo ================================
echo.

docker-compose down
echo %SUCCESS% All services stopped
echo.
pause
goto menu

:cleanup
echo.
echo ================================
echo Cleaning Up
echo ================================
echo.

echo %WARNING% This will remove all containers, volumes, and images. Are you sure?
set /p cleanup_confirm="Type 'yes' to confirm: "

if /i "%cleanup_confirm%"=="yes" (
    docker-compose down -v --rmi all
    docker system prune -f
    echo %SUCCESS% Cleanup completed
) else (
    echo %INFO% Cleanup cancelled
)

echo.
pause
goto menu

:exit
echo.
echo %SUCCESS% Goodbye!
exit /b 0
