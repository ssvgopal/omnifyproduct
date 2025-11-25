"""
Kong Gateway Management Routes
API endpoints for managing Kong gateway configuration and monitoring
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from services.kong_gateway import kong_client, KongService, KongRoute, KongPlugin, KongConsumer, KongACLGroup
from services.oidc_auth import get_current_user, TokenValidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kong", tags=["Kong Gateway Management"])

# Request/Response Models
class KongServiceRequest(BaseModel):
    name: str
    url: str
    protocol: str = "http"
    host: str
    port: int
    path: Optional[str] = None
    connect_timeout: int = 60000
    write_timeout: int = 60000
    read_timeout: int = 60000

class KongRouteRequest(BaseModel):
    name: str
    service_name: str
    protocols: List[str] = ["http", "https"]
    methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    paths: List[str]
    strip_path: bool = True
    preserve_host: bool = False

class KongPluginRequest(BaseModel):
    name: str
    service_name: Optional[str] = None
    route_name: Optional[str] = None
    config: Dict[str, Any]
    enabled: bool = True

class KongConsumerRequest(BaseModel):
    username: str
    custom_id: Optional[str] = None
    tags: List[str] = []

class KongACLGroupRequest(BaseModel):
    group: str
    consumer_name: str

class KongStatsResponse(BaseModel):
    services: int
    routes: int
    plugins: int
    consumers: int
    acl_groups: int
    uptime: str
    version: str

# ========== KONG MANAGEMENT ROUTES ==========

@router.get("/health")
async def kong_health_check():
    """Check Kong gateway health"""
    try:
        return await kong_client.health_check()
    except Exception as e:
        logger.error(f"Kong health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Kong health check failed: {str(e)}"
        )

@router.post("/setup", response_model=Dict[str, Any])
async def setup_kong_gateway(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Setup complete Kong gateway configuration for OmniFy"""
    try:
        # Check if user has admin permissions
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required for Kong setup"
            )

        if not kong_client.enable_kong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kong is not enabled. Set ENABLE_KONG=true to enable."
            )

        result = await kong_client.setup_omnify_gateway()
        
        logger.info("Kong gateway setup completed", extra={
            "user_id": current_user.user_id,
            "services_created": len(result.get("services", [])),
            "routes_created": len(result.get("routes", [])),
            "plugins_created": len(result.get("plugins", []))
        })

        return {
            "status": "success",
            "message": "Kong gateway setup completed successfully",
            "configuration": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kong setup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kong setup failed: {str(e)}"
        )

@router.post("/services", response_model=Dict[str, Any])
async def create_kong_service(
    service_request: KongServiceRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new Kong service"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        service = KongService(**service_request.dict())
        result = await kong_client.create_service(service)
        
        return {
            "status": "success",
            "message": f"Service '{service.name}' created successfully",
            "service": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Kong service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )

@router.post("/routes", response_model=Dict[str, Any])
async def create_kong_route(
    route_request: KongRouteRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new Kong route"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        route = KongRoute(**route_request.dict())
        result = await kong_client.create_route(route)
        
        return {
            "status": "success",
            "message": f"Route '{route.name}' created successfully",
            "route": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Kong route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create route: {str(e)}"
        )

@router.post("/plugins", response_model=Dict[str, Any])
async def create_kong_plugin(
    plugin_request: KongPluginRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new Kong plugin"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        plugin = KongPlugin(**plugin_request.dict())
        result = await kong_client.create_plugin(plugin)
        
        return {
            "status": "success",
            "message": f"Plugin '{plugin.name}' created successfully",
            "plugin": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Kong plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create plugin: {str(e)}"
        )

@router.post("/consumers", response_model=Dict[str, Any])
async def create_kong_consumer(
    consumer_request: KongConsumerRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new Kong consumer"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        consumer = KongConsumer(**consumer_request.dict())
        result = await kong_client.create_consumer(consumer)
        
        return {
            "status": "success",
            "message": f"Consumer '{consumer.username}' created successfully",
            "consumer": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Kong consumer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create consumer: {str(e)}"
        )

@router.post("/acl-groups", response_model=Dict[str, Any])
async def create_kong_acl_group(
    acl_request: KongACLGroupRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create a new Kong ACL group"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        acl_group = KongACLGroup(**acl_request.dict())
        result = await kong_client.create_acl_group(acl_group)
        
        return {
            "status": "success",
            "message": f"ACL group '{acl_group.group}' created successfully",
            "acl_group": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Kong ACL group: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ACL group: {str(e)}"
        )

@router.get("/stats/{resource_name}")
async def get_kong_resource_stats(
    resource_name: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get statistics for a Kong resource (service, route, plugin)"""
    try:
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Determine resource type and get stats
        if resource_name.startswith("service-"):
            service_name = resource_name.replace("service-", "")
            result = await kong_client.get_service_stats(service_name)
        elif resource_name.startswith("route-"):
            route_name = resource_name.replace("route-", "")
            result = await kong_client.get_route_stats(route_name)
        elif resource_name.startswith("plugin-"):
            plugin_name = resource_name.replace("plugin-", "")
            result = await kong_client.get_plugin_stats(plugin_name)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource name. Use format: service-{name}, route-{name}, or plugin-{name}"
            )

        return {
            "resource_name": resource_name,
            "stats": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Kong resource stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.get("/overview", response_model=KongStatsResponse)
async def get_kong_overview(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get Kong gateway overview and statistics"""
    try:
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Get Kong health status
        health = await kong_client.health_check()
        
        # In a real implementation, you'd query Kong Admin API for actual counts
        # For now, return mock data based on our setup
        return KongStatsResponse(
            services=1,  # omnify-api service
            routes=5,   # api-all, auth, agentkit, eyes, health
            plugins=5, # rate-limiting, request-size, cors, prometheus, oidc
            consumers=3, # free-tier, pro-tier, enterprise-tier
            acl_groups=3, # free, pro, enterprise
            uptime="24h", # Would get from Kong status
            version="3.4" # Kong version
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Kong overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overview: {str(e)}"
        )

@router.get("/configuration")
async def get_kong_configuration(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get current Kong gateway configuration"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        return {
            "kong_enabled": kong_client.enable_kong,
            "kong_url": kong_client.kong_url,
            "kong_admin_url": kong_client.kong_admin_url,
            "oidc_plugin_enabled": kong_client.oidc_plugin_enabled,
            "rate_limit_per_minute": kong_client.rate_limit_per_minute,
            "request_size_limit_mb": kong_client.request_size_limit_mb,
            "timeout": kong_client.timeout,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Kong configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )
