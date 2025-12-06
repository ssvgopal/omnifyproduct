from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
# Phase 1 deprecated - MongoDB archived (MVP uses Supabase)
# from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import core components
from core.gateway import gateway
from core.auth import auth_service, AuthService
from core.rate_limiter import rate_limiter

# Import API routes
from api.api_key_routes import router as api_key_router

# Import platform adapters (MVP only)
# Phase 1 deprecated adapters (archived)
# from platform_adapters.agentkit_adapter import agentkit_adapter
# from platform_adapters.gohighlevel_adapter import gohighlevel_adapter
from platform_adapters.custom_adapter import custom_adapter

# Import brain logic modules
from brain_logic.creative_intelligence import creative_intelligence
from brain_logic.market_intelligence import market_intelligence
from brain_logic.client_intelligence import client_intelligence
from brain_logic.customization_engine import customization_engine

# Import shared components
from shared_components.analytics_engine import analytics_engine
from shared_components.integration_hub import integration_hub

# Import models
from models.platform_models import *
from models.brain_models import *
from models.analytics_models import *

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Omnify Cloud Connect", version="1.0.0")

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# ========== CORE API ENDPOINTS ==========

@api_router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Omnify Cloud Connect - Unified Multi-Platform Solution",
        "version": "1.0.0",
        "platforms": ["Custom"],  # MVP only - AgentKit/GoHighLevel archived
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "gateway": "operational",
            "platforms": ["custom"],  # MVP only - AgentKit/GoHighLevel archived
            "brain_logic": "operational",
            "analytics": "operational"
        }
    }

# ========== PLATFORM ADAPTER ENDPOINTS ==========

# Phase 1 deprecated endpoints (AgentKit and GoHighLevel archived)
# All AgentKit and GoHighLevel endpoints removed - archived in Phase 1
# MVP focuses on Meta/Google/TikTok/Shopify integrations only

# @api_router.post("/agentkit/agents")
# async def create_agentkit_agent(agent: AgentCreate):
#     """Create an AgentKit agent - Phase 1 deprecated"""
#     raise HTTPException(status_code=501, detail="AgentKit is Phase 1 deprecated")
# ... (all AgentKit endpoints commented out)

# @api_router.post("/gohighlevel/clients")
# async def create_ghl_client(client_data: ClientCreate):
#     """Create a GoHighLevel client - Phase 1 deprecated"""
#     raise HTTPException(status_code=501, detail="GoHighLevel is Phase 1 deprecated")
# ... (all GoHighLevel endpoints commented out)

# Custom Platform Endpoints
@api_router.post("/custom/microservices")
async def deploy_custom_microservice(service: MicroserviceCreate):
    """Deploy a custom microservice"""
    result = await custom_adapter.deploy_microservice(service.dict())
    return result

@api_router.get("/custom/microservices")
async def list_custom_microservices():
    """List all custom microservices"""
    services = await custom_adapter.list_services()
    return {"services": services}

@api_router.post("/custom/microservices/{service_id}/scale")
async def scale_custom_service(service_id: str, scale: ServiceScale):
    """Scale a custom microservice"""
    result = await custom_adapter.scale_service(service_id, scale.replicas)
    return result

@api_router.get("/custom/microservices/{service_id}/health")
async def get_custom_service_health(service_id: str):
    """Get custom microservice health"""
    health = await custom_adapter.get_service_health(service_id)
    return health

@api_router.post("/custom/workflows")
async def execute_custom_workflow(workflow: WorkflowCreate):
    """Execute a custom workflow"""
    result = await custom_adapter.execute_custom_workflow(workflow.dict())
    return result

# ========== BRAIN LOGIC ENDPOINTS ==========

# Creative Intelligence Endpoints
@api_router.post("/brain/creative/analyze")
async def analyze_content(analysis: ContentAnalysis):
    """Analyze content using AI"""
    result = await creative_intelligence.analyze_content(analysis.content, analysis.context)
    return result

@api_router.post("/brain/creative/repurpose")
async def repurpose_content(repurposing: ContentRepurposing):
    """Repurpose content to different format"""
    result = await creative_intelligence.repurpose_content(
        repurposing.content, 
        repurposing.target_format, 
        repurposing.brand_id
    )
    return result

