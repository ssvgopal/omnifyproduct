"""
Comprehensive Performance Tests for OmniFy Cloud Connect
Load testing, stress testing, and performance benchmarking
"""

import pytest
import asyncio
import json
import time
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

from tests.conftest import test_client, test_user_token

class TestLoadPerformance:
    """Load testing for normal expected usage"""
    
    @pytest.mark.asyncio
    async def test_concurrent_user_load(self, test_client, test_user_token):
        """Test system performance under concurrent user load"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Simulate 50 concurrent users making requests
        concurrent_users = 50
        requests_per_user = 10
        
        async def simulate_user(user_id: int):
            """Simulate a single user making requests"""
            user_headers = {"Authorization": f"Bearer {test_user_token}"}
            response_times = []
            
            for request_num in range(requests_per_user):
                start_time = time.time()
                
                # Mix of different request types
                if request_num % 4 == 0:
                    response = await test_client.get("/campaigns", headers=user_headers)
                elif request_num % 4 == 1:
                    response = await test_client.get("/analytics/dashboard", headers=user_headers)
                elif request_num % 4 == 2:
                    response = await test_client.get("/agents", headers=user_headers)
                else:
                    response = await test_client.get("/workflows", headers=user_headers)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                # Verify response is successful
                assert response.status_code in [200, 201, 202]
            
            return {
                "user_id": user_id,
                "response_times": response_times,
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "min_response_time": min(response_times)
            }
        
        # Run concurrent users
        start_time = time.time()
        tasks = [simulate_user(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        all_response_times = []
        for result in results:
            all_response_times.extend(result["response_times"])
        
        avg_response_time = statistics.mean(all_response_times)
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18]  # 95th percentile
        p99_response_time = statistics.quantiles(all_response_times, n=100)[98]  # 99th percentile
        
        # Performance assertions
        assert avg_response_time < 2.0, f"Average response time {avg_response_time:.2f}s exceeds 2s limit"
        assert p95_response_time < 5.0, f"95th percentile response time {p95_response_time:.2f}s exceeds 5s limit"
        assert p99_response_time < 10.0, f"99th percentile response time {p99_response_time:.2f}s exceeds 10s limit"
        
        # Throughput assertion
        total_requests = concurrent_users * requests_per_user
        throughput = total_requests / total_time
        assert throughput > 100, f"Throughput {throughput:.2f} requests/second below 100 req/s threshold"
        
        print(f"Load Test Results:")
        print(f"  Concurrent Users: {concurrent_users}")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} req/s")
        print(f"  Avg Response Time: {avg_response_time:.2f}s")
        print(f"  95th Percentile: {p95_response_time:.2f}s")
        print(f"  99th Percentile: {p99_response_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_database_performance(self, test_client, test_user_token):
        """Test database performance under load"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test database write performance
        write_times = []
        for i in range(100):
            start_time = time.time()
            
            campaign_data = {
                "name": f"Performance Test Campaign {i}",
                "platform": "google_ads",
                "budget": 1000.0
            }
            
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=campaign_data
            )
            
            end_time = time.time()
            write_times.append(end_time - start_time)
            
            assert response.status_code == 201
        
        # Test database read performance
        read_times = []
        for i in range(100):
            start_time = time.time()
            
            response = await test_client.get("/campaigns", 
                headers=headers,
                params={"limit": 50, "offset": i * 50}
            )
            
            end_time = time.time()
            read_times.append(end_time - start_time)
            
            assert response.status_code == 200
        
        # Analyze database performance
        avg_write_time = statistics.mean(write_times)
        avg_read_time = statistics.mean(read_times)
        
        assert avg_write_time < 1.0, f"Average write time {avg_write_time:.2f}s exceeds 1s limit"
        assert avg_read_time < 0.5, f"Average read time {avg_read_time:.2f}s exceeds 0.5s limit"
        
        print(f"Database Performance Results:")
        print(f"  Avg Write Time: {avg_write_time:.3f}s")
        print(f"  Avg Read Time: {avg_read_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_api_endpoint_performance(self, test_client, test_user_token):
        """Test individual API endpoint performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        endpoints = [
            ("GET", "/campaigns"),
            ("GET", "/analytics/dashboard"),
            ("GET", "/agents"),
            ("GET", "/workflows"),
            ("GET", "/integrations/platforms"),
            ("GET", "/onboarding/status"),
            ("GET", "/health")
        ]
        
        endpoint_performance = {}
        
        for method, endpoint in endpoints:
            response_times = []
            
            # Test each endpoint 50 times
            for i in range(50):
                start_time = time.time()
                
                if method == "GET":
                    response = await test_client.get(endpoint, headers=headers)
                elif method == "POST":
                    response = await test_client.post(endpoint, headers=headers, json={})
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                assert response.status_code in [200, 201, 202, 404]  # 404 acceptable for some endpoints
            
            avg_time = statistics.mean(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]
            
            endpoint_performance[endpoint] = {
                "avg_time": avg_time,
                "p95_time": p95_time,
                "max_time": max(response_times),
                "min_time": min(response_times)
            }
            
            # Performance assertions
            assert avg_time < 2.0, f"Endpoint {endpoint} avg time {avg_time:.2f}s exceeds 2s limit"
            assert p95_time < 5.0, f"Endpoint {endpoint} 95th percentile {p95_time:.2f}s exceeds 5s limit"
        
        print("API Endpoint Performance Results:")
        for endpoint, perf in endpoint_performance.items():
            print(f"  {endpoint}: avg={perf['avg_time']:.3f}s, p95={perf['p95_time']:.3f}s")

class TestStressPerformance:
    """Stress testing for extreme conditions"""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, test_client, test_user_token):
        """Test system under high concurrency stress"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Simulate 200 concurrent users (stress test)
        concurrent_users = 200
        requests_per_user = 5
        
        async def stress_user(user_id: int):
            """Simulate a stressed user"""
            user_headers = {"Authorization": f"Bearer {test_user_token}"}
            success_count = 0
            error_count = 0
            
            for request_num in range(requests_per_user):
                try:
                    response = await test_client.get("/campaigns", headers=user_headers)
                    if response.status_code in [200, 201, 202]:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
            
            return {
                "user_id": user_id,
                "success_count": success_count,
                "error_count": error_count
            }
        
        # Run stress test
        start_time = time.time()
        tasks = [stress_user(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze stress test results
        total_success = sum(r["success_count"] for r in results if isinstance(r, dict))
        total_errors = sum(r["error_count"] for r in results if isinstance(r, dict))
        total_requests = concurrent_users * requests_per_user
        
        success_rate = total_success / total_requests
        error_rate = total_errors / total_requests
        
        # Stress test assertions
        assert success_rate > 0.8, f"Success rate {success_rate:.2%} below 80% threshold"
        assert error_rate < 0.2, f"Error rate {error_rate:.2%} above 20% threshold"
        
        print(f"Stress Test Results:")
        print(f"  Concurrent Users: {concurrent_users}")
        print(f"  Total Requests: {total_requests}")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Error Rate: {error_rate:.2%}")
        print(f"  Total Time: {total_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_memory_usage_stress(self, test_client, test_user_token):
        """Test memory usage under stress"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large amounts of data
        large_campaigns = []
        for i in range(1000):
            campaign_data = {
                "name": f"Memory Stress Test Campaign {i}",
                "platform": "google_ads",
                "budget": 1000.0,
                "description": "x" * 1000,  # Large description
                "metadata": {f"key{j}": f"value{j}" * 100 for j in range(10)}  # Large metadata
            }
            
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=campaign_data
            )
            
            if response.status_code == 201:
                large_campaigns.append(response.json()["campaign_id"])
        
        # Check memory usage after creating large data
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory usage assertions
        assert memory_increase < 500, f"Memory increase {memory_increase:.2f}MB exceeds 500MB limit"
        
        # Clean up large data
        for campaign_id in large_campaigns:
            await test_client.delete(f"/campaigns/{campaign_id}", headers=headers)
        
        # Check memory after cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_after_cleanup = final_memory - initial_memory
        
        print(f"Memory Stress Test Results:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Peak Memory: {peak_memory:.2f}MB")
        print(f"  Memory Increase: {memory_increase:.2f}MB")
        print(f"  Memory After Cleanup: {memory_after_cleanup:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_long_running_operations(self, test_client, test_user_token):
        """Test long-running operations performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test long-running analytics job
        analytics_data = {
            "job_type": "comprehensive_analytics",
            "parameters": {
                "platforms": ["google_ads", "meta_ads", "linkedin_ads"],
                "date_range": "2024-01-01,2024-12-31",
                "detailed_breakdown": True
            }
        }
        
        start_time = time.time()
        
        job_response = await test_client.post("/jobs/submit", 
            headers=headers,
            json=analytics_data
        )
        
        assert job_response.status_code == 202
        job_id = job_response.json()["job_id"]
        
        # Monitor job progress
        max_wait_time = 60  # seconds
        start_monitor_time = time.time()
        
        while time.time() - start_monitor_time < max_wait_time:
            status_response = await test_client.get(f"/jobs/{job_id}/status", headers=headers)
            status = status_response.json()
            
            if status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)
        
        total_job_time = time.time() - start_time
        
        # Long-running operation assertions
        assert total_job_time < 60, f"Long-running job took {total_job_time:.2f}s, exceeds 60s limit"
        
        print(f"Long-Running Operations Test Results:")
        print(f"  Job Completion Time: {total_job_time:.2f}s")

class TestPerformanceBenchmarks:
    """Performance benchmarking tests"""
    
    @pytest.mark.asyncio
    async def test_campaign_creation_benchmark(self, test_client, test_user_token):
        """Benchmark campaign creation performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        creation_times = []
        
        for i in range(100):
            start_time = time.time()
            
            campaign_data = {
                "name": f"Benchmark Campaign {i}",
                "platform": "google_ads",
                "objective": "lead_generation",
                "budget": 1000.0,
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["technology"]
                }
            }
            
            response = await test_client.post("/campaigns/create", 
                headers=headers,
                json=campaign_data
            )
            
            end_time = time.time()
            creation_times.append(end_time - start_time)
            
            assert response.status_code == 201
        
        # Benchmark analysis
        avg_creation_time = statistics.mean(creation_times)
        median_creation_time = statistics.median(creation_times)
        p95_creation_time = statistics.quantiles(creation_times, n=20)[18]
        
        # Benchmark assertions
        assert avg_creation_time < 1.0, f"Avg campaign creation time {avg_creation_time:.3f}s exceeds 1s benchmark"
        assert median_creation_time < 0.8, f"Median campaign creation time {median_creation_time:.3f}s exceeds 0.8s benchmark"
        assert p95_creation_time < 2.0, f"95th percentile creation time {p95_creation_time:.3f}s exceeds 2s benchmark"
        
        print(f"Campaign Creation Benchmark:")
        print(f"  Average: {avg_creation_time:.3f}s")
        print(f"  Median: {median_creation_time:.3f}s")
        print(f"  95th Percentile: {p95_creation_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_analytics_generation_benchmark(self, test_client, test_user_token):
        """Benchmark analytics generation performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        analytics_times = []
        
        for i in range(50):
            start_time = time.time()
            
            analytics_data = {
                "platform": "google_ads",
                "metrics": ["impressions", "clicks", "conversions", "spend"],
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                },
                "breakdown": ["campaign"]
            }
            
            response = await test_client.post("/analytics/generate", 
                headers=headers,
                json=analytics_data
            )
            
            end_time = time.time()
            analytics_times.append(end_time - start_time)
            
            assert response.status_code == 200
        
        # Benchmark analysis
        avg_analytics_time = statistics.mean(analytics_times)
        median_analytics_time = statistics.median(analytics_times)
        p95_analytics_time = statistics.quantiles(analytics_times, n=20)[18]
        
        # Benchmark assertions
        assert avg_analytics_time < 3.0, f"Avg analytics generation time {avg_analytics_time:.3f}s exceeds 3s benchmark"
        assert median_analytics_time < 2.0, f"Median analytics generation time {median_analytics_time:.3f}s exceeds 2s benchmark"
        assert p95_analytics_time < 5.0, f"95th percentile analytics time {p95_analytics_time:.3f}s exceeds 5s benchmark"
        
        print(f"Analytics Generation Benchmark:")
        print(f"  Average: {avg_analytics_time:.3f}s")
        print(f"  Median: {median_analytics_time:.3f}s")
        print(f"  95th Percentile: {p95_analytics_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_ai_agent_execution_benchmark(self, test_client, test_user_token):
        """Benchmark AI agent execution performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create test agent
        agent_data = {
            "name": "Benchmark Test Agent",
            "type": "creative_agent",
            "capabilities": ["content_generation"],
            "prompt_template": "Generate creative content for: {topic}",
            "model": "gpt-4o",
            "temperature": 0.7
        }
        
        agent_response = await test_client.post("/agents/create", 
            headers=headers,
            json=agent_data
        )
        agent_id = agent_response.json()["agent_id"]
        
        execution_times = []
        
        for i in range(30):
            start_time = time.time()
            
            execution_data = {
                "agent_id": agent_id,
                "input_data": {"topic": f"Benchmark test topic {i}"},
                "action": "generate_content"
            }
            
            response = await test_client.post("/agents/execute", 
                headers=headers,
                json=execution_data
            )
            
            end_time = time.time()
            execution_times.append(end_time - start_time)
            
            assert response.status_code == 200
        
        # Benchmark analysis
        avg_execution_time = statistics.mean(execution_times)
        median_execution_time = statistics.median(execution_times)
        p95_execution_time = statistics.quantiles(execution_times, n=20)[18]
        
        # Benchmark assertions
        assert avg_execution_time < 5.0, f"Avg AI agent execution time {avg_execution_time:.3f}s exceeds 5s benchmark"
        assert median_execution_time < 4.0, f"Median AI agent execution time {median_execution_time:.3f}s exceeds 4s benchmark"
        assert p95_execution_time < 10.0, f"95th percentile execution time {p95_execution_time:.3f}s exceeds 10s benchmark"
        
        print(f"AI Agent Execution Benchmark:")
        print(f"  Average: {avg_execution_time:.3f}s")
        print(f"  Median: {median_execution_time:.3f}s")
        print(f"  95th Percentile: {p95_execution_time:.3f}s")

class TestResourceUtilization:
    """Resource utilization tests"""
    
    @pytest.mark.asyncio
    async def test_cpu_utilization(self, test_client, test_user_token):
        """Test CPU utilization under load"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Create CPU-intensive workload
        async def cpu_intensive_task():
            """CPU-intensive task"""
            for i in range(1000):
                # Simulate CPU work
                sum(range(1000))
                await asyncio.sleep(0.001)  # Small delay to prevent blocking
        
        # Run multiple CPU-intensive tasks concurrently
        tasks = [cpu_intensive_task() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Check CPU usage after workload
        final_cpu = psutil.cpu_percent(interval=1)
        
        print(f"CPU Utilization Test:")
        print(f"  Initial CPU: {initial_cpu:.1f}%")
        print(f"  Final CPU: {final_cpu:.1f}%")
        
        # CPU utilization should be reasonable
        assert final_cpu < 90, f"CPU utilization {final_cpu:.1f}% exceeds 90% threshold"
    
    @pytest.mark.asyncio
    async def test_disk_io_performance(self, test_client, test_user_token):
        """Test disk I/O performance"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test file upload performance
        upload_times = []
        
        for i in range(10):
            # Create test file content
            file_content = b"x" * (1024 * 1024)  # 1MB file
            
            start_time = time.time()
            
            files = {"file": ("test_file.txt", file_content, "text/plain")}
            response = await test_client.post("/files/upload", 
                headers=headers,
                files=files
            )
            
            end_time = time.time()
            upload_times.append(end_time - start_time)
            
            assert response.status_code == 201
        
        avg_upload_time = statistics.mean(upload_times)
        
        # Disk I/O performance assertions
        assert avg_upload_time < 2.0, f"Average file upload time {avg_upload_time:.2f}s exceeds 2s limit"
        
        print(f"Disk I/O Performance Test:")
        print(f"  Average Upload Time: {avg_upload_time:.2f}s")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
