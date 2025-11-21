#!/bin/bash
# Deploy as hybrid (monolith + one microservice)

echo "🚀 Deploying Omnify as Hybrid (Monolith + Microservices)..."

cd "$(dirname "$0")/../.."

# Build and run
docker-compose -f ops/docker/docker-compose.hybrid.yml up --build -d

echo "✅ Hybrid deployment complete!"
echo "Monolith API: http://localhost:8000"
echo "Integrations Service (Microservice): http://localhost:8002"
echo "Frontend: http://localhost:3000"

