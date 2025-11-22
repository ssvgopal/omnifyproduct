# Frontend Setup Script for Windows PowerShell
# OmniFy Cloud Connect - Frontend Setup

Write-Host "🚀 Setting up OmniFy Frontend..." -ForegroundColor Green
Write-Host ""

# Check Node.js version
Write-Host "Checking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node --version
if ($nodeVersion -match "v(\d+)") {
    $majorVersion = [int]$matches[1]
    if ($majorVersion -lt 18) {
        Write-Host "❌ Node.js version 18+ required. Current: $nodeVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Could not determine Node.js version" -ForegroundColor Red
    exit 1
}

# Check npm version
Write-Host "Checking npm version..." -ForegroundColor Yellow
$npmVersion = npm --version
Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
if (Test-Path "node_modules") {
    Write-Host "✅ node_modules directory exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    
    $envContent = @"
# Frontend Environment Configuration
# OmniFy Cloud Connect - React Application

# Backend API URL (REQUIRED)
REACT_APP_BACKEND_URL=http://localhost:8000

# Environment Configuration
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_PREDICTIVE_INTELLIGENCE=true
REACT_APP_ENABLE_ADVANCED_ANALYTICS=true

# Development Settings
DISABLE_HOT_RELOAD=false
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please review and update .env file if needed" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Frontend setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review .env file and update REACT_APP_BACKEND_URL if needed"
Write-Host "  2. Start development server: npm start"
Write-Host "  3. Run tests: npm test"
Write-Host "  4. Build for production: npm run build"
Write-Host ""

