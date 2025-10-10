"""
Comprehensive API Documentation for OmnifyProduct
OpenAPI/Swagger documentation with complete endpoint specifications
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our application
from agentkit_server import app
from services.auth_service import get_current_user, AuthService
from services.agentkit_service import AgentKitService
from services.validation_service import ValidationService
from models.agentkit_models import (
    AgentConfig, WorkflowDefinition, AgentExecutionRequest, AgentExecutionResponse,
    WorkflowExecution, ComplianceCheck, AgentStatus, WorkflowStatus
)


def custom_openapi():
    """
    Generate custom OpenAPI schema for OmnifyProduct
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="OmnifyProduct API",
        version="2.0.0",
        description="""
        # OmnifyProduct API

        **OmnifyProduct** is an enterprise-grade platform that leverages OpenAI's AgentKit for intelligent workflow orchestration and marketing automation.

        ## Features

        - **AgentKit-First Architecture**: Built on OpenAI's enterprise agent platform
        - **Workflow Orchestration**: Advanced multi-step workflows with dependency management
        - **Real-time Analytics**: Performance tracking and predictive insights
        - **SOC 2 Compliance**: Built-in audit logging and data retention
        - **Multi-platform Integration**: Google Ads, Meta Ads, LinkedIn Ads, and more

        ## Authentication

        All API endpoints require authentication via JWT tokens. Include the token in the Authorization header:

        ```
        Authorization: Bearer <your_jwt_token>
        ```

        ## Rate Limits

        - Standard tier: 100 requests/minute
        - Professional tier: 1000 requests/minute
        - Enterprise tier: 10000 requests/minute

        ## Support

        For support, contact: support@omnifyproduct.com

        ## License

        © 2024 OmnifyProduct. All rights reserved.
        """,
        routes=app.routes,
        servers=[
            {"url": "https://api.omnifyproduct.com", "description": "Production server"},
            {"url": "https://staging.omnifyproduct.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ],
        tags=[
            {
                "name": "health",
                "description": "Health check and system information"
            },
            {
                "name": "organizations",
                "description": "Organization management and setup"
            },
            {
                "name": "agents",
                "description": "AgentKit agent management"
            },
            {
                "name": "workflows",
                "description": "Workflow orchestration and execution"
            },
            {
                "name": "compliance",
                "description": "Compliance checking and audit logs"
            },
            {
                "name": "analytics",
                "description": "Performance metrics and analytics"
            }
        ],
        contact={
            "name": "OmnifyProduct Support",
            "url": "https://omnifyproduct.com/support",
            "email": "support@omnifyproduct.com"
        },
        license_info={
            "name": "Proprietary",
            "url": "https://omnifyproduct.com/legal"
        }
    )

    # Add custom security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Authorization header using the Bearer scheme"
        }
    }

    # Apply security to all endpoints
    for path_data in openapi_schema["paths"].values():
        for operation in path_data.values():
            if "security" not in operation:
                operation["security"] = [{"BearerAuth": []}]

    # Add custom response schemas
    openapi_schema["components"]["schemas"].update({
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"},
                "details": {"type": "object", "nullable": True},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["error", "message", "timestamp"]
        },
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["success", "timestamp"]
        }
    })

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/docs", include_in_schema=False)
async def get_documentation():
    """Get API documentation"""
    return get_swagger_ui_html(openapi_url="/openapi.json", title="OmnifyProduct API")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    """Get ReDoc API documentation"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OmnifyProduct API Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """)


# Additional endpoints for API documentation and discovery

@app.get("/api/info", tags=["health"])
async def get_api_info():
    """Get comprehensive API information"""
    return {
        "name": "OmnifyProduct API",
        "version": "2.0.0",
        "description": "Enterprise-grade marketing automation with AgentKit integration",
        "features": [
            "AgentKit-First Architecture",
            "Advanced Workflow Orchestration",
            "Real-time Analytics",
            "SOC 2 Compliance",
            "Multi-platform Integration"
        ],
        "supported_platforms": [
            "Google Ads",
            "Meta Ads",
            "LinkedIn Ads",
            "TikTok Ads"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "contact": {
            "support_email": "support@omnifyproduct.com",
            "documentation_url": "https://docs.omnifyproduct.com"
        }
    }


@app.get("/api/endpoints", tags=["health"])
async def get_api_endpoints():
    """Get list of all available API endpoints"""
    endpoints = []

    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            endpoint_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', None),
                "summary": getattr(route, 'summary', None),
                "description": getattr(route, 'description', None),
                "tags": getattr(route, 'tags', [])
            }
            endpoints.append(endpoint_info)

    return {
        "total_endpoints": len(endpoints),
        "endpoints": sorted(endpoints, key=lambda x: x["path"])
    }


