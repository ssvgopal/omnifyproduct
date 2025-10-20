"""
Kong API Gateway Integration
Enterprise-grade API gateway with OIDC authentication, rate limiting, and request filtering
"""

import os
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class KongPluginType(Enum):
    OIDC = "oidc"
    RATE_LIMITING = "rate-limiting"
    REQUEST_SIZE_LIMITING = "request-size-limiting"
    IP_RESTRICTION = "ip-restriction"
    CORS = "cors"
    REQUEST_TRANSFORMER = "request-transformer"
    RESPONSE_TRANSFORMER = "response-transformer"
    PROMETHEUS = "prometheus"

class KongService(BaseModel):
    """Kong service definition"""
    name: str
    url: str
    protocol: str = "http"
    host: str
    port: int
    path: Optional[str] = None
    connect_timeout: int = 60000
    write_timeout: int = 60000
    read_timeout: int = 60000

class KongRoute(BaseModel):
    """Kong route definition"""
    name: str
    service_name: str
    protocols: List[str] = ["http", "https"]
    methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    paths: List[str]
    strip_path: bool = True
    preserve_host: bool = False

class KongPlugin(BaseModel):
    """Kong plugin definition"""
    name: str
    service_name: Optional[str] = None
    route_name: Optional[str] = None
    config: Dict[str, Any]
    enabled: bool = True

class KongConsumer(BaseModel):
    """Kong consumer definition"""
    username: str
    custom_id: Optional[str] = None
    tags: List[str] = []

class KongACLGroup(BaseModel):
    """Kong ACL group definition"""
    group: str
    consumer_name: str

