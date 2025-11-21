"""
Tests for REFLEXES Performance Optimization Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import psutil
from services.reflexes_performance_service import ReflexesPerformanceService, PerformanceMetrics, Bottleneck, OptimizationAction


@pytest.fixture
def mock_db():
    """Mock database client"""
    db = AsyncMock()
    db.request_logs = AsyncMock()
    db.command = AsyncMock()
    return db


@pytest.fixture
def reflexes_service(mock_db):
    """Create REFLEXES service instance"""
    return ReflexesPerformanceService(mock_db)


@pytest.mark.asyncio
async def test_get_system_metrics(reflexes_service, mock_db):
    """Test system metrics retrieval"""
    # Mock database responses
    mock_db.command.return_value = {
        'dataSize': 1000000,
        'storageSize': 2000000,
        'collections': 10
    }
    mock_db.request_logs.find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=[
        {'response_time': 150, 'timestamp': datetime.utcnow().isoformat()},
        {'response_time': 200, 'timestamp': datetime.utcnow().isoformat()}
    ])
    mock_db.request_logs.count_documents = AsyncMock(return_value=100)
    
    with patch('psutil.cpu_percent', return_value=45.0):
        with patch('psutil.virtual_memory') as mock_mem:
            mock_mem.return_value.percent = 60.0
            with patch('psutil.disk_usage') as mock_disk:
                mock_disk.return_value.percent = 50.0
                with patch('psutil.net_io_counters') as mock_net:
                    mock_net.return_value.bytes_sent = 1000000
                    mock_net.return_value.bytes_recv = 2000000
                    
                    result = await reflexes_service.get_system_metrics()
                    
                    assert isinstance(result, PerformanceMetrics)
                    assert result.cpu_usage == 45.0
                    assert result.memory_usage == 60.0
                    assert result.disk_io == 50.0
                    assert result.response_time > 0


@pytest.mark.asyncio
async def test_identify_bottlenecks(reflexes_service, mock_db):
    """Test bottleneck identification"""
    # Mock high CPU and memory usage
    with patch.object(reflexes_service, 'get_system_metrics', new_callable=AsyncMock) as mock_metrics:
        mock_metrics.return_value = PerformanceMetrics(
            cpu_usage=85.0,
            memory_usage=90.0,
            disk_io=50.0,
            network_io=100.0,
            response_time=1500.0,
            throughput=10.0,
            error_rate=8.0,
            timestamp=datetime.utcnow()
        )
        
        result = await reflexes_service.identify_bottlenecks()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(b, Bottleneck) for b in result)
        
        # Check for CPU bottleneck
        cpu_bottlenecks = [b for b in result if b.component == 'CPU']
        assert len(cpu_bottlenecks) > 0
        assert cpu_bottlenecks[0].severity in ['high', 'critical']


@pytest.mark.asyncio
async def test_get_optimization_recommendations(reflexes_service, mock_db):
    """Test optimization recommendations"""
    with patch.object(reflexes_service, 'get_system_metrics', new_callable=AsyncMock) as mock_metrics:
        mock_metrics.return_value = PerformanceMetrics(
            cpu_usage=75.0,
            memory_usage=80.0,
            disk_io=50.0,
            network_io=100.0,
            response_time=800.0,
            throughput=10.0,
            error_rate=3.0,
            timestamp=datetime.utcnow()
        )
        
        result = await reflexes_service.get_optimization_recommendations()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(r, OptimizationAction) for r in result)
        
        # Check for memory optimization
        memory_actions = [r for r in result if r.target == 'Memory']
        assert len(memory_actions) > 0

