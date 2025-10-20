"""
Integration Tests for OmniFy Backend API
Tests API endpoints and database integration
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid

# Import the FastAPI app
from agentkit_server import app
from database.mongodb import get_database

class TestAPIIntegration:
    """Integration tests for API endpoints"""

@pytest.fixture
    def client(self):
    """Create test client"""
        return TestClient(app)

@pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

@pytest.fixture
    async def test_db(self):
        """Create test database connection"""
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.test_omnify
        yield db
        # Cleanup
        await db.drop_collection("test_collection")
        client.close()
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_agentkit_endpoints(self, async_client):
        """Test AgentKit API endpoints"""
        # Test create agent
        agent_data = {
            "name": "test-agent",
            "description": "Test agent for integration testing",
            "agent_type": "workflow",
            "config": {"test": "config"}
        }
        
        response = await async_client.post("/api/agentkit/agents", json=agent_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "agent_id" in data

        agent_id = data["agent_id"]

        # Test get agent
        response = await async_client.get(f"/api/agentkit/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["agent"]["name"] == "test-agent"
        
        # Test execute agent
        execution_data = {
            "input_data": {"test": "input"},
            "context": {"user_id": "test-user"}
        }
        
        response = await async_client.post(f"/api/agentkit/agents/{agent_id}/execute", json=execution_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "execution_id" in data

    @pytest.mark.asyncio
    async def test_proactive_intelligence_endpoints(self, async_client):
        """Test Proactive Intelligence API endpoints"""
        client_id = "test-client-123"
        
        # Test get client preference
        response = await async_client.get(f"/api/proactive-intelligence/preference/{client_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert "preference_level" in data
        
        # Test generate proactive action
        action_data = {
            "action_type": "creative_fatigue",
            "context": {"campaign_id": "test-campaign"}
        }
        
        response = await async_client.post(f"/api/proactive-intelligence/actions/{client_id}", json=action_data)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert data["action_type"] == "creative_fatigue"
        assert "confidence_score" in data

    @pytest.mark.asyncio
    async def test_onboarding_endpoints(self, async_client):
        """Test Onboarding API endpoints"""
        user_id = "test-user-123"
        
        # Test start onboarding
        onboarding_data = {
            "role": "cmo",
            "company_name": "Test Company"
        }
        
        response = await async_client.post(f"/api/onboarding/start/{user_id}", json=onboarding_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["role"] == "cmo"
        assert data["status"] == "in_progress"
        
        session_id = data["session_id"]
        
        # Test complete step
        step_data = {
            "step_number": 1,
            "step_data": {"company_name": "Test Company"}
        }
        
        response = await async_client.post(f"/api/onboarding/sessions/{session_id}/complete-step", json=step_data)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "in_progress"
        
        # Test get next step
        response = await async_client.get(f"/api/onboarding/sessions/{session_id}/next-step")
        assert response.status_code == 200
        data = response.json()
        assert data["step_number"] == 2
        assert "step_title" in data

    @pytest.mark.asyncio
    async def test_instant_value_endpoints(self, async_client):
        """Test Instant Value Delivery API endpoints"""
        client_id = "test-client-123"
        
        # Test identify quick wins
        response = await async_client.get(f"/api/instant-value/quick-wins/{client_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert "quick_wins" in data
        assert len(data["quick_wins"]) > 0
        
        # Test implement optimization
        optimization_data = {
            "optimization_type": "bid_optimization",
            "platform": "google_ads",
            "parameters": {"bid_multiplier": 1.2}
        }
        
        response = await async_client.post(f"/api/instant-value/optimizations/{client_id}", json=optimization_data)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert data["optimization_type"] == "bid_optimization"
        assert data["status"] == "implemented"

    @pytest.mark.asyncio
    async def test_predictive_intelligence_endpoints(self, async_client):
        """Test Predictive Intelligence API endpoints"""
        client_id = "test-client-123"
        
        # Test get predictions
        response = await async_client.get(f"/api/predictive/predictions?client_id={client_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for prediction in data:
            assert "type" in prediction
            assert "confidence" in prediction
            assert "value" in prediction
        
        # Test get trends
        response = await async_client.get(f"/api/predictive/trends?client_id={client_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for trend in data:
            assert "metric" in trend
            assert "direction" in trend
            assert "strength" in trend
        
        # Test get opportunities
        response = await async_client.get(f"/api/predictive/opportunities?client_id={client_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for opportunity in data:
            assert "type" in opportunity
            assert "potential_value" in opportunity
            assert "urgency" in opportunity

    @pytest.mark.asyncio
    async def test_adaptive_learning_endpoints(self, async_client):
        """Test Adaptive Learning API endpoints"""
        client_id = "test-client-123"
        
        # Test analyze behavior
        behavior_data = {
            "interactions": 50,
            "response_time": 2.5,
            "preferred_channels": ["email", "dashboard"],
            "decision_style": "analytical"
        }
        
        response = await async_client.post(f"/api/adaptive-learning/behavior/{client_id}", json=behavior_data)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert "personality_type" in data
        assert "learning_style" in data
        
        # Test get recommendations
        response = await async_client.get(f"/api/adaptive-learning/recommendations/{client_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_expert_intervention_endpoints(self, async_client):
        """Test Expert Intervention API endpoints"""
        client_id = "test-client-123"
        
        # Test request intervention
        intervention_data = {
            "intervention_type": "budget_allocation",
            "urgency": "high",
            "context": {"budget": 50000, "campaigns": 5}
        }
        
        response = await async_client.post(f"/api/expert-intervention/request/{client_id}", json=intervention_data)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert data["intervention_type"] == "budget_allocation"
        assert "intervention_id" in data
        assert "assigned_expert" in data
        
        intervention_id = data["intervention_id"]
        
        # Test get intervention status
        response = await async_client.get(f"/api/expert-intervention/interventions/{intervention_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["intervention_id"] == intervention_id
        assert "status" in data
        assert "assigned_expert" in data

    @pytest.mark.asyncio
    async def test_critical_decision_endpoints(self, async_client):
        """Test Critical Decision API endpoints"""
        client_id = "test-client-123"
        
        # Test start decision process
        decision_data = {
            "decision_type": "budget_allocation",
            "context": {"total_budget": 100000, "campaigns": 3}
        }
        
        response = await async_client.post(f"/api/critical-decision/start/{client_id}", json=decision_data)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert data["decision_type"] == "budget_allocation"
        assert data["status"] == "in_progress"
        assert "decision_id" in data

        decision_id = data["decision_id"]

        # Test get guidance
        response = await async_client.get(f"/api/critical-decision/guidance/{decision_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == decision_id
        assert "guidance" in data
        assert "questions" in data
        assert "checklist" in data
        
        # Test make decision
        decision_result = {
            "decision_data": {"allocated_budget": 60000, "reasoning": "Focus on top performers"},
            "confidence": 0.8
        }
        
        response = await async_client.post(f"/api/critical-decision/decide/{decision_id}", json=decision_result)
        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == decision_id
        assert data["status"] == "decision_made"
        assert "recommendations" in data

class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    @pytest.fixture
    async def test_db(self):
        """Create test database connection"""
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.test_omnify
        yield db
        # Cleanup
        await db.drop_collection("test_collection")
        client.close()

    @pytest.mark.asyncio
    async def test_client_profile_crud(self, test_db):
        """Test client profile CRUD operations"""
        collection = test_db.client_profiles
        
        # Create client profile
        profile_data = {
            "client_id": "test-client-123",
            "name": "Test Client",
            "email": "test@example.com",
            "company": "Test Company",
            "industry": "technology",
            "budget": 50000,
            "goals": ["increase_conversions", "reduce_cpa"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(profile_data)
        assert result.inserted_id is not None
        
        # Read client profile
        profile = await collection.find_one({"client_id": "test-client-123"})
        assert profile is not None
        assert profile["name"] == "Test Client"
        assert profile["email"] == "test@example.com"
        
        # Update client profile
        update_data = {"budget": 75000, "updated_at": datetime.utcnow()}
        result = await collection.update_one(
            {"client_id": "test-client-123"},
            {"$set": update_data}
        )
        assert result.modified_count == 1
        
        # Verify update
        updated_profile = await collection.find_one({"client_id": "test-client-123"})
        assert updated_profile["budget"] == 75000
        
        # Delete client profile
        result = await collection.delete_one({"client_id": "test-client-123"})
        assert result.deleted_count == 1
        
        # Verify deletion
        deleted_profile = await collection.find_one({"client_id": "test-client-123"})
        assert deleted_profile is None

    @pytest.mark.asyncio
    async def test_campaign_data_crud(self, test_db):
        """Test campaign data CRUD operations"""
        collection = test_db.campaigns
        
        # Create campaign
        campaign_data = {
            "campaign_id": "test-campaign-123",
            "name": "Test Campaign",
            "platform": "google_ads",
            "budget": 10000,
            "status": "active",
            "target_audience": "tech_professionals",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(campaign_data)
        assert result.inserted_id is not None
        
        # Read campaign
        campaign = await collection.find_one({"campaign_id": "test-campaign-123"})
        assert campaign is not None
        assert campaign["name"] == "Test Campaign"
        assert campaign["platform"] == "google_ads"
        
        # Update campaign
        update_data = {"budget": 15000, "updated_at": datetime.utcnow()}
        result = await collection.update_one(
            {"campaign_id": "test-campaign-123"},
            {"$set": update_data}
        )
        assert result.modified_count == 1
        
        # Verify update
        updated_campaign = await collection.find_one({"campaign_id": "test-campaign-123"})
        assert updated_campaign["budget"] == 15000
        
        # Delete campaign
        result = await collection.delete_one({"campaign_id": "test-campaign-123"})
        assert result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_performance_metrics_crud(self, test_db):
        """Test performance metrics CRUD operations"""
        collection = test_db.performance_metrics
        
        # Create performance metrics
        metrics_data = {
            "campaign_id": "test-campaign-123",
            "date": datetime.utcnow(),
            "impressions": 10000,
            "clicks": 500,
            "conversions": 25,
            "cost": 1000.00,
            "cpa": 40.00,
            "roas": 2.5,
            "ctr": 5.0,
            "conversion_rate": 5.0,
            "created_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(metrics_data)
        assert result.inserted_id is not None
        
        # Read performance metrics
        metrics = await collection.find_one({"campaign_id": "test-campaign-123"})
        assert metrics is not None
        assert metrics["impressions"] == 10000
        assert metrics["clicks"] == 500
        assert metrics["conversions"] == 25
        
        # Update performance metrics
        update_data = {"impressions": 12000, "clicks": 600}
        result = await collection.update_one(
            {"campaign_id": "test-campaign-123"},
            {"$set": update_data}
        )
        assert result.modified_count == 1
        
        # Verify update
        updated_metrics = await collection.find_one({"campaign_id": "test-campaign-123"})
        assert updated_metrics["impressions"] == 12000
        assert updated_metrics["clicks"] == 600
        
        # Delete performance metrics
        result = await collection.delete_one({"campaign_id": "test-campaign-123"})
        assert result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_aggregation_queries(self, test_db):
        """Test aggregation queries"""
        collection = test_db.performance_metrics
        
        # Insert test data
        test_data = [
            {
                "campaign_id": "campaign-1",
                "date": datetime.utcnow(),
                "impressions": 10000,
                "clicks": 500,
                "conversions": 25,
                "cost": 1000.00,
                "platform": "google_ads"
            },
            {
                "campaign_id": "campaign-2",
                "date": datetime.utcnow(),
                "impressions": 15000,
                "clicks": 750,
                "conversions": 30,
                "cost": 1500.00,
                "platform": "meta_ads"
            },
            {
                "campaign_id": "campaign-3",
                "date": datetime.utcnow(),
                "impressions": 8000,
                "clicks": 400,
                "conversions": 20,
                "cost": 800.00,
                "platform": "google_ads"
            }
        ]
        
        await collection.insert_many(test_data)
        
        # Test aggregation pipeline
        pipeline = [
            {"$group": {
                "_id": "$platform",
                "total_impressions": {"$sum": "$impressions"},
                "total_clicks": {"$sum": "$clicks"},
                "total_conversions": {"$sum": "$conversions"},
                "total_cost": {"$sum": "$cost"},
                "avg_ctr": {"$avg": {"$divide": ["$clicks", "$impressions"]}}
            }},
            {"$sort": {"total_cost": -1}}
        ]
        
        results = await collection.aggregate(pipeline).to_list(length=None)
        
        assert len(results) == 2  # Two platforms
        assert results[0]["_id"] == "meta_ads"  # Highest cost
        assert results[1]["_id"] == "google_ads"
        
        # Verify aggregation results
        meta_ads_result = next(r for r in results if r["_id"] == "meta_ads")
        assert meta_ads_result["total_impressions"] == 15000
        assert meta_ads_result["total_clicks"] == 750
        assert meta_ads_result["total_conversions"] == 30
        assert meta_ads_result["total_cost"] == 1500.00
        
        google_ads_result = next(r for r in results if r["_id"] == "google_ads")
        assert google_ads_result["total_impressions"] == 18000
        assert google_ads_result["total_clicks"] == 900
        assert google_ads_result["total_conversions"] == 45
        assert google_ads_result["total_cost"] == 1800.00

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test invalid JSON returns 422"""
        response = client.post("/api/agentkit/agents", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test missing required fields returns 422"""
        response = client.post("/api/agentkit/agents", json={"name": "test"})
        assert response.status_code == 422
    
    def test_invalid_uuid(self, client):
        """Test invalid UUID returns 422"""
        response = client.get("/api/agentkit/agents/invalid-uuid")
        assert response.status_code == 422
    
    def test_rate_limiting(self, client):
        """Test rate limiting"""
        # Make multiple requests quickly
        for _ in range(100):
            response = client.get("/health")
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        assert response.status_code == 429

class TestAuthentication:
    """Test authentication and authorization"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_protected_endpoint_without_auth(self, client):
        """Test protected endpoint without authentication"""
        response = client.get("/api/admin/users")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, client):
        """Test protected endpoint with valid token"""
        # This would need a valid JWT token
        # For now, just test the structure
        headers = {"Authorization": "Bearer valid-token"}
        response = client.get("/api/admin/users", headers=headers)
        # Should return 200 or 403 (forbidden) but not 401 (unauthorized)
        assert response.status_code in [200, 403]

class TestPerformanceIntegration:
    """Test performance and load handling"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time
            })
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 10
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 1.0  # Should respond within 1 second
    
    def test_large_payload_handling(self, client):
        """Test handling large payloads"""
        large_data = {
            "name": "test-agent",
            "description": "Test agent for large payload testing",
            "agent_type": "workflow",
            "config": {
                "large_array": list(range(1000)),
                "large_string": "x" * 10000
            }
        }
        
        response = client.post("/api/agentkit/agents", json=large_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend", "--cov-report=html"])