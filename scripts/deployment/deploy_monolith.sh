#!/bin/bash
# Deploy as monolith

echo "🚀 Deploying Omnify as Monolith..."

cd "$(dirname "$0")/../.."

# Build and run
docker-compose -f ops/docker/docker-compose.monolith.yml up --build -d

echo "✅ Monolith deployed!"
echo "API: http://localhost:8000"
echo "Frontend: http://localhost:3000"

