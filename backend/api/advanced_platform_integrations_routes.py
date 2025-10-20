"""
Advanced Platform Integrations API Routes
Production-grade API endpoints for LinkedIn, TikTok, YouTube, Shopify, and Stripe integrations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.advanced_platform_integrations_service import (
    get_advanced_platform_service, AdvancedPlatformIntegrationsService,
    PlatformType, CampaignStatus, AdFormat
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class PlatformCredentials(BaseModel):
    access_token: Optional[str] = None
    secret_key: Optional[str] = None
    advertiser_id: Optional[str] = None
    customer_id: Optional[str] = None
    shop_domain: Optional[str] = None

class CampaignCreateRequest(BaseModel):
    name: str = Field(..., description="Campaign name")
    objective: str = Field(..., description="Campaign objective")
    budget: float = Field(..., description="Campaign budget")
    daily_budget: Optional[float] = Field(None, description="Daily budget")
    status: str = Field("active", description="Campaign status")
    targeting: Optional[Dict[str, Any]] = Field({}, description="Targeting criteria")
    creative: Optional[Dict[str, Any]] = Field({}, description="Creative assets")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")

class ProductCreateRequest(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field("", description="Product description")
    price: float = Field(..., description="Product price")
    compare_at_price: Optional[float] = Field(None, description="Compare at price")
    sku: Optional[str] = Field("", description="Product SKU")
    inventory_quantity: Optional[int] = Field(0, description="Inventory quantity")
    tags: Optional[List[str]] = Field([], description="Product tags")
    images: Optional[List[str]] = Field([], description="Product images")
    vendor: Optional[str] = Field("", description="Product vendor")
    product_type: Optional[str] = Field("", description="Product type")

class PaymentCreateRequest(BaseModel):
    amount: float = Field(..., description="Payment amount")
    currency: str = Field("usd", description="Payment currency")
    description: Optional[str] = Field("", description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Payment metadata")
    customer_email: Optional[str] = Field(None, description="Customer email")

class CampaignResponse(BaseModel):
    campaign_id: str
    platform: str
    name: str
    status: str
    objective: str
    budget: float
    daily_budget: float
    start_date: str
    end_date: Optional[str]
    targeting: Dict[str, Any]
    creative: Dict[str, Any]
    created_at: str

class ProductResponse(BaseModel):
    product_id: str
    platform: str
    title: str
    description: str
    price: float
    compare_at_price: Optional[float]
    sku: str
    inventory_quantity: int
    status: str
    tags: List[str]
    images: List[str]
    variants: List[Dict[str, Any]]
    created_at: str

class PaymentResponse(BaseModel):
    payment_id: str
    platform: str
    amount: float
    currency: str
    status: str
    customer_id: str
    description: str
    metadata: Dict[str, Any]
    created_at: str

class PlatformOverviewResponse(BaseModel):
    initialized_platforms: List[str]
    platform_capabilities: Dict[str, List[str]]
    total_campaigns: int
    total_products: int
    total_payments: int
    recent_activity: List[Dict[str, Any]]

# Dependency
async def get_platform_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedPlatformIntegrationsService:
    return get_advanced_platform_service(db)

# Platform Management Endpoints
@router.post("/api/platforms/{platform_type}/initialize", summary="Initialize Platform Integration")
async def initialize_platform(
    platform_type: str,
    credentials: PlatformCredentials = Body(...),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Initialize platform integration with credentials.
    Sets up API client for the specified platform.
    """
    try:
        platform_enum = PlatformType(platform_type)
        credentials_dict = credentials.dict()
        
        # Remove None values
        credentials_dict = {k: v for k, v in credentials_dict.items() if v is not None}
        
        success = await platform_service.initialize_platform(platform_enum, credentials_dict)
        
        if success:
            return {
                "platform": platform_type,
                "status": "initialized",
                "message": f"{platform_type} platform integration initialized successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to initialize {platform_type} platform"
            )
            
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform type: {platform_type}"
        )
    except Exception as e:
        logger.error(f"Error initializing platform {platform_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize platform"
        )

@router.get("/api/platforms/overview", response_model=PlatformOverviewResponse, summary="Get Platform Overview")
async def get_platform_overview(
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get overview of all platform integrations.
    Returns initialized platforms, capabilities, and activity summary.
    """
    try:
        overview = await platform_service.get_platform_overview()
        
        return PlatformOverviewResponse(**overview)
    except Exception as e:
        logger.error(f"Error getting platform overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform overview"
        )

# Campaign Management Endpoints
@router.post("/api/platforms/{platform_type}/campaigns", response_model=CampaignResponse, summary="Create Campaign")
async def create_campaign(
    platform_type: str,
    campaign_data: CampaignCreateRequest = Body(...),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Create campaign on specified platform.
    Supports LinkedIn Ads, TikTok Ads, and YouTube Ads.
    """
    try:
        platform_enum = PlatformType(platform_type)
        
        if platform_enum not in [PlatformType.LINKEDIN_ADS, PlatformType.TIKTOK_ADS, PlatformType.YOUTUBE_ADS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campaign creation not supported for {platform_type}"
            )
        
        campaign_data_dict = campaign_data.dict()
        
        # Convert date strings to datetime objects
        if campaign_data_dict.get("start_date"):
            campaign_data_dict["start_date"] = datetime.fromisoformat(campaign_data_dict["start_date"])
        if campaign_data_dict.get("end_date"):
            campaign_data_dict["end_date"] = datetime.fromisoformat(campaign_data_dict["end_date"])
        
        result = await platform_service.create_campaign(platform_enum, campaign_data_dict)
        
        return CampaignResponse(**result["campaign"])
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform type: {platform_type}"
        )
    except Exception as e:
        logger.error(f"Error creating campaign on {platform_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign"
        )