@app.get("/api/health/detailed", tags=["health"])
async def get_detailed_health(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed system health (requires authentication)"""
    # This would integrate with the database health checker
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": {"status": "operational", "version": "2.0.0"},
            "database": {"status": "operational", "connections": "active"},
            "agentkit": {"status": "operational", "mode": "simulation"},
            "redis": {"status": "operational", "memory_used": "45MB"}
        },
        "performance": {
            "response_time_ms": 45,
            "uptime_seconds": 86400,
            "requests_per_minute": 150
        },
        "organization": {
            "id": current_user.get("organization_id"),
            "agents_count": 4,
            "workflows_count": 2,
            "recent_executions": 15
        }
    }


# Example endpoint implementations with comprehensive documentation

@app.post(
    "/api/agentkit/agents",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Create a new AgentKit agent",
    description="""
    Create a new AgentKit agent for workflow orchestration.

    **Agent Types:**
    - `creative_intelligence`: Analyzes creative assets and provides AIDA optimization
    - `marketing_automation`: Automates campaign creation and deployment
    - `client_management`: Manages client relationships and success metrics
    - `analytics`: Provides real-time analytics and performance insights

    **Required Fields:**
    - `name`: Human-readable agent name
    - `agent_type`: One of the supported agent types
    - `config`: Agent-specific configuration object

    **Example Request:**
    ```json
    {
      "name": "Creative Intelligence Agent",
      "agent_type": "creative_intelligence",
      "description": "Analyzes creative assets for AIDA optimization",
      "config": {
        "analysis_types": ["aida", "brand_compliance"],
        "platforms": ["google_ads", "meta_ads"],
        "auto_optimize": true
      }
    }
    ```

    **Example Response:**
    ```json
    {
      "agent_id": "org_creative_intelligence",
      "status": "created",
      "agentkit_agent_id": "agent_abc123def456",
      "created_at": "2024-01-15T10:30:00Z"
    }
    ```
    """,
    response_description="Agent creation result",
    responses={
        200: {
            "description": "Agent created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "agent_id": "org_creative_intelligence",
                        "status": "created",
                        "agentkit_agent_id": "agent_abc123def456"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation Error",
                        "message": "Invalid agent type",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Error",
                        "message": "Valid JWT token required",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    },
    tags=["agents"]
)
async def create_agent(
    agent_config: AgentConfig,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new AgentKit agent"""
    # Implementation would go here
    return {"agent_id": agent_config.agent_id, "status": "created"}


@app.post(
    "/api/agentkit/workflows",
    response_model=Dict[str, Any],
    summary="Create a new workflow",
    description="""
    Create a complex workflow with multiple steps and dependencies.

    **Workflow Steps:**
    Each step must have:
    - `step_id`: Unique identifier for the step
    - `agent_type`: Agent to execute for this step
    - `input_mapping`: Map workflow data to agent input
    - `output_mapping`: Map agent output to workflow data

    **Dependencies:**
    Use `depends_on` to specify step dependencies:
    ```json
    {
      "step_id": "campaign_creation",
      "agent_type": "marketing_automation",
      "depends_on": ["creative_analysis"],
      "input_mapping": {
        "aida_scores": "campaign_aida_scores"
      }
    }
    ```

    **Example Workflow:**
    ```json
    {
      "name": "Campaign Launch Workflow",
      "description": "Complete campaign creation process",
      "steps": [
        {
          "step_id": "creative_analysis",
          "agent_type": "creative_intelligence",
          "input_mapping": {"asset_url": "campaign_creative_url"},
          "output_mapping": {"aida_scores": "campaign_aida_scores"}
        },
        {
          "step_id": "campaign_creation",
          "agent_type": "marketing_automation",
          "depends_on": ["creative_analysis"],
          "input_mapping": {"aida_scores": "campaign_aida_scores"},
          "output_mapping": {"platform_campaign_ids": "deployment_results"}
        }
      ]
    }
    ```
    """,
    tags=["workflows"]
)
async def create_workflow(
    workflow: WorkflowDefinition,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new workflow"""
    # Implementation would go here
    return {"workflow_id": workflow.workflow_id, "status": "created"}


@app.post(
    "/api/agentkit/compliance/check",
    response_model=ComplianceCheck,
    summary="Run compliance check",
    description="""
    Run SOC 2 compliance check for the organization.

    **Check Types:**
    - `soc2`: Full SOC 2 Type II compliance check
    - `security`: Security configuration audit
    - `data_retention`: Data retention policy validation
    - `audit_logging`: Audit log completeness check

    **Findings:**
    Each finding includes:
    - `severity`: `high`, `medium`, `low`, or `info`
    - `message`: Human-readable description
    - `category`: Compliance category
    - `recommendations`: Suggested remediation steps

    **Example Response:**
    ```json
    {
      "check_id": "check_abc123def456",
      "organization_id": "org_123",
      "check_type": "soc2",
      "status": "passed",
      "findings": [
        {
          "severity": "info",
          "message": "7-day data retention policy active",
          "category": "data_retention",
          "recommendations": []
        }
      ],
      "recommendations": [],
      "checked_at": "2024-01-15T10:30:00Z",
      "next_check_at": "2024-02-15T10:30:00Z"
    }
    ```
    """,
    tags=["compliance"]
)
async def run_compliance_check(
    organization_id: str,
    check_type: str = "soc2",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Run compliance check"""
    # Implementation would go here
    return ComplianceCheck(
        check_id="check_123",
        organization_id=organization_id,
        check_type=check_type,
        status="passed",
        findings=[],
        recommendations=[],
        checked_at=datetime.utcnow(),
        next_check_at=datetime.utcnow()
    )


# Update the FastAPI app to use our custom OpenAPI schema
app.openapi = custom_openapi


# Add custom middleware for API documentation tracking
@app.middleware("http")
async def add_api_documentation_headers(request, call_next):
    """Add custom headers for API documentation"""
    response = await call_next(request)

    # Add documentation URLs in response headers
    response.headers["X-API-Docs"] = "/docs"
    response.headers["X-API-Redirect"] = "/redoc"
    response.headers["X-API-Info"] = "/api/info"

    return response
