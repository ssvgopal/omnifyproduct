"""
Comprehensive End-to-End Tests for OmniFy Cloud Connect
Tests complete user journeys and system integration
"""

import pytest
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import test_client, test_db, test_user_token
from backend.models.user_models import User
from backend.models.agentkit_models import Agent, Workflow
from backend.models.analytics_models import AnalyticsData
from backend.models.brain_models import BrainModuleData

class TestEndToEndUserJourneys:
    """End-to-end tests for complete user journeys"""
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_journey(self, test_client, test_user_token):
        """Test complete user onboarding journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: User registration and login
        login_response = await test_client.post("/auth/login", json={
            "email": "test@omnify.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        
        # Step 2: Complete magical onboarding wizard
        onboarding_response = await test_client.post("/onboarding/start", 
            headers=headers,
            json={
                "user_role": "CMO",
                "company_size": "50-200",
                "industry": "SaaS",
                "primary_goals": ["lead_generation", "brand_awareness"]
            }
        )
        assert onboarding_response.status_code == 200
        onboarding_data = onboarding_response.json()
        assert onboarding_data["step"] == 1
        
        # Complete all onboarding steps
        for step in range(2, 9):
            step_response = await test_client.post(f"/onboarding/step/{step}", 
                headers=headers,
                json={"completed": True}
            )
            assert step_response.status_code == 200
        
        # Step 3: Verify onboarding completion
        completion_response = await test_client.get("/onboarding/status", headers=headers)
        assert completion_response.status_code == 200
        completion_data = completion_response.json()
        assert completion_data["completed"] == True
        assert completion_data["achievements"] is not None
    
    @pytest.mark.asyncio
    async def test_campaign_creation_and_management_journey(self, test_client, test_user_token):
        """Test complete campaign creation and management journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: Create a new campaign
        campaign_data = {
            "name": "Test Campaign E2E",
            "platform": "google_ads",
            "objective": "lead_generation",
            "budget": 1000.0,
            "target_audience": {
                "age_range": "25-45",
                "interests": ["technology", "business"]
            },
            "creative_assets": {
                "headlines": ["Test Headline 1", "Test Headline 2"],
                "descriptions": ["Test Description 1", "Test Description 2"]
            }
        }
        
        campaign_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=campaign_data
        )
        assert campaign_response.status_code == 201
        campaign_result = campaign_response.json()
        campaign_id = campaign_result["campaign_id"]
        
        # Step 2: Verify campaign creation
        get_campaign_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
        assert get_campaign_response.status_code == 200
        campaign = get_campaign_response.json()
        assert campaign["name"] == "Test Campaign E2E"
        assert campaign["status"] == "active"
        
        # Step 3: Create ads for the campaign
        ad_data = {
            "campaign_id": campaign_id,
            "name": "Test Ad E2E",
            "format": "text_ad",
            "creative": {
                "headline": "Test Headline",
                "description": "Test Description",
                "landing_page_url": "https://example.com"
            }
        }
        
        ad_response = await test_client.post("/ads/create", 
            headers=headers,
            json=ad_data
        )
        assert ad_response.status_code == 201
        ad_result = ad_response.json()
        ad_id = ad_result["ad_id"]
        
        # Step 4: Monitor campaign performance
        performance_response = await test_client.get(f"/campaigns/{campaign_id}/performance", 
            headers=headers,
            params={"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        assert performance_response.status_code == 200
        performance = performance_response.json()
        assert "impressions" in performance
        assert "clicks" in performance
        assert "spend" in performance
        
        # Step 5: Optimize campaign based on performance
        optimization_response = await test_client.post(f"/campaigns/{campaign_id}/optimize", 
            headers=headers,
            json={"optimization_type": "bid_adjustment"}
        )
        assert optimization_response.status_code == 200
        optimization = optimization_response.json()
        assert "recommendations" in optimization
        
        # Step 6: Pause campaign
        pause_response = await test_client.post(f"/campaigns/{campaign_id}/pause", headers=headers)
        assert pause_response.status_code == 200
        
        # Verify campaign is paused
        get_campaign_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
        assert get_campaign_response.status_code == 200
        campaign = get_campaign_response.json()
        assert campaign["status"] == "paused"
    
    @pytest.mark.asyncio
    async def test_ai_agent_workflow_journey(self, test_client, test_user_token):
        """Test complete AI agent workflow journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: Create an AI agent
        agent_data = {
            "name": "Test AI Agent E2E",
            "type": "creative_agent",
            "capabilities": ["content_generation", "optimization"],
            "prompt_template": "You are a creative AI agent for marketing campaigns.",
            "model": "gpt-4o",
            "temperature": 0.7
        }
        
        agent_response = await test_client.post("/agents/create", 
            headers=headers,
            json=agent_data
        )
        assert agent_response.status_code == 201
        agent_result = agent_response.json()
        agent_id = agent_result["agent_id"]
        
        # Step 2: Create a workflow using the agent
        workflow_data = {
            "name": "Test Workflow E2E",
            "description": "End-to-end test workflow",
            "steps": [
                {
                    "step_id": 1,
                    "agent_id": agent_id,
                    "action": "generate_content",
                    "input_data": {"topic": "test marketing content"},
                    "dependencies": []
                },
                {
                    "step_id": 2,
                    "agent_id": agent_id,
                    "action": "optimize_content",
                    "input_data": {"optimization_type": "seo"},
                    "dependencies": [1]
                }
            ]
        }
        
        workflow_response = await test_client.post("/workflows/create", 
            headers=headers,
            json=workflow_data
        )
        assert workflow_response.status_code == 201
        workflow_result = workflow_response.json()
        workflow_id = workflow_result["workflow_id"]
        
        # Step 3: Execute the workflow
        execution_response = await test_client.post(f"/workflows/{workflow_id}/execute", 
            headers=headers,
            json={"input_data": {"test": "data"}}
        )
        assert execution_response.status_code == 200
        execution_result = execution_response.json()
        execution_id = execution_result["execution_id"]
        
        # Step 4: Monitor workflow execution
        status_response = await test_client.get(f"/workflows/{workflow_id}/executions/{execution_id}/status", 
            headers=headers
        )
        assert status_response.status_code == 200
        status = status_response.json()
        assert "status" in status
        assert "progress" in status
        
        # Step 5: Get workflow results
        results_response = await test_client.get(f"/workflows/{workflow_id}/executions/{execution_id}/results", 
            headers=headers
        )
        assert results_response.status_code == 200
        results = results_response.json()
        assert "outputs" in results
        assert "execution_time" in results
    
    @pytest.mark.asyncio
    async def test_analytics_and_reporting_journey(self, test_client, test_user_token):
        """Test complete analytics and reporting journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: Generate analytics data
        analytics_data = {
            "platform": "google_ads",
            "metrics": ["impressions", "clicks", "conversions", "spend"],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "breakdown": ["campaign", "ad_group"]
        }
        
        analytics_response = await test_client.post("/analytics/generate", 
            headers=headers,
            json=analytics_data
        )
        assert analytics_response.status_code == 200
        analytics_result = analytics_response.json()
        report_id = analytics_result["report_id"]
        
        # Step 2: Get analytics report
        report_response = await test_client.get(f"/analytics/reports/{report_id}", headers=headers)
        assert report_response.status_code == 200
        report = report_response.json()
        assert "data" in report
        assert "summary" in report
        
        # Step 3: Create custom dashboard
        dashboard_data = {
            "name": "Test Dashboard E2E",
            "description": "End-to-end test dashboard",
            "widgets": [
                {
                    "type": "line_chart",
                    "title": "Performance Over Time",
                    "data_source": report_id,
                    "metrics": ["impressions", "clicks"]
                },
                {
                    "type": "pie_chart",
                    "title": "Campaign Breakdown",
                    "data_source": report_id,
                    "metrics": ["spend"]
                }
            ]
        }
        
        dashboard_response = await test_client.post("/analytics/dashboards/create", 
            headers=headers,
            json=dashboard_data
        )
        assert dashboard_response.status_code == 201
        dashboard_result = dashboard_response.json()
        dashboard_id = dashboard_result["dashboard_id"]
        
        # Step 4: Get dashboard
        get_dashboard_response = await test_client.get(f"/analytics/dashboards/{dashboard_id}", headers=headers)
        assert get_dashboard_response.status_code == 200
        dashboard = get_dashboard_response.json()
        assert dashboard["name"] == "Test Dashboard E2E"
        assert len(dashboard["widgets"]) == 2
        
        # Step 5: Export dashboard as PDF
        export_response = await test_client.post(f"/analytics/dashboards/{dashboard_id}/export", 
            headers=headers,
            json={"format": "pdf"}
        )
        assert export_response.status_code == 200
        export_result = export_response.json()
        assert "download_url" in export_result
    
    @pytest.mark.asyncio
    async def test_multi_platform_integration_journey(self, test_client, test_user_token):
        """Test multi-platform integration journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: Set up multiple platform integrations
        platforms = ["google_ads", "meta_ads", "linkedin_ads"]
        
        for platform in platforms:
            integration_data = {
                "platform": platform,
                "credentials": {
                    "api_key": f"test_{platform}_key",
                    "account_id": f"test_{platform}_account"
                }
            }
            
            integration_response = await test_client.post("/integrations/setup", 
                headers=headers,
                json=integration_data
            )
            assert integration_response.status_code == 201
        
        # Step 2: Test cross-platform campaign creation
        cross_platform_campaign = {
            "name": "Cross-Platform Test Campaign",
            "platforms": platforms,
            "objective": "brand_awareness",
            "budget": 3000.0,
            "budget_allocation": {
                "google_ads": 1000.0,
                "meta_ads": 1000.0,
                "linkedin_ads": 1000.0
            }
        }
        
        campaign_response = await test_client.post("/campaigns/cross-platform/create", 
            headers=headers,
            json=cross_platform_campaign
        )
        assert campaign_response.status_code == 201
        campaign_result = campaign_response.json()
        campaign_id = campaign_result["campaign_id"]
        
        # Step 3: Get cross-platform performance
        performance_response = await test_client.get(f"/campaigns/{campaign_id}/cross-platform-performance", 
            headers=headers,
            params={"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        assert performance_response.status_code == 200
        performance = performance_response.json()
        
        for platform in platforms:
            assert platform in performance
            assert "impressions" in performance[platform]
            assert "clicks" in performance[platform]
            assert "spend" in performance[platform]
        
        # Step 4: Cross-platform optimization
        optimization_response = await test_client.post(f"/campaigns/{campaign_id}/cross-platform-optimize", 
            headers=headers,
            json={"optimization_type": "budget_reallocation"}
        )
        assert optimization_response.status_code == 200
        optimization = optimization_response.json()
        assert "recommendations" in optimization
        assert "budget_adjustments" in optimization
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery_journey(self, test_client, test_user_token):
        """Test error handling and recovery journey"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Step 1: Test invalid campaign creation
        invalid_campaign_data = {
            "name": "",  # Invalid empty name
            "platform": "invalid_platform",
            "budget": -100  # Invalid negative budget
        }
        
        invalid_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=invalid_campaign_data
        )
        assert invalid_response.status_code == 422
        error_data = invalid_response.json()
        assert "detail" in error_data
        
        # Step 2: Test non-existent resource access
        not_found_response = await test_client.get("/campaigns/non-existent-id", headers=headers)
        assert not_found_response.status_code == 404
        
        # Step 3: Test rate limiting
        # Make multiple rapid requests to trigger rate limiting
        for i in range(10):
            rate_limit_response = await test_client.get("/campaigns", headers=headers)
            if rate_limit_response.status_code == 429:
                break
        
        # Step 4: Test authentication failure
        invalid_token_headers = {"Authorization": "Bearer invalid_token"}
        auth_failure_response = await test_client.get("/campaigns", headers=invalid_token_headers)
        assert auth_failure_response.status_code == 401
        
        # Step 5: Test system recovery after errors
        # Create a valid campaign after errors
        valid_campaign_data = {
            "name": "Recovery Test Campaign",
            "platform": "google_ads",
            "objective": "lead_generation",
            "budget": 1000.0
        }
        
        recovery_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=valid_campaign_data
        )
        assert recovery_response.status_code == 201
        recovery_result = recovery_response.json()
        assert "campaign_id" in recovery_result