@api_router.post("/brain/creative/brand-compliance")
async def check_brand_compliance(compliance: BrandCompliance):
    """Check content brand compliance"""
    result = await creative_intelligence.check_brand_compliance(
        compliance.content, 
        compliance.brand_id
    )
    return result

@api_router.post("/brain/creative/optimize")
async def optimize_content_performance(optimization: PerformanceOptimization):
    """Optimize content for performance"""
    result = await creative_intelligence.optimize_performance(
        optimization.content,
        optimization.platform,
        optimization.objective
    )
    return result

@api_router.post("/brain/creative/brands")
async def register_brand(brand: BrandProfileCreate):
    """Register a brand profile"""
    result = await creative_intelligence.register_brand_profile(brand.dict())
    return result

# Market Intelligence Endpoints
@api_router.post("/brain/market/analyze-vertical")
async def analyze_market_vertical(analysis: VerticalAnalysis):
    """Analyze specific market vertical"""
    result = await market_intelligence.analyze_vertical(analysis.vertical, analysis.data)
    return result

@api_router.post("/brain/market/predict-trends")
async def predict_market_trends(prediction: TrendPrediction):
    """Predict market trends"""
    result = await market_intelligence.predict_trends(prediction.vertical, prediction.timeframe)
    return result

@api_router.post("/brain/market/analyze-competitor")
async def analyze_market_competitor(analysis: CompetitorAnalysis):
    """Analyze competitor"""
    result = await market_intelligence.analyze_competitor(
        analysis.competitor_name,
        analysis.vertical
    )
    return result

@api_router.post("/brain/market/identify-opportunities")
async def identify_market_opportunities(identification: OpportunityIdentification):
    """Identify growth opportunities"""
    result = await market_intelligence.identify_opportunities(
        identification.vertical,
        identification.client_profile
    )
    return result

# Client Intelligence Endpoints
@api_router.post("/brain/client/analyze-behavior")
async def analyze_client_behavior(analysis: BehaviorAnalysis):
    """Analyze client behavior"""
    result = await client_intelligence.analyze_behavior(
        analysis.client_id,
        analysis.behavior_data
    )
    return result

@api_router.post("/brain/client/predict-success")
async def predict_client_success(prediction: SuccessPrediction):
    """Predict client success"""
    result = await client_intelligence.predict_success(prediction.client_id)
    return result

@api_router.post("/brain/client/recommendations")
async def generate_client_recommendations(client_id: str):
    """Generate client recommendations"""
    result = await client_intelligence.generate_recommendations(client_id)
    return result

@api_router.post("/brain/client/churn-risk")
async def analyze_churn_risk(analysis: ChurnRiskAnalysis):
    """Analyze client churn risk"""
    result = await client_intelligence.predict_churn_risk(analysis.client_id)
    return result

@api_router.post("/brain/client/satisfaction")
async def track_client_satisfaction(tracking: SatisfactionTracking):
    """Track client satisfaction"""
    result = await client_intelligence.track_satisfaction(
        tracking.client_id,
        tracking.feedback_data
    )
    return result

@api_router.post("/brain/client/profiles")
async def create_client_profile(profile: ClientProfileCreate):
    """Create client intelligence profile"""
    result = await client_intelligence.create_client_profile(profile.dict())
    return result

# Customization Engine Endpoints
@api_router.post("/brain/customize/configuration")
async def create_custom_configuration(config: CustomConfiguration):
    """Create custom configuration"""
    result = await customization_engine.create_configuration(config.dict())
    return result

@api_router.post("/brain/customize/apply-template")
async def apply_vertical_template(template: VerticalTemplate):
    """Apply vertical-specific template"""
    result = await customization_engine.apply_vertical_template(
        template.vertical,
        template.client_id
    )
    return result

@api_router.post("/brain/customize/branding")
async def customize_branding(branding: BrandCustomization):
    """Customize client branding"""
    result = await customization_engine.customize_branding(branding.dict())
    return result

@api_router.post("/brain/customize/workflow")
async def create_custom_workflow(workflow: CustomWorkflow):
    """Create custom workflow"""
    result = await customization_engine.create_custom_workflow(workflow.dict())
    return result

