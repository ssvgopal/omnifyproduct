"""
REFLEXES - Performance Optimization Brain Module
Real-time system optimization, automated scaling, performance monitoring
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.performance_optimization_service import PerformanceOptimizationService
import psutil
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    timestamp: datetime


@dataclass
class OptimizationAction:
    """Performance optimization action"""
    action_type: str
    target: str
    current_value: float
    recommended_value: float
    priority: str  # low, medium, high, critical
    impact: str
    estimated_improvement: float


@dataclass
class Bottleneck:
    """Performance bottleneck identification"""
    component: str
    metric: str
    current_value: float
    threshold: float
    severity: str  # low, medium, high, critical
    recommendations: List[str]


class ReflexesPerformanceService:
    """REFLEXES - Performance Optimization Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.performance_service = PerformanceOptimizationService(db)
        self.metrics_history = []
    
    async def get_system_metrics(self) -> PerformanceMetrics:
        """Get current system performance metrics"""
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network I/O
            net_io = psutil.net_io_counters()
            network_io = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            
            # Get database metrics
            db_metrics = await self._get_database_metrics()
            
            # Calculate response time (average from recent requests)
            response_time = await self._calculate_avg_response_time()
            
            # Calculate throughput (requests per second)
            throughput = await self._calculate_throughput()
            
            # Calculate error rate
            error_rate = await self._calculate_error_rate()
            
            metrics = PerformanceMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_io=disk.percent,
                network_io=network_io,
                response_time=response_time,
                throughput=throughput,
                error_rate=error_rate,
                timestamp=datetime.utcnow()
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            raise
    
    async def identify_bottlenecks(self) -> List[Bottleneck]:
        """Identify performance bottlenecks"""
        try:
            metrics = await self.get_system_metrics()
            bottlenecks = []
            
            # CPU bottleneck
            if metrics.cpu_usage > 80:
                bottlenecks.append(Bottleneck(
                    component='CPU',
                    metric='cpu_usage',
                    current_value=metrics.cpu_usage,
                    threshold=80.0,
                    severity='critical' if metrics.cpu_usage > 90 else 'high',
                    recommendations=[
                        'Scale horizontally by adding more instances',
                        'Optimize CPU-intensive operations',
                        'Consider upgrading CPU resources'
                    ]
                ))
            
            # Memory bottleneck
            if metrics.memory_usage > 85:
                bottlenecks.append(Bottleneck(
                    component='Memory',
                    metric='memory_usage',
                    current_value=metrics.memory_usage,
                    threshold=85.0,
                    severity='critical' if metrics.memory_usage > 95 else 'high',
                    recommendations=[
                        'Increase memory allocation',
                        'Optimize memory usage in code',
                        'Implement memory caching strategies'
                    ]
                ))
            
            # Response time bottleneck
            if metrics.response_time > 1000:  # > 1 second
                bottlenecks.append(Bottleneck(
                    component='API',
                    metric='response_time',
                    current_value=metrics.response_time,
                    threshold=1000.0,
                    severity='high' if metrics.response_time > 2000 else 'medium',
                    recommendations=[
                        'Optimize database queries',
                        'Implement caching',
                        'Review slow endpoints'
                    ]
                ))
            
            # Error rate bottleneck
            if metrics.error_rate > 5.0:  # > 5%
                bottlenecks.append(Bottleneck(
                    component='Error Rate',
                    metric='error_rate',
                    current_value=metrics.error_rate,
                    threshold=5.0,
                    severity='critical' if metrics.error_rate > 10 else 'high',
                    recommendations=[
                        'Review error logs',
                        'Fix critical bugs',
                        'Improve error handling'
                    ]
                ))
            
            return bottlenecks
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {str(e)}")
            raise
    
    async def get_optimization_recommendations(self) -> List[OptimizationAction]:
        """Get performance optimization recommendations"""
        try:
            metrics = await self.get_system_metrics()
            bottlenecks = await self.identify_bottlenecks()
            
            recommendations = []
            
            # CPU optimization
            if metrics.cpu_usage > 70:
                recommendations.append(OptimizationAction(
                    action_type='scale_horizontal',
                    target='CPU',
                    current_value=metrics.cpu_usage,
                    recommended_value=50.0,
                    priority='high' if metrics.cpu_usage > 80 else 'medium',
                    impact='Reduce CPU usage by distributing load',
                    estimated_improvement=(metrics.cpu_usage - 50.0) / metrics.cpu_usage * 100
                ))
            
            # Memory optimization
            if metrics.memory_usage > 75:
                recommendations.append(OptimizationAction(
                    action_type='optimize_memory',
                    target='Memory',
                    current_value=metrics.memory_usage,
                    recommended_value=60.0,
                    priority='high' if metrics.memory_usage > 85 else 'medium',
                    impact='Reduce memory footprint',
                    estimated_improvement=(metrics.memory_usage - 60.0) / metrics.memory_usage * 100
                ))
            
            # Response time optimization
            if metrics.response_time > 500:
                recommendations.append(OptimizationAction(
                    action_type='optimize_queries',
                    target='Response Time',
                    current_value=metrics.response_time,
                    recommended_value=200.0,
                    priority='high' if metrics.response_time > 1000 else 'medium',
                    impact='Improve API response times',
                    estimated_improvement=(metrics.response_time - 200.0) / metrics.response_time * 100
                ))
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {str(e)}")
            raise
    
    async def monitor_performance(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor performance over time"""
        try:
            start_time = datetime.utcnow()
            samples = []
            
            for _ in range(duration_seconds):
                metrics = await self.get_system_metrics()
                samples.append(metrics)
                await asyncio.sleep(1)
            
            # Calculate statistics
            avg_cpu = sum(s.cpu_usage for s in samples) / len(samples)
            avg_memory = sum(s.memory_usage for s in samples) / len(samples)
            avg_response = sum(s.response_time for s in samples) / len(samples)
            max_cpu = max(s.cpu_usage for s in samples)
            max_memory = max(s.memory_usage for s in samples)
            max_response = max(s.response_time for s in samples)
            
            return {
                'duration_seconds': duration_seconds,
                'start_time': start_time.isoformat(),
                'end_time': datetime.utcnow().isoformat(),
                'averages': {
                    'cpu_usage': avg_cpu,
                    'memory_usage': avg_memory,
                    'response_time': avg_response
                },
                'peaks': {
                    'cpu_usage': max_cpu,
                    'memory_usage': max_memory,
                    'response_time': max_response
                },
                'samples': len(samples)
            }
        except Exception as e:
            logger.error(f"Error monitoring performance: {str(e)}")
            raise
    
    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            # Get database stats
            stats = await self.db.command('dbStats')
            return {
                'data_size': stats.get('dataSize', 0),
                'storage_size': stats.get('storageSize', 0),
                'collections': stats.get('collections', 0)
            }
        except Exception as e:
            logger.warning(f"Error getting database metrics: {str(e)}")
            return {}
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent requests"""
        try:
            # Query recent request logs
            recent_logs = await self.db.request_logs.find({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=5)}
            }).sort('timestamp', -1).limit(100).to_list(length=100)
            
            if not recent_logs:
                return 200.0  # Default
            
            response_times = [log.get('response_time', 0) for log in recent_logs if log.get('response_time')]
            return sum(response_times) / len(response_times) if response_times else 200.0
        except Exception as e:
            logger.warning(f"Error calculating response time: {str(e)}")
            return 200.0
    
    async def _calculate_throughput(self) -> float:
        """Calculate requests per second"""
        try:
            # Count requests in last minute
            one_min_ago = datetime.utcnow() - timedelta(minutes=1)
            count = await self.db.request_logs.count_documents({
                'timestamp': {'$gte': one_min_ago}
            })
            return count / 60.0  # Requests per second
        except Exception as e:
            logger.warning(f"Error calculating throughput: {str(e)}")
            return 0.0
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        try:
            one_min_ago = datetime.utcnow() - timedelta(minutes=1)
            total_requests = await self.db.request_logs.count_documents({
                'timestamp': {'$gte': one_min_ago}
            })
            
            if total_requests == 0:
                return 0.0
            
            error_requests = await self.db.request_logs.count_documents({
                'timestamp': {'$gte': one_min_ago},
                'status_code': {'$gte': 400}
            })
            
            return (error_requests / total_requests) * 100.0
        except Exception as e:
            logger.warning(f"Error calculating error rate: {str(e)}")
            return 0.0