class TestSystemIntegration:
    """System integration tests"""
    
    @pytest.mark.asyncio
    async def test_database_integration(self, test_client, test_user_token):
        """Test database integration and data persistence"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create test data
        test_data = {
            "name": "Database Integration Test",
            "type": "test",
            "data": {"key": "value", "number": 123}
        }
        
        create_response = await test_client.post("/test/data", 
            headers=headers,
            json=test_data
        )
        assert create_response.status_code == 201
        create_result = create_response.json()
        data_id = create_result["id"]
        
        # Verify data persistence
        get_response = await test_client.get(f"/test/data/{data_id}", headers=headers)
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        assert retrieved_data["name"] == "Database Integration Test"
        assert retrieved_data["data"]["key"] == "value"
        assert retrieved_data["data"]["number"] == 123
        
        # Update data
        update_data = {
            "name": "Updated Database Integration Test",
            "data": {"key": "updated_value", "number": 456}
        }
        
        update_response = await test_client.put(f"/test/data/{data_id}", 
            headers=headers,
            json=update_data
        )
        assert update_response.status_code == 200
        
        # Verify update
        get_updated_response = await test_client.get(f"/test/data/{data_id}", headers=headers)
        assert get_updated_response.status_code == 200
        updated_data = get_updated_response.json()
        assert updated_data["name"] == "Updated Database Integration Test"
        assert updated_data["data"]["key"] == "updated_value"
        assert updated_data["data"]["number"] == 456
        
        # Delete data
        delete_response = await test_client.delete(f"/test/data/{data_id}", headers=headers)
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = await test_client.get(f"/test/data/{data_id}", headers=headers)
        assert get_deleted_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_external_api_integration(self, test_client, test_user_token):
        """Test external API integration"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test platform integration
        platform_data = {
            "platform": "google_ads",
            "action": "get_campaigns",
            "params": {"account_id": "test_account"}
        }
        
        platform_response = await test_client.post("/integrations/execute", 
            headers=headers,
            json=platform_data
        )
        assert platform_response.status_code == 200
        platform_result = platform_response.json()
        assert "status" in platform_result
        assert "data" in platform_result
    
    @pytest.mark.asyncio
    async def test_background_job_processing(self, test_client, test_user_token):
        """Test background job processing"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Submit background job
        job_data = {
            "job_type": "analytics_processing",
            "parameters": {
                "platform": "google_ads",
                "date_range": "2024-01-01,2024-01-31"
            }
        }
        
        job_response = await test_client.post("/jobs/submit", 
            headers=headers,
            json=job_data
        )
        assert job_response.status_code == 202
        job_result = job_response.json()
        job_id = job_result["job_id"]
        
        # Check job status
        status_response = await test_client.get(f"/jobs/{job_id}/status", headers=headers)
        assert status_response.status_code == 200
        status = status_response.json()
        assert "status" in status
        assert status["status"] in ["pending", "running", "completed", "failed"]
        
        # Wait for job completion (with timeout)
        max_wait_time = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_response = await test_client.get(f"/jobs/{job_id}/status", headers=headers)
            status = status_response.json()
            
            if status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
        
        # Verify job completion
        final_status_response = await test_client.get(f"/jobs/{job_id}/status", headers=headers)
        final_status = final_status_response.json()
        assert final_status["status"] in ["completed", "failed"]
        
        if final_status["status"] == "completed":
            # Get job results
            results_response = await test_client.get(f"/jobs/{job_id}/results", headers=headers)
            assert results_response.status_code == 200
            results = results_response.json()
            assert "output" in results

class TestDataConsistency:
    """Data consistency tests"""
    
    @pytest.mark.asyncio
    async def test_cross_module_data_consistency(self, test_client, test_user_token):
        """Test data consistency across modules"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create campaign
        campaign_data = {
            "name": "Consistency Test Campaign",
            "platform": "google_ads",
            "budget": 1000.0
        }
        
        campaign_response = await test_client.post("/campaigns/create", 
            headers=headers,
            json=campaign_data
        )
        campaign_id = campaign_response.json()["campaign_id"]
        
        # Create analytics data for the campaign
        analytics_data = {
            "campaign_id": campaign_id,
            "platform": "google_ads",
            "metrics": {
                "impressions": 10000,
                "clicks": 500,
                "conversions": 50,
                "spend": 200.0
            }
        }
        
        analytics_response = await test_client.post("/analytics/data", 
            headers=headers,
            json=analytics_data
        )
        assert analytics_response.status_code == 201
        
        # Verify data consistency across modules
        campaign_response = await test_client.get(f"/campaigns/{campaign_id}", headers=headers)
        campaign = campaign_response.json()
        
        analytics_response = await test_client.get(f"/analytics/campaigns/{campaign_id}", headers=headers)
        analytics = analytics_response.json()
        
        # Verify campaign ID consistency
        assert campaign["campaign_id"] == campaign_id
        assert analytics["campaign_id"] == campaign_id
        
        # Verify budget consistency
        assert campaign["budget"] == 1000.0
        assert analytics["metrics"]["spend"] <= campaign["budget"]
    
    @pytest.mark.asyncio
    async def test_concurrent_data_modification(self, test_client, test_user_token):
        """Test concurrent data modification handling"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create test resource
        resource_data = {"name": "Concurrent Test Resource", "value": 0}
        create_response = await test_client.post("/test/concurrent-resource", 
            headers=headers,
            json=resource_data
        )
        resource_id = create_response.json()["id"]
        
        # Simulate concurrent modifications
        async def modify_resource(increment):
            update_data = {"value": increment}
            response = await test_client.put(f"/test/concurrent-resource/{resource_id}", 
                headers=headers,
                json=update_data
            )
            return response.status_code == 200
        
        # Run concurrent modifications
        tasks = [modify_resource(i) for i in range(1, 6)]
        results = await asyncio.gather(*tasks)
        
        # Verify all modifications succeeded
        assert all(results)
        
        # Verify final state
        final_response = await test_client.get(f"/test/concurrent-resource/{resource_id}", headers=headers)
        final_data = final_response.json()
        assert "value" in final_data
        assert final_data["value"] >= 0  # Should be non-negative

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
