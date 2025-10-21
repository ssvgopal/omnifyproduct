"""
Performance Optimization API Routes
Production-grade API endpoints for performance optimization features
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from backend.services.performance_optimization_service import (
    get_performance_optimization_service, PerformanceOptimizationService,
    CacheType, CacheStrategy, OptimizationType
)
from backend.core.database import get_database
from backend.core.redis_client import get_redis_client
from backend.core.auth import get_current_user
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/performance", tags=["Performance Optimization"])

@router.get("/dashboard")
async def get_performance_dashboard(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get performance optimization dashboard"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        dashboard = await service.get_performance_dashboard(organization_id)
        
        return JSONResponse(content=dashboard)
        
    except Exception as e:
        logger.error(f"Error getting performance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get comprehensive performance metrics"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        metrics = await service.get_performance_metrics()
        
        return JSONResponse(content=metrics)
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/get")
async def cache_get(
    cache_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get value from cache"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        key = cache_request["key"]
        value = await service.cache_get(key)
        
        return JSONResponse(content={
            "key": key,
            "value": value,
            "found": value is not None,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting from cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/set")
async def cache_set(
    cache_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Set value in cache"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        key = cache_request["key"]
        value = cache_request["value"]
        ttl = cache_request.get("ttl")
        
        success = await service.cache_set(key, value, ttl)
        
        return JSONResponse(content={
            "key": key,
            "success": success,
            "ttl": ttl,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error setting cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/{key}")
async def cache_delete(
    key: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Delete key from cache"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        success = await service.cache_delete(key)
        
        return JSONResponse(content={
            "key": key,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error deleting from cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def cache_clear(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Clear all cache"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        success = await service.cache_clear()
        
        return JSONResponse(content={
            "success": success,
            "message": "Cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/optimize-query")
async def optimize_database_query(
    query_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Optimize database query"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        query = query_request["query"]
        params = query_request.get("params")
        
        result = await service.optimize_database_query(query, params)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error optimizing database query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/create-index")
async def create_database_index(
    index_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Create database index"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        collection = index_request["collection"]
        fields = index_request["fields"]
        options = index_request.get("options")
        
        success = await service.create_database_index(collection, fields, options)
        
        return JSONResponse(content={
            "collection": collection,
            "fields": fields,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating database index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/analyze")
async def analyze_query_performance(
    query_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Analyze query performance"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        query = query_request["query"]
        analysis = await service.analyze_query_performance(query)
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing query performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def run_performance_optimization(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Run comprehensive performance optimization"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        optimizations = await service.optimize_performance()
        
        return JSONResponse(content=optimizations)
        
    except Exception as e:
        logger.error(f"Error running performance optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/metrics")
async def get_cache_metrics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get cache performance metrics"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        metrics = await service.get_performance_metrics()
        cache_metrics = metrics["cache_metrics"]
        
        return JSONResponse(content={
            "cache_metrics": cache_metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting cache metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/slow-queries")
async def get_slow_queries(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get slow queries"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        metrics = await service.get_performance_metrics()
        slow_queries = metrics["slow_queries"][-limit:] if metrics["slow_queries"] else []
        
        return JSONResponse(content={
            "slow_queries": slow_queries,
            "total_count": len(metrics["slow_queries"]),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get system performance metrics"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        metrics = await service.get_performance_metrics()
        system_metrics = metrics["system_metrics"]
        
        return JSONResponse(content={
            "system_metrics": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_performance_alerts(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get performance alerts"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        metrics = await service.get_performance_metrics()
        alerts = metrics["alerts"]
        
        return JSONResponse(content={
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting performance alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/update")
async def update_performance_settings(
    settings_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Update performance settings"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        # Update settings
        for key, value in settings_request.items():
            if key in service.settings:
                service.settings[key] = value
        
        return JSONResponse(content={
            "settings": service.settings,
            "message": "Settings updated successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating performance settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_performance_settings(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get performance settings"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        return JSONResponse(content={
            "settings": service.settings,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting performance settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/types")
async def get_cache_types():
    """Get supported cache types"""
    return JSONResponse(content={
        "cache_types": [ct.value for ct in CacheType],
        "cache_strategies": [cs.value for cs in CacheStrategy],
        "optimization_types": [ot.value for ot in OptimizationType]
    })

@router.post("/cache/warm")
async def warm_cache(
    warm_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Warm cache with frequently accessed data"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        keys_to_warm = warm_request.get("keys", [])
        
        # Warm cache in background
        async def warm_cache_task():
            for key in keys_to_warm:
                # Simulate warming cache with data
                await service.cache_set(key, f"warmed_data_{key}", 3600)
        
        background_tasks.add_task(warm_cache_task)
        
        return JSONResponse(content={
            "message": f"Cache warming started for {len(keys_to_warm)} keys",
            "keys": keys_to_warm,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error warming cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/analyze-indexes")
async def analyze_database_indexes(
    collection: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Analyze database indexes"""
    try:
        service = get_performance_optimization_service(db, redis_client)
        
        analysis = await service.database_optimizer.analyze_index_usage(collection)
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing database indexes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
