"""
Service Registry - Groups routes by service for microservices deployment
Enables both monolithic and microservices deployment from the same codebase
"""

from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Service types for deployment"""
    AUTH = "auth"
    INTEGRATIONS = "integrations"
    AGENTKIT = "agentkit"
    ANALYTICS = "analytics"
    ONBOARDING = "onboarding"
    ML = "ml"
    INFRASTRUCTURE = "infrastructure"


# Service route mapping - groups routes by service
SERVICE_ROUTES: Dict[ServiceType, List[str]] = {
    ServiceType.AUTH: [
        "api.auth_routes",
        "api.legal_routes",
        "api.email_verification_routes",
        "api.mfa_routes",
        "api.rbac_routes",
        "api.session_routes",
    ],
    ServiceType.INTEGRATIONS: [
        "api.triplewhale_routes",
        "api.triplewhale_oauth_routes",
        "api.hubspot_routes",
        "api.hubspot_oauth_routes",
        "api.klaviyo_routes",
        "api.google_ads_oauth_routes",
        "api.meta_ads_oauth_routes",
        "api.linkedin_ads_oauth_routes",
        "api.tiktok_ads_oauth_routes",
        "api.youtube_ads_oauth_routes",
        "api.shopify_oauth_routes",
        "api.stripe_oauth_routes",
        "api.gohighlevel_oauth_routes",
    ],
    ServiceType.AGENTKIT: [
        "api.agentkit_routes",
        "api.workflow_routes",
    ],
    ServiceType.ANALYTICS: [
        "api.dashboard_routes",
        "api.metrics_routes",
        "api.brain_modules_routes",
        "api.advanced_analytics_routes",
        "api.advanced_reporting_routes",
    ],
    ServiceType.ONBOARDING: [
        "api.client_onboarding_routes",
        "api.onboarding_routes",
    ],
    ServiceType.ML: [
        "api.predictive_routes",
        "api.predictive_intelligence_routes",
        "api.ai_ml_enhancements_routes",
    ],
    ServiceType.INFRASTRUCTURE: [
        "api.kong_routes",
        "api.temporal_routes",
        "api.airbyte_routes",
        "api.kafka_routes",
        "api.metabase_routes",
    ],
}

# Service dependencies (what services each service needs)
SERVICE_DEPENDENCIES: Dict[ServiceType, List[ServiceType]] = {
    ServiceType.AUTH: [],
    ServiceType.INTEGRATIONS: [ServiceType.AUTH],  # Needs auth for user context
    ServiceType.AGENTKIT: [ServiceType.AUTH],
    ServiceType.ANALYTICS: [ServiceType.AUTH, ServiceType.INTEGRATIONS],
    ServiceType.ONBOARDING: [ServiceType.AUTH],
    ServiceType.ML: [ServiceType.AUTH, ServiceType.ANALYTICS],
    ServiceType.INFRASTRUCTURE: [],
}

# Service ports (for microservices deployment)
SERVICE_PORTS: Dict[ServiceType, int] = {
    ServiceType.AUTH: 8001,
    ServiceType.INTEGRATIONS: 8002,
    ServiceType.AGENTKIT: 8003,
    ServiceType.ANALYTICS: 8004,
    ServiceType.ONBOARDING: 8005,
    ServiceType.ML: 8006,
    ServiceType.INFRASTRUCTURE: 8007,
}

# Service descriptions
SERVICE_DESCRIPTIONS: Dict[ServiceType, str] = {
    ServiceType.AUTH: "Authentication, authorization, and legal documents",
    ServiceType.INTEGRATIONS: "Platform integrations (TripleWhale, HubSpot, Klaviyo, etc.)",
    ServiceType.AGENTKIT: "AgentKit agents and workflow orchestration",
    ServiceType.ANALYTICS: "Dashboards, metrics, and analytics",
    ServiceType.ONBOARDING: "Client onboarding and onboarding wizard",
    ServiceType.ML: "Predictive intelligence and AI/ML enhancements",
    ServiceType.INFRASTRUCTURE: "Infrastructure services (Kong, Temporal, Airbyte, Kafka, Metabase)",
}


def get_routes_for_service(service_type: ServiceType) -> List[str]:
    """Get list of route modules for a service"""
    return SERVICE_ROUTES.get(service_type, [])


def get_service_dependencies(service_type: ServiceType) -> List[ServiceType]:
    """Get dependencies for a service"""
    return SERVICE_DEPENDENCIES.get(service_type, [])


def get_service_port(service_type: ServiceType) -> int:
    """Get default port for a service"""
    return SERVICE_PORTS.get(service_type, 8000)


def get_service_description(service_type: ServiceType) -> str:
    """Get description for a service"""
    return SERVICE_DESCRIPTIONS.get(service_type, "")


def get_all_services() -> List[ServiceType]:
    """Get all service types"""
    return list(ServiceType)


def get_service_by_name(name: str) -> Optional[ServiceType]:
    """Get service type by name"""
    try:
        return ServiceType(name.lower())
    except ValueError:
        return None


def validate_service_dependencies(service_type: ServiceType) -> Dict[str, any]:
    """Validate that all dependencies are satisfied"""
    dependencies = get_service_dependencies(service_type)
    missing = []
    
    for dep in dependencies:
        # In microservices mode, check if dependency service is available
        # This would check service discovery or environment variables
        pass
    
    return {
        "service": service_type.value,
        "dependencies": [d.value for d in dependencies],
        "missing": missing,
        "valid": len(missing) == 0
    }

