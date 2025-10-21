"""
Performance Optimization System
Comprehensive caching, CDN, database optimization, and query optimization
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis
import aiohttp
import hashlib
import pickle
import time
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import psutil
import gc
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import wraps, lru_cache
import weakref
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import memcached
import elasticsearch
from elasticsearch import AsyncElasticsearch
import aioredis
import aiomcache

logger = logging.getLogger(__name__)

class CacheType(str, Enum):
    """Cache types"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"
    DISK = "disk"
    CDN = "cdn"

class CacheStrategy(str, Enum):
    """Cache strategies"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"

class OptimizationType(str, Enum):
    """Optimization types"""
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    CONNECTION_POOLING = "connection_pooling"
    QUERY_CACHING = "query_caching"
    RESULT_CACHING = "result_caching"
    CDN_CACHING = "cdn_caching"
    MEMORY_OPTIMIZATION = "memory_optimization"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int
    misses: int
    hit_rate: float
    miss_rate: float
    evictions: int
    memory_usage: int
    total_requests: int
    avg_response_time: float

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    connection_count: int
    active_queries: int
    slow_queries: int
    avg_query_time: float
    index_usage: Dict[str, float]
    cache_hit_rate: float
    deadlocks: int
    lock_waits: int

@dataclass
class PerformanceMetrics:
    """Overall performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    cache_metrics: CacheMetrics
    database_metrics: DatabaseMetrics

