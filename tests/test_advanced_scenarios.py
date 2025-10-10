"""
Advanced Backend Testing Suite for OmnifyProduct
Performance, security, and edge case testing
"""

import pytest
import asyncio
import time
import psutil
import tracemalloc
from unittest.mock import Mock, patch, AsyncMock
from motor.motor_asyncio import AsyncIOMotorClient
import os
from concurrent.futures import ThreadPoolExecutor
import gc

# Import our application
from services.agentkit_service import AgentKitService
from services.auth_service import AuthService
from services.workflow_orchestrator import WorkflowOrchestrator
from models.agentkit_models import (
    AgentConfig, WorkflowDefinition, AgentExecutionRequest,
    AgentType, WorkflowStatus
)


class TestPerformance:
    """Performance and load testing"""

    @pytest.mark.asyncio
    async def test_api_response_time(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test API endpoint response times"""
        # Test health endpoint response time
        start_time = time.time()
        response = await client.get("/health", headers=auth_headers)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response.status_code == 200
        assert response_time < 100  # Should respond within 100ms

    @pytest.mark.asyncio
    async def test_concurrent_agent_executions(self, client: AsyncClient, auth_headers: Dict[str, str], test_db: Any):
        """Test performance under concurrent load"""
        # Create test agent first
        agent_config = {
            "name": "Performance Test Agent",
            "agent_type": "creative_intelligence",
            "description": "Agent for performance testing",
            "organization_id": "test_org",
            "config": {"platforms": ["google_ads"]}
        }

        create_response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
        agent_id = create_response.json()["agent_id"]

        # Execute multiple agents concurrently
        start_time = time.time()

        tasks = []
        for i in range(50):  # 50 concurrent executions
            execution_request = {
                "input_data": {
                    "asset_url": f"https://example.com/asset_{i}.jpg",
                    "analysis_type": "aida"
                },
                "context": {"request_id": i}
            }

            task = client.post(
                f"/api/agentkit/agents/{agent_id}/execute",
                json=execution_request,
                headers=auth_headers
            )
            tasks.append(task)

        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All should succeed
        for response in responses:
            assert response.status_code == 200

        # Performance assertions
        avg_response_time = total_time / 50
        assert avg_response_time < 2.0  # Average under 2 seconds
        assert total_time < 30.0  # All 50 should complete within 30 seconds

    @pytest.mark.asyncio
    async def test_memory_usage_during_workflow_execution(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test memory usage during complex workflow execution"""
        # Start memory tracing
        tracemalloc.start()

        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create complex workflow with many steps
        workflow_data = {
            "name": "Memory Test Workflow",
            "description": "Workflow for memory testing",
            "organization_id": test_organization["organization_id"],
            "steps": []
        }

        # Add 20 steps to test memory usage
        for i in range(20):
            workflow_data["steps"].append({
                "step_id": f"step_{i}",
                "agent_type": "creative_intelligence" if i % 2 == 0 else "analytics",
                "input_mapping": {"data": f"input_{i}"},
                "output_mapping": {f"result_{i}": f"output_{i}"}
            })

        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        # Execute workflow and measure memory
        snapshot_before = tracemalloc.take_snapshot()

        execution_request = {
            "input_data": {f"input_{i}": f"test_data_{i}" for i in range(20)}
        }

        response = await service.execute_workflow(
            workflow_id=workflow_data["workflow_id"],
            input_data=execution_request,
            user_id="test_user",
            organization_id=test_organization["organization_id"]
        )

        snapshot_after = tracemalloc.take_snapshot()

        # Calculate memory usage
        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        total_memory_increase = sum(stat.size_diff for stat in stats)

        # Memory usage should be reasonable (< 50MB increase)
        assert total_memory_increase < 50 * 1024 * 1024  # 50MB

        # Clean up
        tracemalloc.stop()

    @pytest.mark.asyncio
    async def test_database_query_performance(self, test_db: Any):
        """Test database query performance with large datasets"""
        # Insert large dataset
        agents_data = []
        for i in range(1000):
            agents_data.append({
                "agent_id": f"perf_agent_{i}",
                "organization_id": "test_org",
                "name": f"Performance Agent {i}",
                "agent_type": "creative_intelligence",
                "is_active": True
            })

        await test_db.agentkit_agents.insert_many(agents_data)

        # Test query performance
        start_time = time.time()

        # Query with filtering and sorting
        agents = await test_db.agentkit_agents.find(
            {"organization_id": "test_org", "is_active": True}
        ).sort("name", 1).limit(100).to_list(None)

        end_time = time.time()
        query_time = end_time - start_time

        assert len(agents) == 100
        assert query_time < 0.5  # Should complete within 500ms

    @pytest.mark.asyncio
    async def test_workflow_execution_under_load(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test workflow execution performance under concurrent load"""
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create test workflow
        workflow_data = {
            "name": "Load Test Workflow",
            "description": "Workflow for load testing",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "analysis",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"asset_url": "test_url"},
                    "output_mapping": {"result": "analysis_result"}
                }
            ]
        }

        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        # Execute multiple workflows concurrently
        start_time = time.time()

        tasks = []
        for i in range(20):  # 20 concurrent workflows
            task = service.execute_workflow(
                workflow_id=workflow_data["workflow_id"],
                input_data={"test_url": f"https://example.com/test_{i}.jpg"},
                user_id="test_user",
                organization_id=test_organization["organization_id"]
            )
            tasks.append(task)

        # Wait for all workflows to complete
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All should succeed
        for result in results:
            assert result.status == WorkflowStatus.COMPLETED

        # Performance assertions
        assert total_time < 60.0  # All workflows should complete within 60 seconds
        assert len(results) == 20


class TestSecurity:
    """Comprehensive security testing"""

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test SQL injection prevention"""
        # Try various SQL injection payloads
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; UPDATE users SET password='hacked'; --",
            "1; SELECT * FROM users WHERE '1'='1"
        ]

        for payload in malicious_inputs:
            response = await client.post(
                "/api/agentkit/agents",
                json={
                    "name": payload,
                    "agent_type": "creative_intelligence",
                    "config": {}
                },
                headers=auth_headers
            )

            # Should either reject with validation error or sanitize input
            assert response.status_code in [422, 200]

            if response.status_code == 200:
                data = response.json()
                # Input should be sanitized
                assert payload not in data.get("name", "")

    @pytest.mark.asyncio
    async def test_xss_prevention(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test XSS attack prevention"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ]

        for payload in xss_payloads:
            response = await client.post(
                "/api/agentkit/agents",
                json={
                    "name": "Test Agent",
                    "agent_type": "creative_intelligence",
                    "description": payload,
                    "config": {}
                },
                headers=auth_headers
            )

            assert response.status_code in [422, 200]

            if response.status_code == 200:
                data = response.json()
                # Description should be sanitized
                assert "<script>" not in data.get("description", "")

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test rate limiting effectiveness"""
        # Make many rapid requests
        tasks = []
        for i in range(150):  # Exceed typical rate limit
            task = client.get("/health", headers=auth_headers)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Should have some rate limited responses
        status_codes = [response.status_code for response in responses]
        rate_limited_count = status_codes.count(429)  # Too Many Requests

        assert rate_limited_count > 0  # Should have some rate limiting

    @pytest.mark.asyncio
    async def test_authentication_bypass_attempts(self, client: AsyncClient):
        """Test authentication bypass prevention"""
        bypass_attempts = [
            {"Authorization": ""},  # Empty auth
            {"Authorization": "Bearer "},  # Empty token
            {"Authorization": "Bearer invalid.jwt.token"},  # Invalid token
            {"Authorization": "Basic dGVzdDp0ZXN0"},  # Wrong auth type
            {},  # Missing auth header
        ]

        for headers in bypass_attempts:
            response = await client.get("/api/agentkit/agents", headers=headers)
            assert response.status_code == 401  # Should be unauthorized

    @pytest.mark.asyncio
    async def test_input_validation_comprehensive(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test comprehensive input validation"""
        # Test oversized input
        oversized_input = "A" * 100000  # 100KB string

        response = await client.post(
            "/api/agentkit/agents",
            json={
                "name": oversized_input,
                "agent_type": "creative_intelligence",
                "config": {}
            },
            headers=auth_headers
        )

        # Should reject oversized input
        assert response.status_code == 422

        # Test malicious file upload simulation
        malicious_filename = "../../../etc/passwd"

        response = await client.post(
            "/api/agentkit/agents",
            json={
                "name": "Malicious Agent",
                "agent_type": "creative_intelligence",
                "config": {"malicious_path": malicious_filename}
            },
            headers=auth_headers
        )

        # Should sanitize or reject malicious paths
        assert response.status_code in [422, 400]


class TestEdgeCases:
    """Edge case and boundary condition testing"""

    @pytest.mark.asyncio
    async def test_maximum_workflow_steps(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test workflow with maximum allowed steps"""
        # Create workflow with maximum steps (50 steps)
        steps = []
        for i in range(50):
            steps.append({
                "step_id": f"step_{i}",
                "agent_type": "creative_intelligence",
                "input_mapping": {f"data_{i}": f"input_{i}"},
                "output_mapping": {f"result_{i}": f"output_{i}"}
            })

        workflow_data = {
            "name": "Maximum Steps Workflow",
            "description": "Workflow with maximum allowed steps",
            "organization_id": test_organization["organization_id"],
            "steps": steps
        }

        response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=auth_headers)

        # Should either accept or reject with appropriate error
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            # If accepted, should execute successfully
            workflow_id = response.json()["workflow_id"]

            execution_data = {f"input_{i}": f"test_data_{i}" for i in range(50)}
            exec_response = await client.post(
                f"/api/agentkit/workflows/{workflow_id}/execute",
                json={"input_data": execution_data},
                headers=auth_headers
            )

            # Should handle large workflow execution
            assert exec_response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_concurrent_user_sessions(self, client: AsyncClient, test_organization: Dict[str, Any]):
        """Test multiple concurrent user sessions"""
        # Simulate multiple users accessing the system simultaneously
        async def simulate_user_session(user_id: str):
            # Create auth token for user
            auth_service = AuthService(db=client._transport.app.state.db)
            token = await auth_service.generate_token(user_id, test_organization["organization_id"])
            headers = {"Authorization": f"Bearer {token}"}

            # Perform various operations
            await client.get("/api/agentkit/agents", headers=headers)
            await client.get("/api/agentkit/workflows", headers=headers)
            await client.get("/health", headers=headers)

            return True

        # Run multiple concurrent sessions
        user_ids = [f"concurrent_user_{i}" for i in range(10)]
        tasks = [simulate_user_session(user_id) for user_id in user_ids]

        results = await asyncio.gather(*tasks)

        # All sessions should complete successfully
        assert all(results)

    @pytest.mark.asyncio
    async def test_workflow_with_circular_dependencies(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test workflow with circular dependencies"""
        # Create workflow with circular dependency (Step 1 depends on Step 2, Step 2 depends on Step 1)
        workflow_data = {
            "name": "Circular Dependency Workflow",
            "description": "Workflow with circular dependencies",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "step_1",
                    "agent_type": "creative_intelligence",
                    "depends_on": ["step_2"],  # Circular dependency
                    "input_mapping": {"data": "input_1"},
                    "output_mapping": {"result": "output_1"}
                },
                {
                    "step_id": "step_2",
                    "agent_type": "analytics",
                    "depends_on": ["step_1"],  # Circular dependency
                    "input_mapping": {"data": "output_1"},
                    "output_mapping": {"result": "output_2"}
                }
            ]
        }

        response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=auth_headers)

        # Should detect and reject circular dependencies
        assert response.status_code == 422

        data = response.json()
        assert "circular dependency" in data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_agent_execution_with_invalid_input_data(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test agent execution with various invalid input scenarios"""
        # Create test agent
        agent_config = {
            "name": "Validation Test Agent",
            "agent_type": "creative_intelligence",
            "description": "Agent for input validation testing",
            "organization_id": test_organization["organization_id"],
            "config": {"platforms": ["google_ads"]}
        }

        create_response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
        agent_id = create_response.json()["agent_id"]

        # Test various invalid inputs
        invalid_inputs = [
            {"input_data": None},  # Null input
            {"input_data": {}},  # Empty input
            {"input_data": {"malformed": "data" * 10000}},  # Oversized input
            {"input_data": {"asset_url": ""}},  # Empty required field
            {"input_data": {"asset_url": "not-a-url"}},  # Invalid URL format
        ]

        for invalid_input in invalid_inputs:
            response = await client.post(
                f"/api/agentkit/agents/{agent_id}/execute",
                json=invalid_input,
                headers=auth_headers
            )

            # Should handle invalid input appropriately
            assert response.status_code in [422, 400, 200]

    @pytest.mark.asyncio
    async def test_workflow_execution_timeout(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test workflow execution timeout handling"""
        # Create workflow with very short timeout
        workflow_data = {
            "name": "Timeout Test Workflow",
            "description": "Workflow for timeout testing",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "long_running_step",
                    "agent_type": "analytics",
                    "input_mapping": {"delay": "10"},  # Simulate long execution
                    "output_mapping": {"result": "output"}
                }
            ],
            "config": {"timeout_seconds": 1}  # Very short timeout
        }

        response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=auth_headers)

        if response.status_code == 200:
            workflow_id = response.json()["workflow_id"]

            # Execute workflow that should timeout
            exec_response = await client.post(
                f"/api/agentkit/workflows/{workflow_id}/execute",
                json={"input_data": {"delay": "10"}},
                headers=auth_headers
            )

            # Should handle timeout appropriately
            assert exec_response.status_code in [200, 408, 422]

    @pytest.mark.asyncio
    async def test_database_connection_failure_recovery(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test system behavior during database failures"""
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create test agent first
        agent_config = AgentConfig(
            agent_id="db_failure_test_agent",
            organization_id=test_organization["organization_id"],
            name="DB Failure Test Agent",
            agent_type="creative_intelligence",
            description="Agent for DB failure testing",
            config={}
        )

        await service.create_agent(agent_config)

        # Simulate database connection failure
        original_db = service.db
        service.db = None  # Simulate DB connection loss

        try:
            # Try to execute agent during DB failure
            execution_request = AgentExecutionRequest(
                agent_id="db_failure_test_agent",
                input_data={"test": "data"},
                user_id="test_user",
                organization_id=test_organization["organization_id"]
            )

            # Should handle database failure gracefully
            # This would depend on error handling implementation
            response = await service.execute_agent(execution_request)

            # Should either fail gracefully or queue for retry
            assert response.status in ["failed", "queued"]

        finally:
            # Restore database connection
            service.db = original_db

    @pytest.mark.asyncio
    async def test_memory_exhaustion_scenarios(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test system behavior under memory pressure"""
        # Monitor memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create many large workflows to consume memory
        for i in range(10):
            workflow_data = {
                "name": f"Memory Test Workflow {i}",
                "description": "Workflow for memory testing",
                "organization_id": test_organization["organization_id"],
                "steps": []
            }

            # Add many steps with large data
            for j in range(10):
                workflow_data["steps"].append({
                    "step_id": f"step_{i}_{j}",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"large_data": "x" * 10000},  # 10KB per step
                    "output_mapping": {f"result_{j}": f"output_{j}"}
                })

            workflow = WorkflowDefinition(**workflow_data)
            await service.create_workflow(workflow)

        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable (< 100MB increase)
        assert memory_increase < 100 * 1024 * 1024  # 100MB

        # Force garbage collection
        gc.collect()

        # Memory should be freed after GC
        after_gc_memory = process.memory_info().rss
        assert after_gc_memory <= final_memory