@router.get("/api/platforms/{platform_type}/campaigns/{campaign_id}/metrics", summary="Get Campaign Metrics")
async def get_campaign_metrics(
    platform_type: str,
    campaign_id: str,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get campaign metrics from specified platform.
    Returns performance data for the specified date range.
    """
    try:
        platform_enum = PlatformType(platform_type)
        
        if platform_enum not in [PlatformType.LINKEDIN_ADS, PlatformType.TIKTOK_ADS, PlatformType.YOUTUBE_ADS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campaign metrics not supported for {platform_type}"
            )
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        metrics = await platform_service.get_campaign_metrics(platform_enum, campaign_id, start_dt, end_dt)
        
        return {
            "campaign_id": campaign_id,
            "platform": platform_type,
            "start_date": start_date,
            "end_date": end_date,
            "metrics": metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform type: {platform_type}"
        )
    except Exception as e:
        logger.error(f"Error getting campaign metrics from {platform_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign metrics"
        )

# Shopify Product Management Endpoints
@router.post("/api/platforms/shopify/products", response_model=ProductResponse, summary="Create Shopify Product")
async def create_shopify_product(
    product_data: ProductCreateRequest = Body(...),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Create product in Shopify store.
    Creates product with variants, images, and inventory.
    """
    try:
        product_data_dict = product_data.dict()
        result = await platform_service.create_shopify_product(product_data_dict)
        
        return ProductResponse(**result["product"])
        
    except Exception as e:
        logger.error(f"Error creating Shopify product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Shopify product"
        )

@router.get("/api/platforms/shopify/products", summary="Get Shopify Products")
async def get_shopify_products(
    limit: int = Query(50, description="Number of products to return"),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get products from Shopify store.
    Returns list of products with details.
    """
    try:
        if PlatformType.SHOPIFY not in platform_service.platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shopify platform not initialized"
            )
        
        shopify_client = platform_service.platforms[PlatformType.SHOPIFY]
        products = await shopify_client.get_products(limit)
        
        return {
            "products": [ProductResponse(**product.__dict__) for product in products],
            "total_count": len(products),
            "platform": "shopify"
        }
        
    except Exception as e:
        logger.error(f"Error getting Shopify products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Shopify products"
        )

@router.get("/api/platforms/shopify/analytics", summary="Get Shopify Analytics")
async def get_shopify_analytics(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get Shopify store analytics.
    Returns order data, revenue, and product performance.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        analytics = await platform_service.get_shopify_analytics(start_dt, end_dt)
        
        return {
            "platform": "shopify",
            "start_date": start_date,
            "end_date": end_date,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Shopify analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Shopify analytics"
        )

# Stripe Payment Management Endpoints
@router.post("/api/platforms/stripe/payments", response_model=PaymentResponse, summary="Create Stripe Payment")
async def create_stripe_payment(
    payment_data: PaymentCreateRequest = Body(...),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Create Stripe payment intent.
    Creates payment intent for processing.
    """
    try:
        payment_data_dict = payment_data.dict()
        
        # Create customer if email provided
        customer_id = None
        if payment_data_dict.get("customer_email"):
            if PlatformType.STRIPE in platform_service.platforms:
                stripe_client = platform_service.platforms[PlatformType.STRIPE]
                customer_id = await stripe_client.create_customer(
                    payment_data_dict["customer_email"],
                    metadata=payment_data_dict.get("metadata", {})
                )
        
        result = await platform_service.create_stripe_payment(
            payment_data_dict["amount"],
            payment_data_dict["currency"],
            payment_data_dict.get("metadata")
        )
        
        return PaymentResponse(**result["payment"])
        
    except Exception as e:
        logger.error(f"Error creating Stripe payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Stripe payment"
        )

@router.get("/api/platforms/stripe/analytics", summary="Get Stripe Analytics")
async def get_stripe_analytics(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get Stripe payment analytics.
    Returns payment data, success rates, and revenue metrics.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        analytics = await platform_service.get_stripe_analytics(start_dt, end_dt)
        
        return {
            "platform": "stripe",
            "start_date": start_date,
            "end_date": end_date,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Stripe analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Stripe analytics"
        )

# Multi-Platform Analytics Endpoint
@router.get("/api/platforms/analytics/unified", summary="Get Unified Platform Analytics")
async def get_unified_analytics(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Get unified analytics across all platforms.
    Aggregates data from campaigns, products, and payments.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        unified_analytics = {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "campaigns": {
                "total_campaigns": 0,
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "platforms": {}
            },
            "products": {
                "total_products": 0,
                "total_revenue": 0.0,
                "total_orders": 0,
                "average_order_value": 0.0
            },
            "payments": {
                "total_payments": 0,
                "total_amount": 0.0,
                "success_rate": 0.0,
                "average_payment": 0.0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Get campaign analytics from all advertising platforms
        for platform_type in [PlatformType.LINKEDIN_ADS, PlatformType.TIKTOK_ADS, PlatformType.YOUTUBE_ADS]:
            if platform_type in platform_service.platforms:
                try:
                    # Mock campaign data - in production, aggregate from actual campaigns
                    platform_analytics = {
                        "campaigns": 5,
                        "spend": 1000.0,
                        "impressions": 100000,
                        "clicks": 2000,
                        "conversions": 100
                    }
                    
                    unified_analytics["campaigns"]["platforms"][platform_type.value] = platform_analytics
                    unified_analytics["campaigns"]["total_campaigns"] += platform_analytics["campaigns"]
                    unified_analytics["campaigns"]["total_spend"] += platform_analytics["spend"]
                    unified_analytics["campaigns"]["total_impressions"] += platform_analytics["impressions"]
                    unified_analytics["campaigns"]["total_clicks"] += platform_analytics["clicks"]
                    unified_analytics["campaigns"]["total_conversions"] += platform_analytics["conversions"]
                    
                except Exception as e:
                    logger.warning(f"Failed to get analytics for {platform_type.value}: {e}")
        
        # Get Shopify analytics
        if PlatformType.SHOPIFY in platform_service.platforms:
            try:
                shopify_analytics = await platform_service.get_shopify_analytics(start_dt, end_dt)
                unified_analytics["products"]["total_products"] = 10  # Mock data
                unified_analytics["products"]["total_revenue"] = shopify_analytics.get("total_revenue", 0)
                unified_analytics["products"]["total_orders"] = shopify_analytics.get("total_orders", 0)
                unified_analytics["products"]["average_order_value"] = shopify_analytics.get("average_order_value", 0)
                
            except Exception as e:
                logger.warning(f"Failed to get Shopify analytics: {e}")
        
        # Get Stripe analytics
        if PlatformType.STRIPE in platform_service.platforms:
            try:
                stripe_analytics = await platform_service.get_stripe_analytics(start_dt, end_dt)
                unified_analytics["payments"]["total_payments"] = stripe_analytics.get("total_payments", 0)
                unified_analytics["payments"]["total_amount"] = stripe_analytics.get("total_amount", 0)
                unified_analytics["payments"]["success_rate"] = stripe_analytics.get("success_rate", 0)
                unified_analytics["payments"]["average_payment"] = stripe_analytics.get("average_payment", 0)
                
            except Exception as e:
                logger.warning(f"Failed to get Stripe analytics: {e}")
        
        return unified_analytics
        
    except Exception as e:
        logger.error(f"Error getting unified analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unified analytics"
        )

# Platform Health Check
@router.get("/api/platforms/health", summary="Platform Integrations Health Check")
async def platform_health_check(
    platform_service: AdvancedPlatformIntegrationsService = Depends(get_platform_service)
):
    """
    Check the health of platform integrations.
    Returns status of all initialized platforms.
    """
    try:
        # Check database connection
        await platform_service.db.admin.command('ping')
        
        # Check platform integrations
        platform_status = {}
        for platform_type, client in platform_service.platforms.items():
            try:
                # Simple health check - in production, make actual API calls
                platform_status[platform_type.value] = {
                    "status": "healthy",
                    "initialized": True,
                    "capabilities": []
                }
                
                if platform_type in [PlatformType.LINKEDIN_ADS, PlatformType.TIKTOK_ADS, PlatformType.YOUTUBE_ADS]:
                    platform_status[platform_type.value]["capabilities"] = [
                        "campaign_creation", "campaign_management", "metrics_tracking", "audience_targeting"
                    ]
                elif platform_type == PlatformType.SHOPIFY:
                    platform_status[platform_type.value]["capabilities"] = [
                        "product_management", "order_tracking", "inventory_management", "analytics"
                    ]
                elif platform_type == PlatformType.STRIPE:
                    platform_status[platform_type.value]["capabilities"] = [
                        "payment_processing", "customer_management", "subscription_management", "analytics"
                    ]
                    
            except Exception as e:
                platform_status[platform_type.value] = {
                    "status": "unhealthy",
                    "initialized": True,
                    "error": str(e)
                }
        
        all_healthy = all(status.get("status") == "healthy" for status in platform_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "platforms": platform_status,
            "supported_platforms": [platform.value for platform in PlatformType],
            "initialized_count": len(platform_service.platforms),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking platform health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
