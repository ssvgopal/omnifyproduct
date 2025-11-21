#!/bin/bash
# Deploy as microservices

echo "🚀 Deploying Omnify as Microservices..."

cd "$(dirname "$0")/../.."

# Build and run
docker-compose -f ops/docker/docker-compose.microservices.yml up --build -d

echo "✅ Microservices deployed!"
echo "Auth Service: http://localhost:8001"
echo "Integrations Service: http://localhost:8002"
echo "AgentKit Service: http://localhost:8003"
echo "Analytics Service: http://localhost:8004"
echo "Onboarding Service: http://localhost:8005"
echo "ML Service: http://localhost:8006"
echo "Infrastructure Service: http://localhost:8007"
echo "Frontend: http://localhost:3000"

