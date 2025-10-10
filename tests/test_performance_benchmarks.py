"""
Performance Benchmarking Tests for OmnifyProduct
Systematic performance measurement and regression testing
"""

import pytest
import asyncio
import time
import statistics
import psutil
import gc
from typing import Dict, List, Any
from dataclasses import dataclass
from httpx import AsyncClient

# Import our services
from services.agentkit_service import AgentKitService
from services.workflow_orchestrator import WorkflowOrchestrator
from models.agentkit_models import AgentConfig, WorkflowDefinition


@dataclass
class PerformanceMetrics:
    """Performance measurement data"""
    operation_name: str
    execution_times: List[float]
    memory_usage: List[int]
    cpu_usage: List[float]

    @property
    def avg_execution_time(self) -> float:
        return statistics.mean(self.execution_times) if self.execution_times else 0

    @property
    def p95_execution_time(self) -> float:
        return statistics.quantiles(self.execution_times, n=20)[18] if len(self.execution_times) >= 20 else max(self.execution_times)

    @property
    def avg_memory_usage(self) -> int:
        return int(statistics.mean(self.memory_usage)) if self.memory_usage else 0

    @property
    def max_memory_usage(self) -> int:
        return max(self.memory_usage) if self.memory_usage else 0


class PerformanceBenchmark:
    """Performance benchmarking utilities"""

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.process = psutil.Process()

    def start_measurement(self, operation_name: str):
        """Start measuring performance for an operation"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = PerformanceMetrics(
                operation_name=operation_name,
                execution_times=[],
                memory_usage=[],
                cpu_usage=[]
            )

        # Force garbage collection before measurement
        gc.collect()

        return time.time()

    def end_measurement(self, operation_name: str, start_time: float):
        """End measurement and record metrics"""
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        metrics = self.metrics[operation_name]
        metrics.execution_times.append(execution_time)
        metrics.memory_usage.append(self.process.memory_info().rss)
        metrics.cpu_usage.append(self.process.cpu_percent())

    def get_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Get performance metrics for an operation"""
        return self.metrics.get(operation_name)

    def print_summary(self):
        """Print performance summary"""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)

        for operation_name, metrics in self.metrics.items():
            print(f"\n📊 {operation_name}:")
            print(f"  Average execution time: {metrics.avg_execution_time".2f"}ms")
            print(f"  P95 execution time: {metrics.p95_execution_time".2f"}ms")
            print(f"  Average memory usage: {metrics.avg_memory_usage / 1024 / 1024".2f"}MB")
            print(f"  Max memory usage: {metrics.max_memory_usage / 1024 / 1024".2f"}MB")
            print(f"  Samples: {len(metrics.execution_times)}")

        print("\n" + "="*60)


