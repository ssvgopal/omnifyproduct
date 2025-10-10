"""
MongoDB Schema Initialization for Omnify Cloud Connect
Creates collections, indexes, and validation rules for AgentKit integration
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MongoDBSchema:
    """MongoDB schema manager for Omnify Cloud Connect"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def initialize_schema(self):
        """Initialize all collections with indexes and validation"""
        logger.info("Initializing MongoDB schema...")
        
        await self._create_users_collection()
        await self._create_organizations_collection()
        await self._create_subscriptions_collection()
        await self._create_campaigns_collection()
        await self._create_clients_collection()
        await self._create_analytics_collection()
        await self._create_assets_collection()
        await self._create_audit_logs_collection()
        await self._create_agentkit_collections()
        
        logger.info("MongoDB schema initialization complete")
    
    async def _create_users_collection(self):
        """Create users collection with indexes"""
        collection = self.db.users
        
        # Create indexes
        await collection.create_index("email", unique=True)
        await collection.create_index("organization_id")
        await collection.create_index("agentkit_user_id")
        await collection.create_index([("email", 1), ("is_active", 1)])
        
        logger.info("Created users collection with indexes")
    
    async def _create_organizations_collection(self):
        """Create organizations collection with indexes"""
        collection = self.db.organizations
        
        # Create indexes
        await collection.create_index("slug", unique=True)
        await collection.create_index("owner_id")
        await collection.create_index("agentkit_tenant_id")
        await collection.create_index("gohighlevel_location_id")
        await collection.create_index("subscription_tier")
        
        logger.info("Created organizations collection with indexes")
    
    async def _create_subscriptions_collection(self):
        """Create subscriptions collection with indexes"""
        collection = self.db.subscriptions
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("stripe_subscription_id", unique=True, sparse=True)
        await collection.create_index("status")
        await collection.create_index([("organization_id", 1), ("status", 1)])
        await collection.create_index("current_period_end")  # For renewal checks
        
        logger.info("Created subscriptions collection with indexes")
    
    async def _create_campaigns_collection(self):
        """Create campaigns collection with indexes"""
        collection = self.db.campaigns
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("agentkit_workflow_id")
        await collection.create_index("gohighlevel_campaign_id")
        await collection.create_index("status")
        await collection.create_index([("organization_id", 1), ("status", 1)])
        await collection.create_index([("organization_id", 1), ("created_at", -1)])
        await collection.create_index("platforms.platform")
        await collection.create_index("created_by")
        
        logger.info("Created campaigns collection with indexes")
    
    async def _create_clients_collection(self):
        """Create clients collection with indexes"""
        collection = self.db.clients
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("email", unique=True)
        await collection.create_index("gohighlevel_contact_id")
        await collection.create_index([("organization_id", 1), ("status", 1)])
        await collection.create_index([("organization_id", 1), ("created_at", -1)])
        
        logger.info("Created clients collection with indexes")
    
    async def _create_analytics_collection(self):
        """Create analytics collection with indexes"""
        collection = self.db.analytics
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("campaign_id")
        await collection.create_index("date")
        await collection.create_index([("organization_id", 1), ("date", -1)])
        await collection.create_index([("campaign_id", 1), ("date", -1)])
        await collection.create_index([("organization_id", 1), ("campaign_id", 1), ("date", -1)])
        
        # TTL index for data retention (optional - keep 2 years of data)
        await collection.create_index("created_at", expireAfterSeconds=63072000)  # 2 years
        
        logger.info("Created analytics collection with indexes")
    
    async def _create_assets_collection(self):
        """Create assets collection with indexes"""
        collection = self.db.assets
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("campaign_id")
        await collection.create_index("asset_type")
        await collection.create_index([("organization_id", 1), ("asset_type", 1)])
        await collection.create_index([("organization_id", 1), ("created_at", -1)])
        await collection.create_index("storage_url")
        
        logger.info("Created assets collection with indexes")
    
    async def _create_audit_logs_collection(self):
        """Create audit_logs collection with indexes (SOC 2 compliance)"""
        collection = self.db.audit_logs
        
        # Create indexes
        await collection.create_index("organization_id")
        await collection.create_index("user_id")
        await collection.create_index("action")
        await collection.create_index("timestamp")
        await collection.create_index([("organization_id", 1), ("timestamp", -1)])
        await collection.create_index([("user_id", 1), ("timestamp", -1)])
        await collection.create_index([("organization_id", 1), ("action", 1), ("timestamp", -1)])
        
        # TTL index for data retention policy (7 years for SOC 2)
        await collection.create_index("retention_until", expireAfterSeconds=0)
        
        logger.info("Created audit_logs collection with indexes")
    
    async def _create_agentkit_collections(self):
        """Create AgentKit-specific collections"""
        
        # Agent configurations
        agents_collection = self.db.agentkit_agents
        await agents_collection.create_index("organization_id")
        await agents_collection.create_index("agentkit_agent_id", unique=True, sparse=True)
        await agents_collection.create_index("agent_type")
        await agents_collection.create_index([("organization_id", 1), ("agent_type", 1)])
        await agents_collection.create_index([("organization_id", 1), ("is_active", 1)])
        
        # Agent executions
        executions_collection = self.db.agentkit_executions
        await executions_collection.create_index("agent_id")
        await executions_collection.create_index("organization_id")
        await executions_collection.create_index("user_id")
        await executions_collection.create_index("status")
        await executions_collection.create_index([("organization_id", 1), ("started_at", -1)])
        await executions_collection.create_index([("agent_id", 1), ("started_at", -1)])
        # TTL index - keep execution logs for 90 days
        await executions_collection.create_index("started_at", expireAfterSeconds=7776000)  # 90 days
        
        # Workflow definitions
        workflows_collection = self.db.agentkit_workflows
        await workflows_collection.create_index("organization_id")
        await workflows_collection.create_index("agentkit_workflow_id", unique=True, sparse=True)
        await workflows_collection.create_index([("organization_id", 1), ("is_active", 1)])
        
        # Workflow executions
        workflow_executions_collection = self.db.agentkit_workflow_executions
        await workflow_executions_collection.create_index("workflow_id")
        await workflow_executions_collection.create_index("organization_id")
        await workflow_executions_collection.create_index("user_id")
        await workflow_executions_collection.create_index("status")
        await workflow_executions_collection.create_index([("organization_id", 1), ("started_at", -1)])
        await workflow_executions_collection.create_index([("workflow_id", 1), ("started_at", -1)])
        # TTL index - keep workflow execution logs for 90 days
        await workflow_executions_collection.create_index("started_at", expireAfterSeconds=7776000)
        
        # Compliance checks
        compliance_collection = self.db.agentkit_compliance
        await compliance_collection.create_index("organization_id")
        await compliance_collection.create_index("check_type")
        await compliance_collection.create_index("status")
        await compliance_collection.create_index([("organization_id", 1), ("checked_at", -1)])
        await compliance_collection.create_index("next_check_at")  # For scheduled checks
        
        logger.info("Created AgentKit collections with indexes")
    
    async def create_default_data(self, organization_id: str, user_id: str):
        """Create default agents and workflows for a new organization"""
        
        # Default agent configurations
        default_agents = [
            {
                "agent_id": f"{organization_id}_creative_intelligence",
                "agent_type": "creative_intelligence",
                "name": "Creative Intelligence Agent",
                "description": "AI-powered creative repurposing, AIDA analysis, and brand compliance",
                "organization_id": organization_id,
                "capabilities": [
                    "aida_analysis",
                    "brand_compliance_check",
                    "performance_prediction",
                    "creative_repurposing",
                    "multi_platform_optimization"
                ],
                "config": {
                    "max_concurrent_executions": 5,
                    "timeout_seconds": 300,
                    "retry_attempts": 3
                },
                "is_active": True
            },
            {
                "agent_id": f"{organization_id}_marketing_automation",
                "agent_type": "marketing_automation",
                "name": "Marketing Automation Agent",
                "description": "Multi-platform campaign management and automation",
                "organization_id": organization_id,
                "capabilities": [
                    "campaign_creation",
                    "multi_platform_deployment",
                    "lead_nurturing",
                    "email_sms_automation",
                    "audience_targeting"
                ],
                "config": {
                    "max_concurrent_executions": 10,
                    "timeout_seconds": 600,
                    "retry_attempts": 3
                },
                "is_active": True
            },
            {
                "agent_id": f"{organization_id}_client_management",
                "agent_type": "client_management",
                "name": "Client Management Agent",
                "description": "Client onboarding, billing, and success tracking",
                "organization_id": organization_id,
                "capabilities": [
                    "client_onboarding",
                    "subscription_management",
                    "billing_automation",
                    "success_tracking",
                    "reporting"
                ],
                "config": {
                    "max_concurrent_executions": 5,
                    "timeout_seconds": 300,
                    "retry_attempts": 3
                },
                "is_active": True
            },
            {
                "agent_id": f"{organization_id}_analytics",
                "agent_type": "analytics",
                "name": "Analytics Agent",
                "description": "Real-time tracking, predictive analytics, and ROI analysis",
                "organization_id": organization_id,
                "capabilities": [
                    "real_time_tracking",
                    "predictive_analytics",
                    "roi_analysis",
                    "cohort_analysis",
                    "attribution_modeling"
                ],
                "config": {
                    "max_concurrent_executions": 10,
                    "timeout_seconds": 300,
                    "retry_attempts": 2
                },
                "is_active": True
            }
        ]
        
        # Insert default agents
        await self.db.agentkit_agents.insert_many(default_agents)
        logger.info(f"Created {len(default_agents)} default agents for organization {organization_id}")
        
        return default_agents


async def initialize_database(mongo_url: str, db_name: str):
    """Initialize MongoDB database with schema"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    schema_manager = MongoDBSchema(db)
    await schema_manager.initialize_schema()
    
    return db


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        mongo_url = os.getenv("MONGO_URL")
        db_name = os.getenv("DB_NAME", "omnify_cloud")
        
        db = await initialize_database(mongo_url, db_name)
        print("Database initialized successfully")
    
    asyncio.run(main())