class TestIntegrationWithExternalServices:
    """Test integration with external services"""

    @pytest.mark.asyncio
    async def test_agentkit_sdk_error_handling(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test AgentKit SDK error scenarios"""
        with patch('services.agentkit_sdk_client_simulation.AgentKitSDKClient') as mock_sdk:
            # Mock SDK to raise various errors
            mock_sdk_instance = Mock()
            mock_sdk.return_value = mock_sdk_instance

            # Test SDK connection error
            mock_sdk_instance.create_agent.side_effect = Exception("SDK Connection Error")

            service = AgentKitService(db=test_db, agentkit_api_key="test-key")

            agent_config = AgentConfig(
                agent_id="sdk_error_test",
                organization_id=test_organization["organization_id"],
                name="SDK Error Test Agent",
                agent_type="creative_intelligence",
                description="Agent for SDK error testing",
                config={}
            )

            # Should handle SDK errors gracefully
            result = await service.create_agent(agent_config)
            assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_gohighlevel_integration_testing(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test GoHighLevel integration"""
        # This would test actual GoHighLevel API integration
        # Currently using mock, but should test real integration when available

        # Mock GoHighLevel API responses
        with patch('services.gohighlevel_adapter.GoHighLevelAdapter') as mock_ghl:
            mock_adapter = Mock()
            mock_ghl.return_value = mock_adapter

            # Test CRM contact creation
            mock_adapter.create_contact.return_value = {
                "id": "ghl_contact_123",
                "status": "created"
            }

            # Test integration through workflow
            service = AgentKitService(db=test_db, agentkit_api_key="test-key")

            # This would test the actual GoHighLevel integration
            # Implementation depends on adapter implementation

    @pytest.mark.asyncio
    async def test_platform_api_rate_limits(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test platform API rate limit handling"""
        # Test Google Ads API rate limiting
        with patch('services.platform_adapters.google_ads_adapter.GoogleAdsAdapter') as mock_gads:
            mock_adapter = Mock()
            mock_gads.return_value = mock_adapter

            # Simulate rate limit responses
            mock_adapter.create_campaign.side_effect = [
                {"status": "rate_limited", "retry_after": 60},  # First call rate limited
                {"id": "gads_campaign_123", "status": "created"}  # Retry succeeds
            ]

            # Test rate limit handling in workflow
            service = AgentKitService(db=test_db, agentkit_api_key="test-key")

            # This would test rate limit handling
            # Implementation depends on adapter implementation


class TestDataIntegrity:
    """Test data integrity and consistency"""

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_failure(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test transaction rollback when operations fail"""
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Start transaction-like operation
        agent_config = AgentConfig(
            agent_id="rollback_test_agent",
            organization_id=test_organization["organization_id"],
            name="Rollback Test Agent",
            agent_type="creative_intelligence",
            description="Agent for rollback testing",
            config={}
        )

        # Mock service to fail after database write
        with patch.object(service, 'create_agent') as mock_create:
            mock_create.side_effect = Exception("Unexpected failure after DB write")

            # This would test transaction rollback
            # Implementation depends on transaction support

    @pytest.mark.asyncio
    async def test_data_consistency_across_services(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test data consistency across multiple services"""
        auth_service = AuthService(db=test_db)
        agentkit_service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create user and organization
        user = await auth_service.create_user({
            "email": "consistency@example.com",
            "password": "TestPass123!",
            "first_name": "Consistency",
            "last_name": "Test",
            "organization_id": test_organization["organization_id"]
        })

        # Create agent for same organization
        agent_config = AgentConfig(
            agent_id="consistency_test_agent",
            organization_id=test_organization["organization_id"],
            name="Consistency Test Agent",
            agent_type="creative_intelligence",
            description="Agent for consistency testing",
            config={}
        )

        result = await agentkit_service.create_agent(agent_config)

        # Verify data consistency
        assert result["agent_id"] == "consistency_test_agent"
        assert result["organization_id"] == test_organization["organization_id"]

        # Verify user and agent reference same organization
        stored_user = await test_db.users.find_one({"user_id": user["user_id"]})
        stored_agent = await test_db.agentkit_agents.find_one({"agent_id": "consistency_test_agent"})

        assert stored_user["organization_id"] == stored_agent["organization_id"]


class TestScalability:
    """Test system scalability and performance under load"""

    @pytest.mark.asyncio
    async def test_high_concurrency_workflow_execution(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test workflow execution with high concurrency"""
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create test workflow
        workflow_data = {
            "name": "Scalability Test Workflow",
            "description": "Workflow for scalability testing",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "quick_analysis",
                    "agent_type": "analytics",
                    "input_mapping": {"data": "input"},
                    "output_mapping": {"result": "output"}
                }
            ]
        }

        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        # Execute 100 workflows concurrently
        start_time = time.time()

        tasks = []
        for i in range(100):
            task = service.execute_workflow(
                workflow_id=workflow_data["workflow_id"],
                input_data={"input": f"test_data_{i}"},
                user_id=f"scale_user_{i}",
                organization_id=test_organization["organization_id"]
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Performance assertions
        assert len(results) == 100
        assert total_time < 120.0  # Should complete within 2 minutes

        # All workflows should complete successfully
        for result in results:
            assert result.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_database_connection_pool_performance(self, test_db: Any):
        """Test database connection pool under load"""
        # This would test connection pool performance
        # Implementation depends on connection pool configuration

        # Simulate many concurrent database operations
        async def db_operation(i: int):
            # Perform database operation
            await test_db.agentkit_agents.find_one({"agent_id": f"nonexistent_{i}"})
            return True

        # Execute many concurrent operations
        tasks = [db_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks)

        assert all(results)

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test for memory leaks in long-running operations"""
        # Monitor memory usage over time
        process = psutil.Process()

        # Perform many operations and monitor memory
        initial_memory = process.memory_info().rss

        for i in range(10):
            # Create and execute workflow
            service = AgentKitService(db=test_db, agentkit_api_key="test-key")

            workflow_data = {
                "name": f"Leak Test Workflow {i}",
                "description": "Workflow for leak testing",
                "organization_id": test_organization["organization_id"],
                "steps": [
                    {
                        "step_id": f"step_{i}",
                        "agent_type": "creative_intelligence",
                        "input_mapping": {"data": f"input_{i}"},
                        "output_mapping": {"result": f"output_{i}"}
                    }
                ]
            }

            workflow = WorkflowDefinition(**workflow_data)
            await service.create_workflow(workflow)

            # Execute workflow
            await service.execute_workflow(
                workflow_id=workflow_data["workflow_id"],
                input_data={f"input_{i}": f"test_data_{i}"},
                user_id="test_user",
                organization_id=test_organization["organization_id"]
            )

            # Force garbage collection
            gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (< 20MB for 10 workflows)
        assert memory_increase < 20 * 1024 * 1024  # 20MB