class KongClient:
    """
    Kong API Gateway Management Client
    Handles service, route, plugin, and consumer management
    """

    def __init__(self):
        self.enable_kong = os.getenv("ENABLE_KONG", "false").lower() == "true"
        self.kong_url = os.getenv("KONG_URL", "http://kong:8000")
        self.kong_admin_url = os.getenv("KONG_ADMIN_URL", "http://kong:8001")
        self.timeout = int(os.getenv("KONG_TIMEOUT", "30"))
        
        # Kong configuration
        self.oidc_plugin_enabled = os.getenv("KONG_OIDC_PLUGIN", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("KONG_RATE_LIMIT_PER_MINUTE", "1000"))
        self.request_size_limit_mb = int(os.getenv("KONG_REQUEST_SIZE_LIMIT_MB", "10"))
        
        # HTTP client for Kong Admin API
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.kong_admin_url
        )

        logger.info(f"Kong Client initialized", extra={
            "enabled": self.enable_kong,
            "kong_url": self.kong_url,
            "kong_admin_url": self.kong_admin_url,
            "oidc_enabled": self.oidc_plugin_enabled
        })

    async def health_check(self) -> Dict[str, Any]:
        """Check Kong service health"""
        try:
            if not self.enable_kong:
                return {
                    "status": "disabled",
                    "kong_enabled": False,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Check Kong Admin API
            response = await self.http_client.get("/")
            kong_status = "healthy" if response.status_code == 200 else "unhealthy"

            # Check Kong Gateway
            gateway_response = await self.http_client.get("/status")
            gateway_status = "healthy" if gateway_response.status_code == 200 else "unhealthy"

            return {
                "status": "healthy" if kong_status == "healthy" and gateway_status == "healthy" else "degraded",
                "kong_enabled": self.enable_kong,
                "admin_api": kong_status,
                "gateway": gateway_status,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Kong health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def create_service(self, service: KongService) -> Dict[str, Any]:
        """Create a Kong service"""
        try:
            service_data = {
                "name": service.name,
                "url": service.url,
                "protocol": service.protocol,
                "host": service.host,
                "port": service.port,
                "connect_timeout": service.connect_timeout,
                "write_timeout": service.write_timeout,
                "read_timeout": service.read_timeout
            }
            
            if service.path:
                service_data["path"] = service.path

            response = await self.http_client.post("/services", json=service_data)
            response.raise_for_status()
            
            logger.info(f"Kong service created: {service.name}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to create Kong service {service.name}: {str(e)}")
            raise

    async def create_route(self, route: KongRoute) -> Dict[str, Any]:
        """Create a Kong route"""
        try:
            route_data = {
                "name": route.name,
                "service": {"name": route.service_name},
                "protocols": route.protocols,
                "methods": route.methods,
                "paths": route.paths,
                "strip_path": route.strip_path,
                "preserve_host": route.preserve_host
            }

            response = await self.http_client.post("/routes", json=route_data)
            response.raise_for_status()
            
            logger.info(f"Kong route created: {route.name}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to create Kong route {route.name}: {str(e)}")
            raise

    async def create_plugin(self, plugin: KongPlugin) -> Dict[str, Any]:
        """Create a Kong plugin"""
        try:
            plugin_data = {
                "name": plugin.name,
                "config": plugin.config,
                "enabled": plugin.enabled
            }

            if plugin.service_name:
                plugin_data["service"] = {"name": plugin.service_name}
            if plugin.route_name:
                plugin_data["route"] = {"name": plugin.route_name}

            response = await self.http_client.post("/plugins", json=plugin_data)
            response.raise_for_status()
            
            logger.info(f"Kong plugin created: {plugin.name}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to create Kong plugin {plugin.name}: {str(e)}")
            raise

    async def create_consumer(self, consumer: KongConsumer) -> Dict[str, Any]:
        """Create a Kong consumer"""
        try:
            consumer_data = {
                "username": consumer.username,
                "tags": consumer.tags
            }
            
            if consumer.custom_id:
                consumer_data["custom_id"] = consumer.custom_id

            response = await self.http_client.post("/consumers", json=consumer_data)
            response.raise_for_status()
            
            logger.info(f"Kong consumer created: {consumer.username}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to create Kong consumer {consumer.username}: {str(e)}")
            raise

    async def create_acl_group(self, acl_group: KongACLGroup) -> Dict[str, Any]:
        """Create a Kong ACL group"""
        try:
            acl_data = {
                "group": acl_group.group,
                "consumer": {"username": acl_group.consumer_name}
            }

            response = await self.http_client.post(f"/consumers/{acl_group.consumer_name}/acls", json=acl_data)
            response.raise_for_status()
            
            logger.info(f"Kong ACL group created: {acl_group.group} for {acl_group.consumer_name}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to create Kong ACL group {acl_group.group}: {str(e)}")
            raise

    async def setup_omnify_gateway(self) -> Dict[str, Any]:
        """Setup complete OmniFy API gateway configuration"""
        try:
            results = {
                "services": [],
                "routes": [],
                "plugins": [],
                "consumers": [],
                "acl_groups": []
            }

            # Create OmniFy API service
            omnify_service = KongService(
                name="omnify-api",
                url="http://omnify-api:8000",
                protocol="http",
                host="omnify-api",
                port=8000,
                path="/"
            )
            
            service_result = await self.create_service(omnify_service)
            results["services"].append(service_result)

            # Create API routes
            api_routes = [
                KongRoute(
                    name="omnify-api-all",
                    service_name="omnify-api",
                    paths=["/api/"],
                    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
                ),
                KongRoute(
                    name="omnify-auth",
                    service_name="omnify-api",
                    paths=["/api/auth/"],
                    methods=["GET", "POST", "PUT", "DELETE"]
                ),
                KongRoute(
                    name="omnify-agentkit",
                    service_name="omnify-api",
                    paths=["/api/agentkit/"],
                    methods=["GET", "POST", "PUT", "DELETE"]
                ),
                KongRoute(
                    name="omnify-eyes",
                    service_name="omnify-api",
                    paths=["/api/eyes/"],
                    methods=["GET", "POST", "PUT", "DELETE"]
                ),
                KongRoute(
                    name="omnify-health",
                    service_name="omnify-api",
                    paths=["/health", "/api/info"],
                    methods=["GET"]
                )
            ]

            for route in api_routes:
                route_result = await self.create_route(route)
                results["routes"].append(route_result)

            # Create plugins
            plugins = []

            # OIDC Plugin (if enabled)
            if self.oidc_plugin_enabled:
                oidc_plugin = KongPlugin(
                    name="oidc",
                    service_name="omnify-api",
                    config={
                        "client_id": os.getenv("KEYCLOAK_CLIENT_ID", "omnify-api"),
                        "client_secret": os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
                        "discovery": f"{os.getenv('KEYCLOAK_ISSUER_URL', 'http://keycloak:8080')}/realms/{os.getenv('KEYCLOAK_REALM', 'omnify')}/.well-known/openid_configuration",
                        "introspection_endpoint": f"{os.getenv('KEYCLOAK_ISSUER_URL', 'http://keycloak:8080')}/realms/{os.getenv('KEYCLOAK_REALM', 'omnify')}/protocol/openid-connect/token/introspect",
                        "bearer_only": "yes",
                        "realm": os.getenv("KEYCLOAK_REALM", "omnify"),
                        "scope": "openid email profile",
                        "ssl_verify": os.getenv("KEYCLOAK_VERIFY_SSL", "true").lower() == "true"
                    }
                )
                plugins.append(oidc_plugin)

            # Rate Limiting Plugin
            rate_limit_plugin = KongPlugin(
                name="rate-limiting",
                service_name="omnify-api",
                config={
                    "minute": self.rate_limit_per_minute,
                    "hour": self.rate_limit_per_minute * 60,
                    "day": self.rate_limit_per_minute * 60 * 24,
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False
                }
            )
            plugins.append(rate_limit_plugin)

            # Request Size Limiting Plugin
            request_size_plugin = KongPlugin(
                name="request-size-limiting",
                service_name="omnify-api",
                config={
                    "allowed_payload_size": self.request_size_limit_mb * 1024 * 1024,  # Convert MB to bytes
                    "size_unit": "bytes",
                    "require_content_length": True
                }
            )
            plugins.append(request_size_plugin)

            # CORS Plugin
            cors_plugin = KongPlugin(
                name="cors",
                service_name="omnify-api",
                config={
                    "origins": ["*"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                    "headers": ["Accept", "Accept-Version", "Content-Length", "Content-MD5", "Content-Type", "Date", "X-Auth-Token", "Authorization"],
                    "exposed_headers": ["X-Auth-Token"],
                    "credentials": True,
                    "max_age": 3600,
                    "preflight_continue": False
                }
            )
            plugins.append(cors_plugin)

            # Prometheus Plugin for metrics
            prometheus_plugin = KongPlugin(
                name="prometheus",
                service_name="omnify-api",
                config={
                    "per_consumer": True,
                    "status_code_metrics": True,
                    "latency_metrics": True,
                    "bandwidth_metrics": True,
                    "upstream_health_metrics": True
                }
            )
            plugins.append(prometheus_plugin)

            # Create plugins
            for plugin in plugins:
                plugin_result = await self.create_plugin(plugin)
                results["plugins"].append(plugin_result)

            # Create consumers for different plan tiers
            consumers = [
                KongConsumer(
                    username="free-tier",
                    custom_id="free-tier",
                    tags=["plan:free", "tier:basic"]
                ),
                KongConsumer(
                    username="pro-tier",
                    custom_id="pro-tier",
                    tags=["plan:pro", "tier:professional"]
                ),
                KongConsumer(
                    username="enterprise-tier",
                    custom_id="enterprise-tier",
                    tags=["plan:enterprise", "tier:enterprise"]
                )
            ]

            for consumer in consumers:
                consumer_result = await self.create_consumer(consumer)
                results["consumers"].append(consumer_result)

            # Create ACL groups for plan-based access
            acl_groups = [
                KongACLGroup(group="free", consumer_name="free-tier"),
                KongACLGroup(group="pro", consumer_name="pro-tier"),
                KongACLGroup(group="enterprise", consumer_name="enterprise-tier")
            ]

            for acl_group in acl_groups:
                acl_result = await self.create_acl_group(acl_group)
                results["acl_groups"].append(acl_result)

            logger.info("OmniFy Kong gateway setup completed successfully")
            return results

        except Exception as e:
            logger.error(f"Failed to setup OmniFy Kong gateway: {str(e)}")
            raise

    async def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """Get service statistics from Kong"""
        try:
            response = await self.http_client.get(f"/services/{service_name}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get service stats for {service_name}: {str(e)}")
            raise

    async def get_route_stats(self, route_name: str) -> Dict[str, Any]:
        """Get route statistics from Kong"""
        try:
            response = await self.http_client.get(f"/routes/{route_name}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get route stats for {route_name}: {str(e)}")
            raise

    async def get_plugin_stats(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin statistics from Kong"""
        try:
            response = await self.http_client.get(f"/plugins/{plugin_name}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get plugin stats for {plugin_name}: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

# Global instance
kong_client = KongClient()
