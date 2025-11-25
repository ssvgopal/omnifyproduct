"""
Comprehensive Database Schema Management for OmnifyProduct
Handles schema initialization, migrations, and data seeding
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import json

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration system"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.migration_collection = db.migrations

    async def initialize_schema(self):
        """Initialize complete database schema"""
        logger.info("Initializing database schema...")

        # Create collections with proper indexes
        await self._create_collections()
        await self._create_indexes()
        await self._run_migrations()

        logger.info("Database schema initialization completed")

    async def _create_collections(self):
        """Create all required collections"""
        collections = [
            'users',
            'organizations',
            'subscriptions',
            'agentkit_agents',
            'agentkit_executions',
            'agentkit_workflows',
            'agentkit_workflow_executions',
            'audit_logs',
            'compliance_checks',
            'scheduled_workflows',
            'analytics_data',
            'migrations'
        ]

        for collection_name in collections:
            # MongoDB creates collections automatically when first document is inserted
            # But we can ensure they exist by trying to create them
            try:
                await self.db[collection_name].insert_one({"_init": True})
                await self.db[collection_name].delete_one({"_init": True})
            except Exception as e:
                logger.warning(f"Could not initialize collection {collection_name}: {str(e)}")

    async def _create_indexes(self):
        """Create database indexes for performance"""
        # Users collection indexes
        await self.db.users.create_index([("email", 1)], unique=True)
        await self.db.users.create_index([("organization_id", 1)])
        await self.db.users.create_index([("created_at", 1)])

        # Organizations collection indexes
        await self.db.organizations.create_index([("organization_id", 1)], unique=True)
        await self.db.organizations.create_index([("slug", 1)], unique=True)
        await self.db.organizations.create_index([("owner_id", 1)])

        # Agents collection indexes
        await self.db.agentkit_agents.create_index([("agent_id", 1)], unique=True)
        await self.db.agentkit_agents.create_index([("organization_id", 1)])
        await self.db.agentkit_agents.create_index([("agent_type", 1)])
        await self.db.agentkit_agents.create_index([("is_active", 1)])

        # Executions collection indexes
        await self.db.agentkit_executions.create_index([("execution_id", 1)], unique=True)
        await self.db.agentkit_executions.create_index([("agent_id", 1)])
        await self.db.agentkit_executions.create_index([("organization_id", 1)])
        await self.db.agentkit_executions.create_index([("user_id", 1)])
        await self.db.agentkit_executions.create_index([("started_at", 1)])
        await self.db.agentkit_executions.create_index([("status", 1)])

        # Workflows collection indexes
        await self.db.agentkit_workflows.create_index([("workflow_id", 1)], unique=True)
        await self.db.agentkit_workflows.create_index([("organization_id", 1)])

        # Workflow executions collection indexes
        await self.db.agentkit_workflow_executions.create_index([("execution_id", 1)], unique=True)
        await self.db.agentkit_workflow_executions.create_index([("workflow_id", 1)])
        await self.db.agentkit_workflow_executions.create_index([("organization_id", 1)])
        await self.db.agentkit_workflow_executions.create_index([("started_at", 1)])

        # Audit logs collection indexes
        await self.db.audit_logs.create_index([("organization_id", 1)])
        await self.db.audit_logs.create_index([("user_id", 1)])
        await self.db.audit_logs.create_index([("timestamp", 1)])
        await self.db.audit_logs.create_index([("retention_until", 1)])

        # Compliance collection indexes
        await self.db.agentkit_compliance.create_index([("organization_id", 1)])
        await self.db.agentkit_compliance.create_index([("check_type", 1)])
        await self.db.agentkit_compliance.create_index([("checked_at", 1)])

        # Scheduled workflows collection indexes
        await self.db.scheduled_workflows.create_index([("schedule_time", 1)])
        await self.db.scheduled_workflows.create_index([("status", 1)])

        logger.info("Database indexes created successfully")

    async def _run_migrations(self):
        """Run database migrations"""
        migrations = [
            {
                "version": "1.0.0",
                "description": "Initial schema setup",
                "up": self._migration_1_0_0,
                "down": self._migration_1_0_0_down
            },
            {
                "version": "1.1.0",
                "description": "Add workflow orchestration fields",
                "up": self._migration_1_1_0,
                "down": self._migration_1_1_0_down
            }
        ]

        for migration in migrations:
            await self._apply_migration(migration)

    async def _apply_migration(self, migration: Dict[str, Any]):
        """Apply a single migration if not already applied"""
        version = migration["version"]

        # Check if migration already applied
        existing = await self.migration_collection.find_one({"version": version})
        if existing:
            logger.info(f"Migration {version} already applied")
            return

        logger.info(f"Applying migration {version}: {migration['description']}")

        try:
            # Apply migration
            await migration["up"]()

            # Record migration
            await self.migration_collection.insert_one({
                "version": version,
                "description": migration["description"],
                "applied_at": datetime.utcnow(),
                "status": "completed"
            })

            logger.info(f"Migration {version} applied successfully")

        except Exception as e:
            logger.error(f"Migration {version} failed: {str(e)}")

            # Record failed migration
            await self.migration_collection.insert_one({
                "version": version,
                "description": migration["description"],
                "applied_at": datetime.utcnow(),
                "status": "failed",
                "error": str(e)
            })

    async def _migration_1_0_0(self):
        """Initial schema migration"""
        # Add default compliance settings
        await self.db.organizations.update_many(
            {"compliance_settings": {"$exists": False}},
            {"$set": {
                "compliance_settings": {
                    "soc2_enabled": True,
                    "data_retention_days": 2555,  # 7 years
                    "audit_logging": True,
                    "encryption_required": True
                }
            }}
        )

    async def _migration_1_0_0_down(self):
        """Rollback initial schema migration"""
        await self.db.organizations.update_many(
            {},
            {"$unset": {"compliance_settings": ""}}
        )

    async def _migration_1_1_0(self):
        """Add workflow orchestration fields"""
        # Add execution metadata to workflow executions
        await self.db.agentkit_workflow_executions.update_many(
            {"execution_metadata": {"$exists": False}},
            {"$set": {
                "execution_metadata": {
                    "parallel_execution": False,
                    "retry_failed_steps": True,
                    "max_execution_time": 300
                }
            }}
        )

    async def _migration_1_1_0_down(self):
        """Rollback workflow orchestration migration"""
        await self.db.agentkit_workflow_executions.update_many(
            {},
            {"$unset": {"execution_metadata": ""}}
        )


class DatabaseSeeder:
    """Database seeding for development and testing"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def seed_development_data(self, organization_id: str, user_id: str):
        """Seed development data for testing"""
        logger.info(f"Seeding development data for organization {organization_id}")

        # Seed default agents
        await self._seed_default_agents(organization_id, user_id)

        # Seed sample workflows
        await self._seed_sample_workflows(organization_id, user_id)

        # Seed sample execution data
        await self._seed_sample_executions(organization_id, user_id)

        logger.info("Development data seeded successfully")

    async def _seed_default_agents(self, organization_id: str, user_id: str):
        """Seed default agents for organization"""
        default_agents = [
            {
                "agent_id": f"{organization_id}_creative_intelligence",
                "organization_id": organization_id,
                "user_id": user_id,
                "name": "Creative Intelligence Agent",
                "agent_type": "creative_intelligence",
                "description": "Analyzes creative assets and provides AIDA optimization recommendations",
                "config": {
                    "analysis_types": ["aida", "brand_compliance", "performance_prediction"],
                    "platforms": ["google_ads", "meta_ads", "linkedin_ads"],
                    "auto_optimize": True
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "agent_id": f"{organization_id}_marketing_automation",
                "organization_id": organization_id,
                "user_id": user_id,
                "name": "Marketing Automation Agent",
                "agent_type": "marketing_automation",
                "description": "Automates campaign creation and deployment across platforms",
                "config": {
                    "platforms": ["google_ads", "meta_ads", "linkedin_ads"],
                    "auto_bidding": True,
                    "budget_management": True
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "agent_id": f"{organization_id}_client_management",
                "organization_id": organization_id,
                "user_id": user_id,
                "name": "Client Management Agent",
                "agent_type": "client_management",
                "description": "Manages client relationships and success metrics",
                "config": {
                    "success_tracking": True,
                    "billing_integration": True,
                    "reporting_automation": True
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "agent_id": f"{organization_id}_analytics",
                "organization_id": organization_id,
                "user_id": user_id,
                "name": "Analytics Agent",
                "agent_type": "analytics",
                "description": "Provides real-time analytics and performance insights",
                "config": {
                    "real_time_tracking": True,
                    "predictive_analytics": True,
                    "custom_reporting": True
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]

        for agent in default_agents:
            await self.db.agentkit_agents.insert_one(agent)

    async def _seed_sample_workflows(self, organization_id: str, user_id: str):
        """Seed sample workflows"""
        sample_workflows = [
            {
                "workflow_id": f"{organization_id}_campaign_launch",
                "organization_id": organization_id,
                "user_id": user_id,
                "name": "Campaign Launch Workflow",
                "description": "Complete campaign creation and launch process",
                "steps": [
                    {
                        "step_id": "creative_analysis",
                        "agent_type": "creative_intelligence",
                        "input_mapping": {
                            "asset_url": "campaign_creative_url",
                            "analysis_type": "campaign_launch"
                        },
                        "output_mapping": {
                            "aida_scores": "campaign_aida_scores",
                            "recommendations": "creative_recommendations"
                        }
                    },
                    {
                        "step_id": "campaign_creation",
                        "agent_type": "marketing_automation",
                        "depends_on": ["creative_analysis"],
                        "input_mapping": {
                            "campaign_config": "campaign_config",
                            "aida_scores": "campaign_aida_scores"
                        },
                        "output_mapping": {
                            "platform_campaign_ids": "deployment_results"
                        }
                    },
                    {
                        "step_id": "performance_setup",
                        "agent_type": "analytics",
                        "depends_on": ["campaign_creation"],
                        "input_mapping": {
                            "campaign_ids": "deployment_results"
                        },
                        "output_mapping": {
                            "tracking_setup": "analytics_setup"
                        }
                    }
                ],
                "config": {
                    "execution_mode": "sequential",
                    "notification_settings": {
                        "email_on_completion": True,
                        "email_on_failure": True
                    }
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]

        for workflow in sample_workflows:
            await self.db.agentkit_workflows.insert_one(workflow)

    async def _seed_sample_executions(self, organization_id: str, user_id: str):
        """Seed sample execution data"""
        # Sample agent executions
        for i in range(5):
            execution = {
                "execution_id": f"sample_exec_{i}",
                "agent_id": f"{organization_id}_creative_intelligence",
                "organization_id": organization_id,
                "user_id": user_id,
                "status": "completed",
                "input_data": {
                    "asset_url": f"https://example.com/creative_{i}.jpg",
                    "analysis_type": "aida"
                },
                "output_data": {
                    "aida_scores": {
                        "attention": 0.75 + (i * 0.05),
                        "interest": 0.70 + (i * 0.03),
                        "desire": 0.65 + (i * 0.04),
                        "action": 0.70 + (i * 0.02)
                    },
                    "recommendations": [f"Sample recommendation {i}"]
                },
                "started_at": datetime.utcnow() - timedelta(hours=i),
                "completed_at": datetime.utcnow() - timedelta(hours=i-1),
                "duration_seconds": 2.5 + (i * 0.5)
            }
            await self.db.agentkit_executions.insert_one(execution)

    async def create_default_data(self, organization_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Create default agents and workflows for new organization"""
        await self._seed_default_agents(organization_id, user_id)

        # Return created agents
        agents = await self.db.agentkit_agents.find(
            {"organization_id": organization_id}
        ).to_list(None)

        return agents


class DatabaseHealthChecker:
    """Database health and performance monitoring"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def check_database_health(self) -> Dict[str, Any]:
        """Check overall database health"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            # Check database connectivity
            ping_result = await self.db.command("ping")
            health["checks"]["connectivity"] = "healthy"

            # Check collection counts
            collections = await self.db.list_collection_names()
            health["checks"]["collections"] = len(collections)

            # Check sample data presence
            org_count = await self.db.organizations.count_documents({})
            user_count = await self.db.users.count_documents({})
            agent_count = await self.db.agentkit_agents.count_documents({})

            health["checks"]["data"] = {
                "organizations": org_count,
                "users": user_count,
                "agents": agent_count
            }

            # Check recent activity
            recent_executions = await self.db.agentkit_executions.count_documents({
                "started_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            health["checks"]["recent_activity"] = recent_executions

        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
            logger.error(f"Database health check failed: {str(e)}")

        return health

    async def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "collections": {},
            "performance": {}
        }

        try:
            # Collection statistics
            collections = await self.db.list_collection_names()

            for collection_name in collections:
                collection = self.db[collection_name]
                count = await collection.count_documents({})
                stats["collections"][collection_name] = {
                    "document_count": count,
                    "size_bytes": 0  # Would need aggregation for actual size
                }

            # Performance metrics (simplified)
            recent_ops = await self.db.agentkit_executions.count_documents({
                "started_at": {"$gte": datetime.utcnow() - timedelta(hours=1)}
            })
            stats["performance"]["recent_executions_per_hour"] = recent_ops

        except Exception as e:
            logger.error(f"Database statistics check failed: {str(e)}")
            stats["error"] = str(e)

        return stats


class MongoDBSchema:
    """Main schema management class"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.migration = DatabaseMigration(db)
        self.seeder = DatabaseSeeder(db)
        self.health_checker = DatabaseHealthChecker(db)

    async def initialize_schema(self):
        """Initialize complete database schema"""
        await self.migration.initialize_schema()

    async def create_default_data(self, organization_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Create default data for new organization"""
        return await self.seeder.create_default_data(organization_id, user_id)

    async def check_health(self) -> Dict[str, Any]:
        """Check database health"""
        return await self.health_checker.check_database_health()

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return await self.health_checker.get_database_statistics()

    async def cleanup_old_data(self, retention_days: int = 2555):
        """Clean up old data based on retention policies"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        try:
            # Clean up old audit logs
            deleted_audit_logs = await self.db.audit_logs.delete_many({
                "retention_until": {"$lt": cutoff_date}
            })

            # Clean up old executions (keep for 90 days for analytics)
            execution_cutoff = datetime.utcnow() - timedelta(days=90)
            deleted_executions = await self.db.agentkit_executions.delete_many({
                "started_at": {"$lt": execution_cutoff}
            })

            logger.info(f"Cleaned up {deleted_audit_logs.deleted_count} audit logs and {deleted_executions.deleted_count} old executions")

            return {
                "deleted_audit_logs": deleted_audit_logs.deleted_count,
                "deleted_executions": deleted_executions.deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        except Exception as e:
            logger.error(f"Data cleanup failed: {str(e)}")
            raise
    
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
        logger.info("Database initialized successfully")
    
    asyncio.run(main())