class TestAPIPerformance:
    """API endpoint performance testing"""

    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self, client: AsyncClient):
        """Benchmark health endpoint response times"""
        benchmark = PerformanceBenchmark()

        # Warm up
        await client.get("/health")

        # Benchmark multiple requests
        for i in range(100):
            start_time = benchmark.start_measurement("health_endpoint")
            response = await client.get("/health")
            benchmark.end_measurement("health_endpoint", start_time)

            assert response.status_code == 200

        metrics = benchmark.get_metrics("health_endpoint")
        assert metrics.avg_execution_time < 50  # Should average under 50ms
        assert metrics.p95_execution_time < 100  # P95 under 100ms

    @pytest.mark.asyncio
    async def test_agent_creation_performance(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Benchmark agent creation performance"""
        benchmark = PerformanceBenchmark()

        # Benchmark agent creation
        for i in range(50):
            agent_config = {
                "name": f"Performance Agent {i}",
                "agent_type": "creative_intelligence",
                "description": f"Agent for performance testing {i}",
                "organization_id": test_organization["organization_id"],
                "config": {
                    "platforms": ["google_ads", "meta_ads"],
                    "analysis_types": ["aida", "brand_compliance"]
                }
            }

            start_time = benchmark.start_measurement("agent_creation")
            response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
            benchmark.end_measurement("agent_creation", start_time)

            assert response.status_code == 200

        metrics = benchmark.get_metrics("agent_creation")
        assert metrics.avg_execution_time < 200  # Should average under 200ms
        assert metrics.p95_execution_time < 500  # P95 under 500ms

    @pytest.mark.asyncio
    async def test_agent_execution_performance(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Benchmark agent execution performance"""
        benchmark = PerformanceBenchmark()

        # Create test agent first
        agent_config = {
            "name": "Execution Performance Agent",
            "agent_type": "creative_intelligence",
            "description": "Agent for execution performance testing",
            "organization_id": test_organization["organization_id"],
            "config": {"platforms": ["google_ads"]}
        }

        create_response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
        agent_id = create_response.json()["agent_id"]

        # Benchmark agent execution
        for i in range(30):
            execution_request = {
                "input_data": {
                    "asset_url": f"https://example.com/asset_{i}.jpg",
                    "analysis_type": "aida"
                },
                "context": {"request_id": i}
            }

            start_time = benchmark.start_measurement("agent_execution")
            response = await client.post(
                f"/api/agentkit/agents/{agent_id}/execute",
                json=execution_request,
                headers=auth_headers
            )
            benchmark.end_measurement("agent_execution", start_time)

            assert response.status_code == 200

        metrics = benchmark.get_metrics("agent_execution")
        assert metrics.avg_execution_time < 1000  # Should average under 1 second
        assert metrics.p95_execution_time < 2000  # P95 under 2 seconds


class TestWorkflowPerformance:
    """Workflow orchestration performance testing"""

    @pytest.mark.asyncio
    async def test_workflow_creation_performance(self, test_db: Any, test_organization: Dict[str, Any]):
        """Benchmark workflow creation performance"""
        benchmark = PerformanceBenchmark()
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Benchmark workflow creation with varying complexity
        for complexity in [1, 5, 10, 20]:  # Different numbers of steps
            workflow_data = {
                "name": f"Complexity {complexity} Workflow",
                "description": f"Workflow with {complexity} steps for performance testing",
                "organization_id": test_organization["organization_id"],
                "steps": []
            }

            # Add steps based on complexity
            for i in range(complexity):
                workflow_data["steps"].append({
                    "step_id": f"step_{i}",
                    "agent_type": "creative_intelligence" if i % 2 == 0 else "analytics",
                    "input_mapping": {f"data_{i}": f"input_{i}"},
                    "output_mapping": {f"result_{i}": f"output_{i}"}
                })

            operation_name = f"workflow_creation_{complexity}_steps"
            start_time = benchmark.start_measurement(operation_name)

            workflow = WorkflowDefinition(**workflow_data)
            await service.create_workflow(workflow)

            benchmark.end_measurement(operation_name, start_time)

        # Performance assertions
        for complexity in [1, 5, 10, 20]:
            operation_name = f"workflow_creation_{complexity}_steps"
            metrics = benchmark.get_metrics(operation_name)

            # Creation time should scale reasonably with complexity
            max_expected_time = complexity * 50  # 50ms per step
            assert metrics.avg_execution_time < max_expected_time

    @pytest.mark.asyncio
    async def test_parallel_workflow_execution_performance(self, test_db: Any, test_organization: Dict[str, Any]):
        """Benchmark parallel workflow execution performance"""
        benchmark = PerformanceBenchmark()
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        # Create test workflow
        workflow_data = {
            "name": "Parallel Execution Test Workflow",
            "description": "Workflow for parallel execution testing",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "parallel_1",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"data": "input_1"},
                    "output_mapping": {"result": "output_1"}
                },
                {
                    "step_id": "parallel_2",
                    "agent_type": "analytics",
                    "input_mapping": {"data": "input_2"},
                    "output_mapping": {"result": "output_2"}
                }
            ],
            "config": {"execution_mode": "parallel"}
        }

        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20]

        for concurrency in concurrency_levels:
            operation_name = f"parallel_execution_{concurrency}_workflows"
            start_time = benchmark.start_measurement(operation_name)

            # Execute multiple workflows in parallel
            tasks = []
            for i in range(concurrency):
                task = service.execute_workflow(
                    workflow_id=workflow_data["workflow_id"],
                    input_data={
                        "input_1": f"test_data_1_{i}",
                        "input_2": f"test_data_2_{i}"
                    },
                    user_id=f"parallel_user_{i}",
                    organization_id=test_organization["organization_id"]
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            benchmark.end_measurement(operation_name, start_time)

            # All workflows should complete successfully
            for result in results:
                assert result.status == "completed"

        # Performance analysis
        for concurrency in concurrency_levels:
            operation_name = f"parallel_execution_{concurrency}_workflows"
            metrics = benchmark.get_metrics(operation_name)

            # Parallel execution should provide performance benefits
            expected_time = concurrency * 1000  # Base time for serial execution
            actual_time = metrics.avg_execution_time

            # Parallel execution should be faster than serial
            if concurrency > 1:
                speedup_ratio = expected_time / actual_time
                assert speedup_ratio > 1.2  # At least 20% speedup for parallel execution


class TestDatabasePerformance:
    """Database operation performance testing"""

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, test_db: Any):
        """Benchmark bulk insert operations"""
        benchmark = PerformanceBenchmark()

        # Test different batch sizes
        batch_sizes = [10, 50, 100, 500, 1000]

        for batch_size in batch_sizes:
            operation_name = f"bulk_insert_{batch_size}_agents"
            start_time = benchmark.start_measurement(operation_name)

            # Insert batch of agents
            agents_data = []
            for i in range(batch_size):
                agents_data.append({
                    "agent_id": f"bulk_agent_{batch_size}_{i}",
                    "organization_id": "test_org",
                    "name": f"Bulk Agent {i}",
                    "agent_type": "creative_intelligence",
                    "is_active": True,
                    "created_at": "2024-01-15T10:00:00Z"
                })

            await test_db.agentkit_agents.insert_many(agents_data)
            benchmark.end_measurement(operation_name, start_time)

        # Performance analysis
        for batch_size in batch_sizes:
            operation_name = f"bulk_insert_{batch_size}_agents"
            metrics = benchmark.get_metrics(operation_name)

            # Insert time per agent should be reasonable
            time_per_agent = metrics.avg_execution_time / batch_size
            assert time_per_agent < 10  # Less than 10ms per agent

    @pytest.mark.asyncio
    async def test_query_performance_with_indexing(self, test_db: Any):
        """Benchmark query performance with and without indexes"""
        benchmark = PerformanceBenchmark()

        # Insert test data
        agents_data = []
        for i in range(1000):
            agents_data.append({
                "agent_id": f"query_agent_{i}",
                "organization_id": f"org_{i % 10}",  # 10 different organizations
                "name": f"Query Agent {i}",
                "agent_type": "creative_intelligence",
                "is_active": i % 2 == 0,  # 50% active
                "created_at": f"2024-01-{15 + (i % 15):02d}T10:00:00Z"
            })

        await test_db.agentkit_agents.insert_many(agents_data)

        # Test query without index
        operation_name = "query_without_index"
        start_time = benchmark.start_measurement(operation_name)

        # Query by organization (no index on this field)
        agents = await test_db.agentkit_agents.find(
            {"organization_id": "org_5"}
        ).to_list(None)

        benchmark.end_measurement(operation_name, start_time)
        unindexed_time = benchmark.get_metrics(operation_name).avg_execution_time

        # Create index on organization_id
        await test_db.agentkit_agents.create_index([("organization_id", 1)])

        # Test query with index
        operation_name = "query_with_index"
        start_time = benchmark.start_measurement(operation_name)

        agents = await test_db.agentkit_agents.find(
            {"organization_id": "org_5"}
        ).to_list(None)

        benchmark.end_measurement(operation_name, start_time)
        indexed_time = benchmark.get_metrics(operation_name).avg_execution_time

        # Index should provide significant performance improvement
        assert indexed_time < unindexed_time * 0.5  # At least 50% improvement
        assert len(agents) == 100  # Should find 100 agents for org_5

    @pytest.mark.asyncio
    async def test_aggregation_performance(self, test_db: Any):
        """Benchmark aggregation pipeline performance"""
        benchmark = PerformanceBenchmark()

        # Insert test execution data
        executions_data = []
        for i in range(500):
            executions_data.append({
                "execution_id": f"exec_{i}",
                "agent_id": f"agent_{i % 50}",  # 50 different agents
                "organization_id": f"org_{i % 10}",  # 10 different organizations
                "status": "completed" if i % 3 != 0 else "failed",  # ~33% failures
                "execution_time_seconds": (i % 10) + 1,  # 1-10 seconds
                "created_at": f"2024-01-{15 + (i % 15):02d}T10:00:00Z"
            })

        await test_db.agentkit_executions.insert_many(executions_data)

        # Test aggregation performance
        operation_name = "execution_analytics_aggregation"
        start_time = benchmark.start_measurement(operation_name)

        # Complex aggregation pipeline
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id": {
                    "organization_id": "$organization_id",
                    "agent_id": "$agent_id"
                },
                "total_executions": {"$sum": 1},
                "avg_execution_time": {"$avg": "$execution_time_seconds"},
                "success_rate": {"$avg": 1.0}
            }},
            {"$sort": {"total_executions": -1}}
        ]

        results = await test_db.agentkit_executions.aggregate(pipeline).to_list(None)
        benchmark.end_measurement(operation_name, start_time)

        metrics = benchmark.get_metrics(operation_name)

        # Aggregation should complete quickly
        assert metrics.avg_execution_time < 200  # Under 200ms
        assert len(results) > 0  # Should return results

        # Verify aggregation results
        for result in results:
            assert result["total_executions"] > 0
            assert result["avg_execution_time"] > 0


