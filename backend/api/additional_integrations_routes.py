"""
Additional Integrations API Routes
Production-grade API endpoints for additional integrations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from backend.services.additional_integrations_service import (
    get_additional_integrations_service, AdditionalIntegrationsService,
    PlatformType, IntegrationType, IntegrationStatus
)
from backend.core.database import get_database
from backend.core.redis_client import get_redis_client
from backend.core.auth import get_current_user
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/additional-integrations", tags=["Additional Integrations"])

@router.get("/dashboard")
async def get_integration_dashboard(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get additional integrations dashboard"""
    try:
        service = get_additional_integrations_service(db, redis_client)
        dashboard = await service.get_integration_dashboard(organization_id)
        
        return JSONResponse(content=dashboard)
        
    except Exception as e:
        logger.error(f"Error getting integration dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations")
async def create_integration(
    integration_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Create new integration"""
    try:
        service = get_additional_integrations_service(db, redis_client)
        
        # Add organization_id
        integration_data["organization_id"] = current_user.organization_id
        
        integration_id = await service.create_integration(integration_data)
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "message": "Integration created successfully",
            "status": "created"
        })
        
    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/test")
async def test_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Test integration connection"""
    try:
        service = get_additional_integrations_service(db, redis_client)
        
        result = await service.test_integration(integration_id)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/sync")
async def sync_integration_data(
    integration_id: str,
    sync_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Sync data with integration"""
    try:
        service = get_additional_integrations_service(db, redis_client)
        
        operation = sync_request["operation"]
        data = sync_request.get("data")
        
        # Run sync in background
        async def sync_task():
            return await service.sync_data(integration_id, operation, data)
        
        background_tasks.add_task(sync_task)
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "operation": operation,
            "message": "Sync operation started",
            "status": "started"
        })
        
    except Exception as e:
        logger.error(f"Error syncing integration data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integrations")
async def list_integrations(
    organization_id: str,
    platform_type: Optional[str] = None,
    integration_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """List integrations"""
    try:
        service = get_additional_integrations_service(db, redis_client)
        
        integrations = await service.get_integrations(organization_id, platform_type)
        
        # Apply filters
        if integration_type:
            integrations = [i for i in integrations if i.get("integration_type") == integration_type]
        if status:
            integrations = [i for i in integrations if i.get("status") == status]
        
        # Apply pagination
        total_count = len(integrations)
        integrations = integrations[offset:offset + limit]
        
        return JSONResponse(content={
            "integrations": integrations,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        logger.error(f"Error listing integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integrations/{integration_id}")
async def get_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get integration details"""
    try:
        integration = await db.additional_integrations.find_one({"integration_id": integration_id})
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return JSONResponse(content=integration)
        
    except Exception as e:
        logger.error(f"Error getting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/integrations/{integration_id}")
async def update_integration(
    integration_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Update integration"""
    try:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.additional_integrations.update_one(
            {"integration_id": integration_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "message": "Integration updated successfully",
            "status": "updated"
        })
        
    except Exception as e:
        logger.error(f"Error updating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Delete integration"""
    try:
        result = await db.additional_integrations.delete_one({"integration_id": integration_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "message": "Integration deleted successfully",
            "status": "deleted"
        })
        
    except Exception as e:
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integrations/{integration_id}/sync-results")
async def get_sync_results(
    integration_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get sync results for integration"""
    try:
        sync_results = await db.sync_results.find({
            "integration_id": integration_id
        }).sort("started_at", -1).limit(limit).to_list(length=None)
        
        return JSONResponse(content={
            "sync_results": sync_results,
            "total_count": len(sync_results),
            "limit": limit
        })
        
    except Exception as e:
        logger.error(f"Error getting sync results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/webhook")
async def handle_webhook(
    integration_id: str,
    webhook_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Handle webhook from integration"""
    try:
        # Store webhook data
        webhook_doc = {
            "integration_id": integration_id,
            "webhook_data": webhook_data,
            "received_at": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        await db.webhook_events.insert_one(webhook_doc)
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "message": "Webhook received successfully",
            "status": "received"
        })
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms")
async def get_supported_platforms():
    """Get supported platforms and integration types"""
    return JSONResponse(content={
        "platforms": [pt.value for pt in PlatformType],
        "integration_types": [it.value for it in IntegrationType],
        "statuses": [st.value for st in IntegrationStatus]
    })

@router.get("/platforms/{platform_type}/capabilities")
async def get_platform_capabilities(
    platform_type: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get platform capabilities"""
    try:
        capabilities = {
            PlatformType.SALESFORCE.value: {
                "operations": ["get_contacts", "create_contact", "update_contact", "get_leads", "create_lead"],
                "data_types": ["contacts", "leads", "opportunities", "accounts"],
                "authentication": ["oauth2", "api_key"],
                "rate_limits": {"requests_per_hour": 15000}
            },
            PlatformType.HUBSPOT.value: {
                "operations": ["get_contacts", "create_contact", "update_contact", "get_companies", "create_company"],
                "data_types": ["contacts", "companies", "deals", "tickets"],
                "authentication": ["oauth2", "api_key"],
                "rate_limits": {"requests_per_day": 100000}
            },
            PlatformType.MAILCHIMP.value: {
                "operations": ["get_lists", "add_subscriber", "remove_subscriber", "get_campaigns", "create_campaign"],
                "data_types": ["lists", "subscribers", "campaigns", "automations"],
                "authentication": ["api_key"],
                "rate_limits": {"requests_per_hour": 1000}
            },
            PlatformType.WORDPRESS.value: {
                "operations": ["get_posts", "create_post", "update_post", "get_pages", "create_page"],
                "data_types": ["posts", "pages", "comments", "users"],
                "authentication": ["basic_auth", "oauth2"],
                "rate_limits": {"requests_per_minute": 60}
            },
            PlatformType.WOOCOMMERCE.value: {
                "operations": ["get_products", "create_product", "get_orders", "create_order", "get_customers"],
                "data_types": ["products", "orders", "customers", "categories"],
                "authentication": ["consumer_key", "consumer_secret"],
                "rate_limits": {"requests_per_minute": 60}
            },
            PlatformType.TWILIO.value: {
                "operations": ["send_sms", "send_voice", "get_messages", "get_calls"],
                "data_types": ["messages", "calls", "phone_numbers"],
                "authentication": ["account_sid", "auth_token"],
                "rate_limits": {"requests_per_second": 100}
            },
            PlatformType.SLACK.value: {
                "operations": ["send_message", "get_channels", "get_users", "create_channel"],
                "data_types": ["messages", "channels", "users", "files"],
                "authentication": ["bot_token", "oauth2"],
                "rate_limits": {"requests_per_minute": 1000}
            },
            PlatformType.GOOGLE_ANALYTICS.value: {
                "operations": ["get_analytics_data", "get_reports", "get_audiences"],
                "data_types": ["analytics", "reports", "audiences", "goals"],
                "authentication": ["oauth2"],
                "rate_limits": {"requests_per_day": 10000}
            },
            PlatformType.ZAPIER.value: {
                "operations": ["trigger_webhook", "create_zap", "get_zaps"],
                "data_types": ["webhooks", "zaps", "triggers", "actions"],
                "authentication": ["webhook_url", "api_key"],
                "rate_limits": {"requests_per_minute": 100}
            }
        }
        
        platform_capabilities = capabilities.get(platform_type, {})
        
        return JSONResponse(content={
            "platform_type": platform_type,
            "capabilities": platform_capabilities
        })
        
    except Exception as e:
        logger.error(f"Error getting platform capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/credentials/validate")
async def validate_credentials(
    integration_id: str,
    credentials: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Validate integration credentials"""
    try:
        # Get integration
        integration = await db.additional_integrations.find_one({"integration_id": integration_id})
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        platform_type = integration["platform_type"]
        
        # Validate credentials based on platform type
        validation_result = {"valid": True, "errors": []}
        
        if platform_type == PlatformType.SALESFORCE.value:
            required_fields = ["instance_url", "access_token"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
        
        elif platform_type == PlatformType.HUBSPOT.value:
            if "api_key" not in credentials or not credentials["api_key"]:
                validation_result["errors"].append("Missing required field: api_key")
                validation_result["valid"] = False
        
        elif platform_type == PlatformType.MAILCHIMP.value:
            if "api_key" not in credentials or not credentials["api_key"]:
                validation_result["errors"].append("Missing required field: api_key")
                validation_result["valid"] = False
        
        elif platform_type == PlatformType.WORDPRESS.value:
            required_fields = ["base_url", "username", "password"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
        
        elif platform_type == PlatformType.WOOCOMMERCE.value:
            required_fields = ["base_url", "consumer_key", "consumer_secret"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
        
        elif platform_type == PlatformType.TWILIO.value:
            required_fields = ["account_sid", "auth_token", "phone_number"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
        
        elif platform_type == PlatformType.SLACK.value:
            if "bot_token" not in credentials or not credentials["bot_token"]:
                validation_result["errors"].append("Missing required field: bot_token")
                validation_result["valid"] = False
        
        elif platform_type == PlatformType.GOOGLE_ANALYTICS.value:
            required_fields = ["access_token", "property_id"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
        
        elif platform_type == PlatformType.ZAPIER.value:
            if "webhook_url" not in credentials or not credentials["webhook_url"]:
                validation_result["errors"].append("Missing required field: webhook_url")
                validation_result["valid"] = False
        
        return JSONResponse(content={
            "integration_id": integration_id,
            "platform_type": platform_type,
            "validation_result": validation_result
        })
        
    except Exception as e:
        logger.error(f"Error validating credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks")
async def get_webhook_events(
    integration_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get webhook events"""
    try:
        query = {}
        if integration_id:
            query["integration_id"] = integration_id
        
        webhook_events = await db.webhook_events.find(query).sort("received_at", -1).limit(limit).to_list(length=None)
        
        return JSONResponse(content={
            "webhook_events": webhook_events,
            "total_count": len(webhook_events),
            "limit": limit
        })
        
    except Exception as e:
        logger.error(f"Error getting webhook events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
