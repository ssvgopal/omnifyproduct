#!/bin/bash
# Frontend Setup Script for Linux/Mac/Git Bash
# OmniFy Cloud Connect - Frontend Setup

echo "🚀 Setting up OmniFy Frontend..."
echo ""

# Check Node.js version
echo "Checking Node.js version..."
NODE_VERSION=$(node --version)
if [[ $NODE_VERSION =~ v([0-9]+) ]]; then
    MAJOR_VERSION=${BASH_REMATCH[1]}
    if [ "$MAJOR_VERSION" -lt 18 ]; then
        echo "❌ Node.js version 18+ required. Current: $NODE_VERSION"
        exit 1
    fi
    echo "✅ Node.js version: $NODE_VERSION"
else
    echo "❌ Could not determine Node.js version"
    exit 1
fi

# Check npm version
echo "Checking npm version..."
NPM_VERSION=$(npm --version)
echo "✅ npm version: $NPM_VERSION"
echo ""

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✅ node_modules directory exists"
else
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    
    cat > .env << 'EOF'
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
EOF
    
    echo "✅ .env file created"
    echo "⚠️  Please review and update .env file if needed"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review .env file and update REACT_APP_BACKEND_URL if needed"
echo "  2. Start development server: npm start"
echo "  3. Run tests: npm test"
echo "  4. Build for production: npm run build"
echo ""



