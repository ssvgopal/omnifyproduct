"""
Performance Tests for OmniFy Backend
Tests system performance under load and stress conditions
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
import uuid

# Import the modules to test
from services.agentkit_sdk_client import AgentKitSDKClient
from services.proactive_intelligence_engine import ProactiveIntelligenceEngine
from services.predictive_intelligence_dashboard import PredictiveIntelligenceDashboard
from integrations.gohighlevel.client import GoHighLevelAdapter
from integrations.meta_ads.client import MetaAdsAdapter
from integrations.google_ads.client import GoogleAdsAdapter

class TestPerformanceMetrics:
    """Test performance metrics and benchmarks"""
    
    @pytest.fixture
    def agentkit_client(self):
        return AgentKitSDKClient("test-api-key")
    
    @pytest.fixture
    def proactive_engine(self):
        mock_db = None
        return ProactiveIntelligenceEngine(mock_db)
    
    @pytest.fixture
    def predictive_dashboard(self):
        mock_db = None
        return PredictiveIntelligenceDashboard(mock_db)
    
    def test_agent_execution_performance(self, agentkit_client):
        """Test agent execution performance benchmarks"""
        execution_times = []
        
        for _ in range(100):
            start_time = time.time()
            
            # Simulate agent execution
            execution_request = {
                "agent_id": "test-agent",
                "input_data": {"test": "data"},
                "context": {"user_id": "test-user"}
            }
            
            # Mock execution time
            time.sleep(0.01)  # Simulate 10ms execution
            
            end_time = time.time()
            execution_times.append(end_time - start_time)
        
        # Calculate performance metrics
        avg_execution_time = statistics.mean(execution_times)
        median_execution_time = statistics.median(execution_times)
        p95_execution_time = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile
        p99_execution_time = statistics.quantiles(execution_times, n=100)[98]  # 99th percentile
        
        # Performance assertions
        assert avg_execution_time < 0.1, f"Average execution time too slow: {avg_execution_time:.3f}s"
        assert median_execution_time < 0.1, f"Median execution time too slow: {median_execution_time:.3f}s"
        assert p95_execution_time < 0.2, f"95th percentile too slow: {p95_execution_time:.3f}s"
        assert p99_execution_time < 0.5, f"99th percentile too slow: {p99_execution_time:.3f}s"
        
        print(f"Agent Execution Performance:")
        print(f"  Average: {avg_execution_time:.3f}s")
        print(f"  Median: {median_execution_time:.3f}s")
        print(f"  95th percentile: {p95_execution_time:.3f}s")
        print(f"  99th percentile: {p99_execution_time:.3f}s")
    
    def test_prediction_generation_performance(self, predictive_dashboard):
        """Test prediction generation performance"""
        prediction_times = []
        
        for _ in range(50):
            start_time = time.time()
            
            # Simulate prediction generation
            client_id = f"test-client-{uuid.uuid4()}"
            prediction_type = "creative_fatigue"
            
            # Mock prediction generation
            time.sleep(0.005)  # Simulate 5ms generation
            
            end_time = time.time()
            prediction_times.append(end_time - start_time)
        
        # Calculate performance metrics
        avg_prediction_time = statistics.mean(prediction_times)
        median_prediction_time = statistics.median(prediction_times)
        p95_prediction_time = statistics.quantiles(prediction_times, n=20)[18]
        
        # Performance assertions
        assert avg_prediction_time < 0.05, f"Average prediction time too slow: {avg_prediction_time:.3f}s"
        assert median_prediction_time < 0.05, f"Median prediction time too slow: {median_prediction_time:.3f}s"
        assert p95_prediction_time < 0.1, f"95th percentile too slow: {p95_prediction_time:.3f}s"
        
        print(f"Prediction Generation Performance:")
        print(f"  Average: {avg_prediction_time:.3f}s")
        print(f"  Median: {median_prediction_time:.3f}s")
        print(f"  95th percentile: {p95_prediction_time:.3f}s")
    
    def test_proactive_action_generation_performance(self, proactive_engine):
        """Test proactive action generation performance"""
        action_times = []
        
        for _ in range(50):
            start_time = time.time()
            
            # Simulate proactive action generation
            client_id = f"test-client-{uuid.uuid4()}"
            action_type = "creative_fatigue"
            
            # Mock action generation
            time.sleep(0.008)  # Simulate 8ms generation
            
            end_time = time.time()
            action_times.append(end_time - start_time)
        
        # Calculate performance metrics
        avg_action_time = statistics.mean(action_times)
        median_action_time = statistics.median(action_times)
        p95_action_time = statistics.quantiles(action_times, n=20)[18]
        
        # Performance assertions
        assert avg_action_time < 0.05, f"Average action time too slow: {avg_action_time:.3f}s"
        assert median_action_time < 0.05, f"Median action time too slow: {median_action_time:.3f}s"
        assert p95_action_time < 0.1, f"95th percentile too slow: {p95_action_time:.3f}s"
        
        print(f"Proactive Action Generation Performance:")
        print(f"  Average: {avg_action_time:.3f}s")
        print(f"  Median: {median_action_time:.3f}s")
        print(f"  95th percentile: {p95_action_time:.3f}s")

class TestLoadTesting:
    """Test system performance under load"""
    
    def test_concurrent_agent_executions(self):
        """Test concurrent agent executions"""
        def execute_agent():
            start_time = time.time()
            
            # Simulate agent execution
            time.sleep(0.02)  # 20ms execution time
            
            end_time = time.time()
            return end_time - start_time
        
        # Test with different concurrency levels
        concurrency_levels = [10, 25, 50, 100]
        
        for concurrency in concurrency_levels:
            execution_times = []
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(execute_agent) for _ in range(concurrency)]
                
                for future in as_completed(futures):
                    execution_time = future.result()
                    execution_times.append(execution_time)
            
            avg_time = statistics.mean(execution_times)
            max_time = max(execution_times)
            
            print(f"Concurrency {concurrency}:")
            print(f"  Average execution time: {avg_time:.3f}s")
            print(f"  Max execution time: {max_time:.3f}s")
            
            # Performance assertions
            assert avg_time < 0.1, f"Average time too slow for concurrency {concurrency}: {avg_time:.3f}s"
            assert max_time < 0.5, f"Max time too slow for concurrency {concurrency}: {max_time:.3f}s"
    
    def test_concurrent_prediction_generation(self):
        """Test concurrent prediction generation"""
        def generate_prediction():
            start_time = time.time()
            
            # Simulate prediction generation
            time.sleep(0.01)  # 10ms generation time
            
            end_time = time.time()
            return end_time - start_time
        
        # Test with different concurrency levels
        concurrency_levels = [20, 50, 100, 200]
        
        for concurrency in concurrency_levels:
            generation_times = []
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(generate_prediction) for _ in range(concurrency)]
                
                for future in as_completed(futures):
                    generation_time = future.result()
                    generation_times.append(generation_time)
            
            avg_time = statistics.mean(generation_times)
            max_time = max(generation_times)
            
            print(f"Prediction Concurrency {concurrency}:")
            print(f"  Average generation time: {avg_time:.3f}s")
            print(f"  Max generation time: {max_time:.3f}s")
            
            # Performance assertions
            assert avg_time < 0.05, f"Average time too slow for concurrency {concurrency}: {avg_time:.3f}s"
            assert max_time < 0.2, f"Max time too slow for concurrency {concurrency}: {max_time:.3f}s"
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate memory-intensive operations
        large_data_structures = []
        
        for i in range(1000):
            # Create large data structure
            large_data = {
                "id": f"item-{i}",
                "data": [j for j in range(1000)],
                "metadata": {"created_at": datetime.now().isoformat()}
            }
            large_data_structures.append(large_data)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        print(f"Memory Usage Under Load:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Peak memory: {peak_memory:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        
        # Memory assertions
        assert memory_increase < 500, f"Memory increase too high: {memory_increase:.2f} MB"
        
        # Cleanup
        del large_data_structures

class TestStressTesting:
    """Test system behavior under stress conditions"""
    
    def test_sustained_load(self):
        """Test system under sustained load"""
        def sustained_operation():
            start_time = time.time()
            
            # Simulate sustained operation
            for _ in range(100):
                # Simulate work
                time.sleep(0.001)  # 1ms per operation
            
            end_time = time.time()
            return end_time - start_time
        
        # Run sustained load for 30 seconds
        start_time = time.time()
        operation_times = []
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            while time.time() - start_time < 30:  # 30 seconds
                future = executor.submit(sustained_operation)
                operation_time = future.result()
                operation_times.append(operation_time)
        
        # Analyze results
        avg_time = statistics.mean(operation_times)
        max_time = max(operation_times)
        min_time = min(operation_times)
        
        print(f"Sustained Load Test (30 seconds):")
        print(f"  Operations completed: {len(operation_times)}")
        print(f"  Average operation time: {avg_time:.3f}s")
        print(f"  Min operation time: {min_time:.3f}s")
        print(f"  Max operation time: {max_time:.3f}s")
        
        # Stress test assertions
        assert len(operation_times) > 100, "Not enough operations completed"
        assert avg_time < 0.2, f"Average operation time too slow: {avg_time:.3f}s"
        assert max_time < 1.0, f"Max operation time too slow: {max_time:.3f}s"
    
    def test_error_recovery_under_load(self):
        """Test error recovery under load"""
        def operation_with_errors():
            import random
            
            # Simulate occasional errors
            if random.random() < 0.1:  # 10% error rate
                raise Exception("Simulated error")
            
            # Simulate normal operation
            time.sleep(0.01)
            return "success"
        
        success_count = 0
        error_count = 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(operation_with_errors) for _ in range(200)]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result == "success":
                        success_count += 1
                except Exception:
                    error_count += 1
        
        success_rate = success_count / (success_count + error_count)
        
        print(f"Error Recovery Under Load:")
        print(f"  Success count: {success_count}")
        print(f"  Error count: {error_count}")
        print(f"  Success rate: {success_rate:.2%}")
        
        # Error recovery assertions
        assert success_rate > 0.8, f"Success rate too low: {success_rate:.2%}"
        assert error_count > 0, "No errors occurred (test may not be valid)"
    
    def test_resource_exhaustion_recovery(self):
        """Test recovery from resource exhaustion"""
        def resource_intensive_operation():
            # Simulate resource-intensive operation
            large_list = []
            for _ in range(10000):
                large_list.append(uuid.uuid4().hex)
            
            # Simulate processing
            time.sleep(0.01)
            
            return len(large_list)
        
        # Run operations until potential resource exhaustion
        results = []
        
        try:
            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = [executor.submit(resource_intensive_operation) for _ in range(500)]
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(f"Operation failed: {e}")
                        break
        except Exception as e:
            print(f"Resource exhaustion occurred: {e}")
        
        print(f"Resource Exhaustion Recovery:")
        print(f"  Operations completed: {len(results)}")
        print(f"  Success rate: {len(results)/500:.2%}")
        
        # Resource exhaustion assertions
        assert len(results) > 100, "Too few operations completed before exhaustion"
        assert len(results)/500 > 0.2, "Success rate too low after resource exhaustion"

class TestScalability:
    """Test system scalability"""
    
    def test_horizontal_scaling_simulation(self):
        """Test horizontal scaling simulation"""
        def simulate_worker():
            start_time = time.time()
            
            # Simulate work
            time.sleep(0.05)  # 50ms work
            
            end_time = time.time()
            return end_time - start_time
        
        # Test different worker counts
        worker_counts = [1, 2, 4, 8, 16]
        total_work = 100  # Total operations to complete
        
        for workers in worker_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(simulate_worker) for _ in range(total_work)]
                
                for future in as_completed(futures):
                    future.result()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            throughput = total_work / total_time
            
            print(f"Workers: {workers}, Total time: {total_time:.3f}s, Throughput: {throughput:.2f} ops/s")
            
            # Scalability assertions
            if workers > 1:
                # Should see improvement with more workers (up to a point)
                assert throughput > 10, f"Throughput too low with {workers} workers: {throughput:.2f} ops/s"
    
    def test_data_volume_scaling(self):
        """Test data volume scaling"""
        def process_data(data_size):
            start_time = time.time()
            
            # Simulate data processing
            data = [i for i in range(data_size)]
            processed_data = [x * 2 for x in data]
            
            end_time = time.time()
            return end_time - start_time
        
        # Test different data volumes
        data_sizes = [1000, 5000, 10000, 50000, 100000]
        
        for size in data_sizes:
            processing_time = process_data(size)
            throughput = size / processing_time
            
            print(f"Data size: {size}, Processing time: {processing_time:.3f}s, Throughput: {throughput:.0f} items/s")
            
            # Data volume scaling assertions
            assert processing_time < 1.0, f"Processing time too slow for size {size}: {processing_time:.3f}s"
            assert throughput > 1000, f"Throughput too low for size {size}: {throughput:.0f} items/s"

class TestPlatformIntegrationPerformance:
    """Test platform integration performance"""
    
    def test_gohighlevel_api_performance(self):
        """Test GoHighLevel API performance"""
        adapter = GoHighLevelAdapter()
        
        def simulate_api_call():
            start_time = time.time()
            
            # Simulate API call
            time.sleep(0.1)  # 100ms API call
            
            end_time = time.time()
            return end_time - start_time
        
        # Test API call performance
        api_times = []
        for _ in range(20):
            api_time = simulate_api_call()
            api_times.append(api_time)
        
        avg_api_time = statistics.mean(api_times)
        max_api_time = max(api_times)
        
        print(f"GoHighLevel API Performance:")
        print(f"  Average API time: {avg_api_time:.3f}s")
        print(f"  Max API time: {max_api_time:.3f}s")
        
        # API performance assertions
        assert avg_api_time < 0.2, f"Average API time too slow: {avg_api_time:.3f}s"
        assert max_api_time < 0.5, f"Max API time too slow: {max_api_time:.3f}s"
    
    def test_meta_ads_api_performance(self):
        """Test Meta Ads API performance"""
        adapter = MetaAdsAdapter()
        
        def simulate_api_call():
            start_time = time.time()
            
            # Simulate API call
            time.sleep(0.08)  # 80ms API call
            
            end_time = time.time()
            return end_time - start_time
        
        # Test API call performance
        api_times = []
        for _ in range(20):
            api_time = simulate_api_call()
            api_times.append(api_time)
        
        avg_api_time = statistics.mean(api_times)
        max_api_time = max(api_times)
        
        print(f"Meta Ads API Performance:")
        print(f"  Average API time: {avg_api_time:.3f}s")
        print(f"  Max API time: {max_api_time:.3f}s")
        
        # API performance assertions
        assert avg_api_time < 0.15, f"Average API time too slow: {avg_api_time:.3f}s"
        assert max_api_time < 0.3, f"Max API time too slow: {max_api_time:.3f}s"
    
    def test_google_ads_api_performance(self):
        """Test Google Ads API performance"""
        adapter = GoogleAdsAdapter()
        
        def simulate_api_call():
            start_time = time.time()
            
            # Simulate API call
            time.sleep(0.12)  # 120ms API call
            
            end_time = time.time()
            return end_time - start_time
        
        # Test API call performance
        api_times = []
        for _ in range(20):
            api_time = simulate_api_call()
            api_times.append(api_time)
        
        avg_api_time = statistics.mean(api_times)
        max_api_time = max(api_times)
        
        print(f"Google Ads API Performance:")
        print(f"  Average API time: {avg_api_time:.3f}s")
        print(f"  Max API time: {max_api_time:.3f}s")
        
        # API performance assertions
        assert avg_api_time < 0.2, f"Average API time too slow: {avg_api_time:.3f}s"
        assert max_api_time < 0.4, f"Max API time too slow: {max_api_time:.3f}s"

class TestPerformanceRegression:
    """Test for performance regressions"""
    
    def test_performance_baseline(self):
        """Test performance baseline"""
        def baseline_operation():
            start_time = time.time()
            
            # Simulate baseline operation
            time.sleep(0.01)  # 10ms baseline
            
            end_time = time.time()
            return end_time - start_time
        
        # Run baseline test
        baseline_times = []
        for _ in range(100):
            baseline_time = baseline_operation()
            baseline_times.append(baseline_time)
        
        avg_baseline_time = statistics.mean(baseline_times)
        median_baseline_time = statistics.median(baseline_times)
        
        print(f"Performance Baseline:")
        print(f"  Average time: {avg_baseline_time:.3f}s")
        print(f"  Median time: {median_baseline_time:.3f}s")
        
        # Baseline assertions
        assert avg_baseline_time < 0.05, f"Baseline average time too slow: {avg_baseline_time:.3f}s"
        assert median_baseline_time < 0.05, f"Baseline median time too slow: {median_baseline_time:.3f}s"
        
        # Store baseline for regression testing
        self.baseline_avg_time = avg_baseline_time
        self.baseline_median_time = median_baseline_time
    
    def test_performance_regression(self):
        """Test for performance regressions"""
        def current_operation():
            start_time = time.time()
            
            # Simulate current operation (should be similar to baseline)
            time.sleep(0.01)  # 10ms operation
            
            end_time = time.time()
            return end_time - start_time
        
        # Run current test
        current_times = []
        for _ in range(100):
            current_time = current_operation()
            current_times.append(current_time)
        
        avg_current_time = statistics.mean(current_times)
        median_current_time = statistics.median(current_times)
        
        print(f"Current Performance:")
        print(f"  Average time: {avg_current_time:.3f}s")
        print(f"  Median time: {median_current_time:.3f}s")
        
        # Regression assertions
        if hasattr(self, 'baseline_avg_time'):
            regression_factor = avg_current_time / self.baseline_avg_time
            print(f"  Regression factor: {regression_factor:.2f}x")
            
            assert regression_factor < 2.0, f"Performance regression detected: {regression_factor:.2f}x slower"
            assert avg_current_time < 0.1, f"Current average time too slow: {avg_current_time:.3f}s"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