class TestMemoryPerformance:
    """Memory usage and leak detection testing"""

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test memory usage during sustained load"""
        benchmark = PerformanceBenchmark()
        process = psutil.Process()

        # Monitor memory usage over time
        memory_samples = []

        # Simulate sustained load for 30 seconds
        start_time = time.time()
        iteration = 0

        while time.time() - start_time < 30:  # 30 second load test
            iteration += 1

            # Perform memory-intensive operations
            service = AgentKitService(db=test_db, agentkit_api_key="test-key")

            # Create workflow with multiple steps
            workflow_data = {
                "name": f"Load Test Workflow {iteration}",
                "description": "Workflow for load testing",
                "organization_id": test_organization["organization_id"],
                "steps": []
            }

            for i in range(5):  # 5 steps per workflow
                workflow_data["steps"].append({
                    "step_id": f"step_{iteration}_{i}",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"data": f"input_{i}"},
                    "output_mapping": {f"result_{i}": f"output_{i}"}
                })

            workflow = WorkflowDefinition(**workflow_data)
            await service.create_workflow(workflow)

            # Execute workflow
            await service.execute_workflow(
                workflow_id=workflow_data["workflow_id"],
                input_data={f"input_{i}": f"test_data_{i}" for i in range(5)},
                user_id="load_test_user",
                organization_id=test_organization["organization_id"]
            )

            # Sample memory usage
            memory_samples.append(process.memory_info().rss)

            # Small delay to simulate realistic usage
            await asyncio.sleep(0.1)

        # Analyze memory usage pattern
        if len(memory_samples) > 10:
            initial_memory = memory_samples[0]
            final_memory = memory_samples[-1]
            max_memory = max(memory_samples)

            # Memory should not grow unbounded
            memory_growth = final_memory - initial_memory
            assert memory_growth < 50 * 1024 * 1024  # Less than 50MB growth

            # Memory usage should be relatively stable
            memory_std_dev = statistics.stdev(memory_samples) if len(memory_samples) > 1 else 0
            assert memory_std_dev < 20 * 1024 * 1024  # Standard deviation under 20MB

    @pytest.mark.asyncio
    async def test_garbage_collection_effectiveness(self, test_db: Any, test_organization: Dict[str, Any]):
        """Test garbage collection effectiveness"""
        benchmark = PerformanceBenchmark()
        process = psutil.Process()

        # Create many objects and measure GC effectiveness
        memory_before_objects = process.memory_info().rss

        # Create many workflow objects
        workflows = []
        for i in range(100):
            workflow_data = {
                "name": f"GC Test Workflow {i}",
                "description": "Workflow for GC testing",
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
            workflows.append(workflow)

        memory_after_objects = process.memory_info().rss

        # Force garbage collection
        gc.collect()
        memory_after_gc = process.memory_info().rss

        # Calculate GC effectiveness
        objects_memory = memory_after_objects - memory_before_objects
        freed_memory = memory_after_objects - memory_after_gc

        gc_effectiveness = (freed_memory / objects_memory) if objects_memory > 0 else 0

        # GC should free at least 50% of object memory
        assert gc_effectiveness > 0.5

        # Final memory should be close to initial
        final_growth = memory_after_gc - memory_before_objects
        assert final_growth < 10 * 1024 * 1024  # Less than 10MB permanent growth


class TestConcurrentLoad:
    """Concurrent user and operation testing"""

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test API performance under concurrent requests"""
        benchmark = PerformanceBenchmark()

        # Simulate 100 concurrent API requests
        async def make_request(i: int):
            start_time = benchmark.start_measurement(f"concurrent_request_{i}")
            response = await client.get("/health", headers=auth_headers)
            benchmark.end_measurement(f"concurrent_request_{i}", start_time)
            return response.status_code

        # Execute concurrent requests
        tasks = [make_request(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # All requests should succeed
        assert all(status == 200 for status in results)

        # Analyze performance under load
        all_metrics = []
        for i in range(100):
            metrics = benchmark.get_metrics(f"concurrent_request_{i}")
            if metrics:
                all_metrics.append(metrics.avg_execution_time)

        if all_metrics:
            avg_response_time = statistics.mean(all_metrics)
            p95_response_time = statistics.quantiles(all_metrics, n=20)[18] if len(all_metrics) >= 20 else max(all_metrics)

            # Performance under concurrent load
            assert avg_response_time < 200  # Average under 200ms
            assert p95_response_time < 500  # P95 under 500ms

    @pytest.mark.asyncio
    async def test_database_connection_pool_stress(self, test_db: Any):
        """Test database connection pool under stress"""
        benchmark = PerformanceBenchmark()

        # Simulate many concurrent database operations
        async def db_operation(i: int):
            operation_name = f"db_operation_{i}"
            start_time = benchmark.start_measurement(operation_name)

            # Perform various database operations
            await test_db.agentkit_agents.find_one({"agent_id": f"stress_agent_{i}"})
            await test_db.agentkit_executions.find_one({"execution_id": f"stress_exec_{i}"})

            benchmark.end_measurement(operation_name, start_time)
            return True

        # Execute 200 concurrent database operations
        tasks = [db_operation(i) for i in range(200)]
        results = await asyncio.gather(*tasks)

        assert all(results)

        # Analyze database performance under load
        db_metrics = []
        for i in range(200):
            metrics = benchmark.get_metrics(f"db_operation_{i}")
            if metrics:
                db_metrics.append(metrics.avg_execution_time)

        if db_metrics:
            avg_db_time = statistics.mean(db_metrics)
            p95_db_time = statistics.quantiles(db_metrics, n=20)[18] if len(db_metrics) >= 20 else max(db_metrics)

            # Database operations should remain fast under load
            assert avg_db_time < 50  # Average under 50ms
            assert p95_db_time < 100  # P95 under 100ms


class TestRegressionDetection:
    """Regression testing and performance monitoring"""

    def test_performance_regression_detection(self):
        """Detect performance regressions between test runs"""
        # This would compare current performance against baseline
        # Implementation would depend on performance baseline storage

        # Example: Check that critical operations haven't slowed down
        benchmark = PerformanceBenchmark()

        # Simulate critical operation
        start_time = benchmark.start_measurement("critical_operation")
        # Simulate work
        time.sleep(0.1)  # 100ms operation
        benchmark.end_measurement("critical_operation", start_time)

        metrics = benchmark.get_metrics("critical_operation")

        # Check against baseline (would be stored from previous runs)
        baseline_time = 120  # 120ms baseline
        current_time = metrics.avg_execution_time

        # Alert if performance degraded significantly
        degradation_threshold = 1.5  # 50% slower is concerning
        if current_time > baseline_time * degradation_threshold:
            pytest.fail(f"Performance regression detected: {current_time".2f"}ms vs baseline {baseline_time}ms")

    @pytest.mark.asyncio
    async def test_memory_regression_detection(self, test_db: Any):
        """Detect memory usage regressions"""
        benchmark = PerformanceBenchmark()
        process = psutil.Process()

        # Measure memory usage for standard operation
        start_time = benchmark.start_measurement("memory_baseline")
        initial_memory = process.memory_info().rss

        # Perform standard operations
        service = AgentKitService(db=test_db, agentkit_api_key="test-key")

        workflow_data = {
            "name": "Memory Regression Test",
            "description": "Workflow for memory regression testing",
            "organization_id": "test_org",
            "steps": [
                {
                    "step_id": "test_step",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"data": "test"},
                    "output_mapping": {"result": "output"}
                }
            ]
        }

        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        await service.execute_workflow(
            workflow_id=workflow_data["workflow_id"],
            input_data={"test": "data"},
            user_id="test_user",
            organization_id="test_org"
        )

        final_memory = process.memory_info().rss
        benchmark.end_measurement("memory_baseline", start_time)

        memory_increase = final_memory - initial_memory

        # Check against baseline (would be stored from previous runs)
        baseline_memory_increase = 10 * 1024 * 1024  # 10MB baseline

        # Alert if memory usage increased significantly
        if memory_increase > baseline_memory_increase * 2:  # 2x baseline
            pytest.fail(f"Memory regression detected: {memory_increase / 1024 / 1024".2f"}MB vs baseline {baseline_memory_increase / 1024 / 1024".2f"}MB")


# Global benchmark instance for cross-test analysis
_global_benchmark = PerformanceBenchmark()


@pytest.fixture(scope="session", autouse=True)
def session_performance_monitor():
    """Monitor performance across entire test session"""
    yield _global_benchmark
    _global_benchmark.print_summary()


# Performance assertion helpers
def assert_performance_baseline(operation_name: str, max_time_ms: float, max_memory_mb: float = None):
    """Assert that operation meets performance baseline"""
    metrics = _global_benchmark.get_metrics(operation_name)

    if metrics:
        assert metrics.avg_execution_time <= max_time_ms, \
            f"{operation_name} exceeded time baseline: {metrics.avg_execution_time".2f"}ms > {max_time_ms}ms"

        if max_memory_mb and metrics.avg_memory_usage > 0:
            avg_memory_mb = metrics.avg_memory_usage / 1024 / 1024
            assert avg_memory_mb <= max_memory_mb, \
                f"{operation_name} exceeded memory baseline: {avg_memory_mb".2f"}MB > {max_memory_mb}MB"
