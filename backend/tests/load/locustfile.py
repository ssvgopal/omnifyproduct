"""
Load Testing with Locust
Run with: locust -f backend/tests/load/locustfile.py
"""

from locust import HttpUser, task, between
import random


class OmnifyUser(HttpUser):
    """Simulated user for load testing"""
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login when user starts"""
        # Register or login
        self.client.post("/api/auth/login", json={
            "email": f"loadtest{random.randint(1, 1000)}@example.com",
            "password": "LoadTest123!"
        })
    
    @task(3)
    def view_dashboard(self):
        """View dashboard (most common action)"""
        self.client.get("/api/dashboard", headers={
            "Authorization": "Bearer test-token"
        })
    
    @task(2)
    def list_campaigns(self):
        """List campaigns"""
        self.client.get("/api/campaigns", headers={
            "Authorization": "Bearer test-token"
        })
    
    @task(1)
    def create_campaign(self):
        """Create campaign (less common)"""
        self.client.post("/api/campaigns", json={
            "name": f"Load Test Campaign {random.randint(1, 10000)}",
            "platform": "google_ads",
            "budget": random.randint(100, 10000)
        }, headers={
            "Authorization": "Bearer test-token"
        })
    
    @task(1)
    def get_campaign_performance(self):
        """Get campaign performance"""
        campaign_id = f"campaign_{random.randint(1, 100)}"
        self.client.get(f"/api/campaigns/{campaign_id}/performance", headers={
            "Authorization": "Bearer test-token"
        })