@api_router.post("/brain/customize/integration")
async def configure_custom_integration(integration: IntegrationConfiguration):
    """Configure custom integration"""
    result = await customization_engine.configure_integrations(integration.dict())
    return result

@api_router.get("/brain/customize/options")
async def get_customization_options(vertical: str, platform: str):
    """Get customization options"""
    result = await customization_engine.get_customization_options(vertical, platform)
    return result

# ========== SHARED COMPONENTS ENDPOINTS ==========

# Analytics Endpoints
@api_router.post("/analytics/collect")
async def collect_analytics_metrics(collection: MetricsCollection):
    """Collect platform metrics"""
    result = await analytics_engine.collect_metrics(collection.platform, collection.metrics)
    return result

@api_router.get("/analytics/cross-platform")
async def get_cross_platform_analytics(timeframe: str = '30_days'):
    """Get cross-platform analytics"""
    result = await analytics_engine.get_cross_platform_analytics(timeframe)
    return result

@api_router.post("/analytics/dashboards")
async def create_analytics_dashboard(dashboard: DashboardCreate):
    """Create analytics dashboard"""
    result = await analytics_engine.create_dashboard(dashboard.dict())
    return result

@api_router.post("/analytics/reports")
async def generate_analytics_report(report: ReportGeneration):
    """Generate analytics report"""
    result = await analytics_engine.generate_report(report.dict())
    return result

@api_router.post("/analytics/track-performance")
async def track_entity_performance(tracking: PerformanceTracking):
    """Track entity performance"""
    result = await analytics_engine.track_performance(
        tracking.entity_type,
        tracking.entity_id,
        tracking.metrics
    )
    return result

# Integration Hub Endpoints
@api_router.post("/integrations/register")
async def register_integration(integration: IntegrationRegistration):
    """Register a new integration"""
    result = await integration_hub.register_integration(integration.dict())
    return result

@api_router.post("/integrations/{integration_id}/credentials")
async def configure_integration_credentials(integration_id: str, credentials: IntegrationCredentials):
    """Configure integration credentials"""
    result = await integration_hub.configure_credentials(integration_id, credentials.credentials)
    return result

@api_router.post("/integrations/{integration_id}/execute")
async def execute_integration_action(integration_id: str, execution: IntegrationExecution):
    """Execute integration action"""
    result = await integration_hub.execute_integration(
        integration_id,
        execution.action,
        execution.data
    )
    return result

@api_router.post("/integrations/{integration_id}/sync")
async def sync_integration_data(integration_id: str, sync: DataSync):
    """Sync integration data"""
    result = await integration_hub.sync_data(integration_id, sync.sync_config)
    return result

@api_router.get("/integrations/available")
async def list_available_integrations(category: str = None):
    """List available integrations"""
    result = await integration_hub.list_available_integrations(category)
    return result

@api_router.get("/integrations/{integration_id}/status")
async def get_integration_status(integration_id: str):
    """Get integration status"""
    result = await integration_hub.get_integration_status(integration_id)
    return result

@api_router.get("/integrations")
async def list_registered_integrations():
    """List all registered integrations"""
    integrations = await integration_hub.list_registered_integrations()
    return {"integrations": integrations}

# ========== UNIFIED GATEWAY ENDPOINTS ==========

@api_router.post("/gateway/route")
async def route_unified_request(request: RouteRequest):
    """Route request through unified gateway"""
    result = await gateway.route_request(request.platform, request.operation, request.data)
    return result

@api_router.post("/gateway/aggregate")
async def aggregate_platform_responses(aggregate: AggregateResponses):
    """Aggregate responses from multiple platforms"""
    result = await gateway.aggregate_response(aggregate.responses)
    return result

# Include the routers in the main app
app.include_router(api_router)
app.include_router(api_key_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Omnify Cloud Connect - Starting up...")
    logger.info("Unified API Gateway initialized")
    logger.info("Platform adapters: AgentKit, GoHighLevel, Custom - Ready")
    logger.info("Brain logic modules: Creative, Market, Client Intelligence - Ready")
    logger.info("Shared components: Analytics, Integration Hub - Ready")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Omnify Cloud Connect - Shutting down...")
