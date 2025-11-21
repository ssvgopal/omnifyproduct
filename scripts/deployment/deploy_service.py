#!/usr/bin/env python3
"""
Deploy a single service as microservice
Usage: python deploy_service.py <service_name>
"""

import sys
import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

SERVICES = {
    "auth": {"port": 8001, "dockerfile": "services/auth_service/Dockerfile"},
    "integrations": {"port": 8002, "dockerfile": "services/integrations_service/Dockerfile"},
    "agentkit": {"port": 8003, "dockerfile": "services/agentkit_service/Dockerfile"},
    "analytics": {"port": 8004, "dockerfile": "services/analytics_service/Dockerfile"},
    "onboarding": {"port": 8005, "dockerfile": "services/onboarding_service/Dockerfile"},
    "ml": {"port": 8006, "dockerfile": "services/ml_service/Dockerfile"},
    "infrastructure": {"port": 8007, "dockerfile": "services/infrastructure_service/Dockerfile"},
}

def deploy_service(service_name: str):
    """Deploy a single service"""
    if service_name not in SERVICES:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available services: {', '.join(SERVICES.keys())}")
        sys.exit(1)
    
    service = SERVICES[service_name]
    print(f"🚀 Deploying {service_name} service on port {service['port']}...")
    
    # Build Docker image
    dockerfile = ROOT_DIR / service['dockerfile']
    image_name = f"omnify/{service_name}-service:latest"
    
    cmd = [
        "docker", "build",
        "-f", str(dockerfile),
        "-t", image_name,
        str(ROOT_DIR)
    ]
    
    print(f"Building image: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    if result.returncode != 0:
        print(f"❌ Build failed")
        sys.exit(1)
    
    print(f"✅ Service {service_name} built successfully!")
    print(f"Run with: docker run -p {service['port']}:{service['port']} -e DEPLOYMENT_MODE=microservices -e SERVICE_NAME={service_name} {image_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_service.py <service_name>")
        print(f"Available services: {', '.join(SERVICES.keys())}")
        sys.exit(1)
    
    deploy_service(sys.argv[1])