class MemoryCache:
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = deque()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            self.hits += 1
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key = self.access_order.popleft()
            del self.cache[oldest_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        miss_rate = self.misses / total_requests if total_requests > 0 else 0
        
        return CacheMetrics(
            hits=self.hits,
            misses=self.misses,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            evictions=0,  # LRU doesn't track evictions separately
            memory_usage=len(self.cache),
            total_requests=total_requests,
            avg_response_time=0.001  # In-memory is very fast
        )

class RedisCache:
    """Redis-based cache with advanced features"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = await self.redis.get(key)
            if value is not None:
                self.hits += 1
                return pickle.loads(value)
            else:
                self.misses += 1
                return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        try:
            serialized_value = pickle.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized_value)
            else:
                await self.redis.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        miss_rate = self.misses / total_requests if total_requests > 0 else 0
        
        return CacheMetrics(
            hits=self.hits,
            misses=self.misses,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            evictions=0,
            memory_usage=0,  # Redis doesn't expose memory usage easily
            total_requests=total_requests,
            avg_response_time=0.005  # Redis is fast but not as fast as memory
        )

class MemcachedCache:
    """Memcached-based cache"""
    
    def __init__(self, memcached_client):
        self.memcached = memcached_client
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Memcached"""
        try:
            value = await self.memcached.get(key)
            if value is not None:
                self.hits += 1
                return pickle.loads(value)
            else:
                self.misses += 1
                return None
        except Exception as e:
            logger.error(f"Memcached get error: {e}")
            self.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Memcached"""
        try:
            serialized_value = pickle.dumps(value)
            await self.memcached.set(key, serialized_value, ttl or 0)
            return True
        except Exception as e:
            logger.error(f"Memcached set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Memcached"""
        try:
            await self.memcached.delete(key)
            return True
        except Exception as e:
            logger.error(f"Memcached delete error: {e}")
            return False
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        miss_rate = self.misses / total_requests if total_requests > 0 else 0
        
        return CacheMetrics(
            hits=self.hits,
            misses=self.misses,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            evictions=0,
            memory_usage=0,
            total_requests=total_requests,
            avg_response_time=0.003  # Memcached is very fast
        )

class CDNCache:
    """CDN cache management"""
    
    def __init__(self, cdn_client):
        self.cdn = cdn_client
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from CDN cache"""
        try:
            # Simulate CDN get operation
            # In real implementation, this would check CDN cache
            self.misses += 1
            return None
        except Exception as e:
            logger.error(f"CDN get error: {e}")
            self.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in CDN cache"""
        try:
            # Simulate CDN set operation
            # In real implementation, this would upload to CDN
            return True
        except Exception as e:
            logger.error(f"CDN set error: {e}")
            return False
    
    async def purge(self, key: str) -> bool:
        """Purge key from CDN cache"""
        try:
            # Simulate CDN purge operation
            return True
        except Exception as e:
            logger.error(f"CDN purge error: {e}")
            return False
    
    def get_metrics(self) -> CacheMetrics:
        """Get CDN cache metrics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        miss_rate = self.misses / total_requests if total_requests > 0 else 0
        
        return CacheMetrics(
            hits=self.hits,
            misses=self.misses,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            evictions=0,
            memory_usage=0,
            total_requests=total_requests,
            avg_response_time=0.1  # CDN is slower but has global distribution
        )

class MultiLevelCache:
    """Multi-level cache system"""
    
    def __init__(self, redis_client: redis.Redis, memcached_client=None, cdn_client=None):
        self.memory_cache = MemoryCache(max_size=1000)
        self.redis_cache = RedisCache(redis_client)
        self.memcached_cache = MemcachedCache(memcached_client) if memcached_client else None
        self.cdn_cache = CDNCache(cdn_client) if cdn_client else None
        
        # Cache hierarchy (fastest to slowest)
        self.cache_levels = [self.memory_cache, self.redis_cache]
        if self.memcached_cache:
            self.cache_levels.append(self.memcached_cache)
        if self.cdn_cache:
            self.cache_levels.append(self.cdn_cache)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        for cache in self.cache_levels:
            value = await cache.get(key)
            if value is not None:
                # Promote to faster caches
                for faster_cache in self.cache_levels[:self.cache_levels.index(cache)]:
                    await faster_cache.set(key, value)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache"""
        success = True
        for cache in self.cache_levels:
            if not await cache.set(key, value, ttl):
                success = False
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        success = True
        for cache in self.cache_levels:
            if not await cache.delete(key):
                success = False
        return success
    
    async def clear(self) -> bool:
        """Clear all cache levels"""
        success = True
        for cache in self.cache_levels:
            if not await cache.clear():
                success = False
        return success
    
    def get_metrics(self) -> Dict[str, CacheMetrics]:
        """Get metrics for all cache levels"""
        metrics = {}
        for i, cache in enumerate(self.cache_levels):
            metrics[f"level_{i}"] = cache.get_metrics()
        return metrics

class DatabaseOptimizer:
    """Database optimization system"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.query_cache = {}
        self.slow_queries = []
        self.connection_pool = None
    
    async def optimize_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize database query"""
        try:
            # Analyze query performance
            start_time = time.time()
            
            # Execute query
            if params:
                result = await self.db.collection.find(query, params)
            else:
                result = await self.db.collection.find(query)
            
            execution_time = time.time() - start_time
            
            # Check if query is slow
            if execution_time > 1.0:  # 1 second threshold
                self.slow_queries.append({
                    "query": query,
                    "params": params,
                    "execution_time": execution_time,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Suggest optimizations
            optimizations = []
            if execution_time > 0.5:
                optimizations.append("Consider adding indexes")
            if "sort" in query.lower() and "limit" not in query.lower():
                optimizations.append("Add LIMIT clause to sort operations")
            if "count" in query.lower():
                optimizations.append("Consider using estimated count for large collections")
            
            return {
                "query": query,
                "execution_time": execution_time,
                "optimizations": optimizations,
                "is_slow": execution_time > 1.0
            }
            
        except Exception as e:
            logger.error(f"Query optimization error: {e}")
            return {
                "query": query,
                "execution_time": 0,
                "optimizations": ["Query failed"],
                "is_slow": False,
                "error": str(e)
            }
    
    async def create_index(self, collection: str, fields: List[str], options: Dict[str, Any] = None) -> bool:
        """Create database index"""
        try:
            index_spec = [(field, 1) for field in fields]
            await self.db[collection].create_index(index_spec, **(options or {}))
            logger.info(f"Created index on {collection}: {fields}")
            return True
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            return False
    
    async def analyze_index_usage(self, collection: str) -> Dict[str, Any]:
        """Analyze index usage"""
        try:
            # Get index statistics
            stats = await self.db.command("collStats", collection)
            
            return {
                "collection": collection,
                "index_count": len(stats.get("indexSizes", {})),
                "total_size": stats.get("size", 0),
                "index_sizes": stats.get("indexSizes", {}),
                "avg_obj_size": stats.get("avgObjSize", 0)
            }
        except Exception as e:
            logger.error(f"Index analysis error: {e}")
            return {"collection": collection, "error": str(e)}
    
    async def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow queries"""
        return self.slow_queries[-100:]  # Last 100 slow queries
    
    async def optimize_connection_pool(self, max_connections: int = 100) -> bool:
        """Optimize connection pool"""
        try:
            # Configure connection pool
            self.connection_pool = QueuePool(
                creator=lambda: self.db,
                pool_size=max_connections,
                max_overflow=max_connections * 2,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            return True
        except Exception as e:
            logger.error(f"Connection pool optimization error: {e}")
            return False

class QueryOptimizer:
    """Query optimization system"""
    
    def __init__(self):
        self.query_patterns = {}
        self.optimization_rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize optimization rules"""
        self.optimization_rules = [
            {
                "pattern": r"SELECT \* FROM",
                "optimization": "Use specific column names instead of SELECT *",
                "impact": "high"
            },
            {
                "pattern": r"WHERE.*LIKE.*%",
                "optimization": "Avoid leading wildcards in LIKE queries",
                "impact": "high"
            },
            {
                "pattern": r"ORDER BY.*LIMIT",
                "optimization": "Ensure ORDER BY columns are indexed",
                "impact": "medium"
            },
            {
                "pattern": r"JOIN.*ON.*=",
                "optimization": "Ensure JOIN columns are indexed",
                "impact": "high"
            },
            {
                "pattern": r"GROUP BY.*HAVING",
                "optimization": "Consider filtering in WHERE instead of HAVING",
                "impact": "medium"
            }
        ]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query for optimization opportunities"""
        optimizations = []
        
        for rule in self.optimization_rules:
            if re.search(rule["pattern"], query, re.IGNORECASE):
                optimizations.append({
                    "rule": rule["optimization"],
                    "impact": rule["impact"],
                    "pattern": rule["pattern"]
                })
        
        return {
            "query": query,
            "optimizations": optimizations,
            "optimization_count": len(optimizations),
            "has_high_impact": any(opt["impact"] == "high" for opt in optimizations)
        }
    
    def suggest_indexes(self, query: str) -> List[str]:
        """Suggest indexes for query"""
        indexes = []
        
        # Extract WHERE conditions
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)", query, re.IGNORECASE)
        if where_match:
            conditions = where_match.group(1)
            # Simple extraction of column names
            columns = re.findall(r"(\w+)\s*[=<>!]", conditions)
            if columns:
                indexes.append(f"Index on: {', '.join(columns)}")
        
        # Extract ORDER BY columns
        order_match = re.search(r"ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)", query, re.IGNORECASE)
        if order_match:
            order_columns = order_match.group(1)
            indexes.append(f"Index on ORDER BY: {order_columns}")
        
        return indexes

class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.alerts = []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_rate = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_rate = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent_rate = network_io.bytes_sent / (1024 * 1024) if network_io else 0
            network_recv_rate = network_io.bytes_recv / (1024 * 1024) if network_io else 0
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_available": memory.available / (1024 * 1024 * 1024),  # GB
                "disk_read_rate": disk_read_rate,
                "disk_write_rate": disk_write_rate,
                "network_sent_rate": network_sent_rate,
                "network_recv_rate": network_recv_rate,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        alerts = []
        
        if metrics.get("cpu_usage", 0) > 80:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics['cpu_usage']:.1f}%",
                "severity": "warning",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if metrics.get("memory_usage", 0) > 85:
            alerts.append({
                "type": "memory_high",
                "message": f"High memory usage: {metrics['memory_usage']:.1f}%",
                "severity": "critical",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if metrics.get("disk_read_rate", 0) > 100:  # 100 MB/s
            alerts.append({
                "type": "disk_io_high",
                "message": f"High disk I/O: {metrics['disk_read_rate']:.1f} MB/s",
                "severity": "warning",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def record_metrics(self, metrics: Dict[str, Any]):
        """Record metrics in history"""
        self.metrics_history.append(metrics)
    
    def get_metrics_trend(self, metric_name: str, hours: int = 24) -> List[float]:
        """Get metrics trend for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        trend_data = []
        for metrics in self.metrics_history:
            if datetime.fromisoformat(metrics["timestamp"]) > cutoff_time:
                trend_data.append(metrics.get(metric_name, 0))
        
        return trend_data

class PerformanceOptimizationService:
    """Main performance optimization service"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis_client = redis_client
        self.multi_level_cache = MultiLevelCache(redis_client)
        self.database_optimizer = DatabaseOptimizer(db)
        self.query_optimizer = QueryOptimizer()
        self.performance_monitor = PerformanceMonitor()
        
        # Performance settings
        self.settings = {
            "cache_ttl": 3600,  # 1 hour
            "max_cache_size": 10000,
            "slow_query_threshold": 1.0,  # 1 second
            "performance_check_interval": 60,  # 1 minute
            "auto_optimize": True
        }
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.multi_level_cache.get(key)
    
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        return await self.multi_level_cache.set(key, value, ttl or self.settings["cache_ttl"])
    
    async def cache_delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.multi_level_cache.delete(key)
    
    async def cache_clear(self) -> bool:
        """Clear all cache"""
        return await self.multi_level_cache.clear()
    
    async def optimize_database_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize database query"""
        return await self.database_optimizer.optimize_query(query, params)
    
    async def create_database_index(self, collection: str, fields: List[str], options: Dict[str, Any] = None) -> bool:
        """Create database index"""
        return await self.database_optimizer.create_index(collection, fields, options)
    
    async def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analyze query performance"""
        query_analysis = self.query_optimizer.analyze_query(query)
        suggested_indexes = self.query_optimizer.suggest_indexes(query)
        
        return {
            **query_analysis,
            "suggested_indexes": suggested_indexes
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        system_metrics = self.performance_monitor.get_system_metrics()
        cache_metrics = self.multi_level_cache.get_metrics()
        slow_queries = await self.database_optimizer.get_slow_queries()
        
        # Check for alerts
        alerts = self.performance_monitor.check_performance_alerts(system_metrics)
        
        # Record metrics
        self.performance_monitor.record_metrics(system_metrics)
        
        return {
            "system_metrics": system_metrics,
            "cache_metrics": cache_metrics,
            "slow_queries": slow_queries,
            "alerts": alerts,
            "settings": self.settings,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Run comprehensive performance optimization"""
        optimizations = []
        
        # Cache optimization
        cache_metrics = self.multi_level_cache.get_metrics()
        for level, metrics in cache_metrics.items():
            if metrics.hit_rate < 0.8:  # Less than 80% hit rate
                optimizations.append({
                    "type": "cache_optimization",
                    "level": level,
                    "action": "Increase cache size or TTL",
                    "current_hit_rate": metrics.hit_rate
                })
        
        # Database optimization
        slow_queries = await self.database_optimizer.get_slow_queries()
        if len(slow_queries) > 10:
            optimizations.append({
                "type": "database_optimization",
                "action": "Review and optimize slow queries",
                "slow_query_count": len(slow_queries)
            })
        
        # System optimization
        system_metrics = self.performance_monitor.get_system_metrics()
        if system_metrics.get("memory_usage", 0) > 80:
            optimizations.append({
                "type": "memory_optimization",
                "action": "Consider increasing memory or optimizing memory usage",
                "current_usage": system_metrics["memory_usage"]
            })
        
        return {
            "optimizations": optimizations,
            "optimization_count": len(optimizations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_performance_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get performance optimization dashboard"""
        try:
            # Get comprehensive metrics
            metrics = await self.get_performance_metrics()
            
            # Get optimization recommendations
            optimizations = await self.optimize_performance()
            
            # Get cache statistics
            cache_stats = {}
            for level, cache_metrics in metrics["cache_metrics"].items():
                cache_stats[level] = {
                    "hit_rate": cache_metrics.hit_rate,
                    "miss_rate": cache_metrics.miss_rate,
                    "total_requests": cache_metrics.total_requests,
                    "memory_usage": cache_metrics.memory_usage
                }
            
            return {
                "organization_id": organization_id,
                "system_metrics": metrics["system_metrics"],
                "cache_statistics": cache_stats,
                "database_metrics": {
                    "slow_queries_count": len(metrics["slow_queries"]),
                    "recent_slow_queries": metrics["slow_queries"][-5:] if metrics["slow_queries"] else []
                },
                "performance_alerts": metrics["alerts"],
                "optimization_recommendations": optimizations["optimizations"],
                "settings": self.settings,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance dashboard: {e}")
            raise

# Global instance
performance_optimization_service = None

def get_performance_optimization_service(db: AsyncIOMotorClient, redis_client: redis.Redis) -> PerformanceOptimizationService:
    """Get performance optimization service instance"""
    global performance_optimization_service
    if performance_optimization_service is None:
        performance_optimization_service = PerformanceOptimizationService(db, redis_client)
    return performance_optimization_service
