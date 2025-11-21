#!/usr/bin/env python3
"""
Test hybrid deployment - validates both monolith and microservices modes
"""

import asyncio
import httpx
import sys
from typing import Dict, List

SERVICES = {
    "monolith": {"url": "http://localhost:8000", "name": "Monolith"},
    "auth": {"url": "http://localhost:8001", "name": "Auth Service"},
    "integrations": {"url": "http://localhost:8002", "name": "Integrations Service"},
    "agentkit": {"url": "http://localhost:8003", "name": "AgentKit Service"},
    "analytics": {"url": "http://localhost:8004", "name": "Analytics Service"},
    "onboarding": {"url": "http://localhost:8005", "name": "Onboarding Service"},
    "ml": {"url": "http://localhost:8006", "name": "ML Service"},
    "infrastructure": {"url": "http://localhost:8007", "name": "Infrastructure Service"},
}

async def check_service_health(service_name: str, url: str) -> Dict[str, any]:
    """Check if a service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "data": response.json()
                }
            else:
                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
    except httpx.ConnectError:
        return {
            "service": service_name,
            "status": "not_running",
            "error": "Connection refused"
        }
    except Exception as e:
        return {
            "service": service_name,
            "status": "error",
            "error": str(e)
        }

async def test_all_services() -> List[Dict[str, any]]:
    """Test all services"""
    print("🧪 Testing Hybrid Deployment...\n")
    
    results = []
    for service_name, config in SERVICES.items():
        print(f"Checking {config['name']}...", end=" ")
        result = await check_service_health(service_name, config["url"])
        results.append(result)
        
        if result["status"] == "healthy":
            print("✅")
        elif result["status"] == "not_running":
            print("⚠️  Not running")
        else:
            print(f"❌ {result.get('error', 'Unknown error')}")
    
    return results

def print_summary(results: List[Dict[str, any]]):
    """Print test summary"""
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    healthy = [r for r in results if r["status"] == "healthy"]
    not_running = [r for r in results if r["status"] == "not_running"]
    unhealthy = [r for r in results if r["status"] in ["unhealthy", "error"]]
    
    print(f"\n✅ Healthy: {len(healthy)}")
    for r in healthy:
        print(f"   - {r['service']}")
    
    if not_running:
        print(f"\n⚠️  Not Running: {len(not_running)}")
        for r in not_running:
            print(f"   - {r['service']}")
    
    if unhealthy:
        print(f"\n❌ Unhealthy: {len(unhealthy)}")
        for r in unhealthy:
            print(f"   - {r['service']}: {r.get('error', 'Unknown')}")
    
    print("\n" + "="*50)
    
    if len(healthy) > 0:
        print("✅ At least one service is running!")
        if len(healthy) == len(results):
            print("🎉 All services are healthy!")
        else:
            print("💡 Some services are not running (this is OK for partial deployments)")
    else:
        print("❌ No services are running!")
        print("💡 Start services with:")
        print("   docker-compose -f ops/docker/docker-compose.monolith.yml up")
        print("   OR")
        print("   docker-compose -f ops/docker/docker-compose.microservices.yml up")

async def main():
    """Main test function"""
    results = await test_all_services()
    print_summary(results)
    
    # Exit with error if no services are healthy
    healthy_count = len([r for r in results if r["status"] == "healthy"])
    if healthy_count == 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

