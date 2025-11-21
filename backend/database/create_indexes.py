"""
Database Index Creation Script
Creates indexes for optimal query performance
"""

import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')


async def create_indexes():
    """Create all database indexes"""
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'omnify_cloud')
    
    if not mongo_url:
        logger.error("MONGO_URL environment variable not set")
        sys.exit(1)
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        logger.info(f"Connecting to MongoDB: {db_name}")
        
        # Users collection
        logger.info("Creating indexes for 'users' collection...")
        await db.users.create_index("email", unique=True, name="email_unique")
        await db.users.create_index("organization_id", name="organization_id_idx")
        await db.users.create_index([("created_at", -1)], name="created_at_desc_idx")
        await db.users.create_index("verification_token", name="verification_token_idx", sparse=True)
        await db.users.create_index("email_verified", name="email_verified_idx")
        
        # Organizations collection
        logger.info("Creating indexes for 'organizations' collection...")
        await db.organizations.create_index("slug", unique=True, name="slug_unique")
        await db.organizations.create_index("subscription_tier", name="subscription_tier_idx")
        await db.organizations.create_index([("created_at", -1)], name="created_at_desc_idx")
        await db.organizations.create_index("owner_email", name="owner_email_idx")
        
        # Campaigns collection
        logger.info("Creating indexes for 'campaigns' collection...")
        await db.campaigns.create_index("organization_id", name="organization_id_idx")
        await db.campaigns.create_index("user_id", name="user_id_idx")
        await db.campaigns.create_index([("created_at", -1)], name="created_at_desc_idx")
        await db.campaigns.create_index("status", name="status_idx")
        await db.campaigns.create_index([("organization_id", 1), ("status", 1)], name="org_status_compound_idx")
        
        # Analytics collection
        logger.info("Creating indexes for 'analytics' collection...")
        await db.analytics.create_index("campaign_id", name="campaign_id_idx")
        await db.analytics.create_index([("timestamp", -1)], name="timestamp_desc_idx")
        await db.analytics.create_index("platform", name="platform_idx")
        await db.analytics.create_index([("campaign_id", 1), ("timestamp", -1)], name="campaign_timestamp_compound_idx")
        
        # Agents collection
        logger.info("Creating indexes for 'agents' collection...")
        await db.agents.create_index("organization_id", name="organization_id_idx")
        await db.agents.create_index("type", name="type_idx")
        await db.agents.create_index("status", name="status_idx")
        await db.agents.create_index([("organization_id", 1), ("type", 1)], name="org_type_compound_idx")
        
        # Audit logs
        logger.info("Creating indexes for 'audit_logs' collection...")
        await db.audit_logs.create_index("user_id", name="user_id_idx")
        await db.audit_logs.create_index("organization_id", name="organization_id_idx")
        await db.audit_logs.create_index([("timestamp", -1)], name="timestamp_desc_idx")
        await db.audit_logs.create_index("action", name="action_idx")
        await db.audit_logs.create_index([("organization_id", 1), ("timestamp", -1)], name="org_timestamp_compound_idx")
        
        # Client onboarding collections (new)
        logger.info("Creating indexes for 'client_profiles' collection...")
        await db.client_profiles.create_index("organization_id", name="organization_id_idx")
        await db.client_profiles.create_index("client_id", unique=True, name="client_id_unique")
        await db.client_profiles.create_index("onboarding_status", name="onboarding_status_idx")
        await db.client_profiles.create_index([("organization_id", 1), ("onboarding_status", 1)], name="org_status_compound_idx")
        
        logger.info("Creating indexes for 'uploaded_files' collection...")
        await db.uploaded_files.create_index("client_id", name="client_id_idx")
        await db.uploaded_files.create_index("file_category", name="file_category_idx")
        await db.uploaded_files.create_index([("uploaded_at", -1)], name="uploaded_at_desc_idx")
        await db.uploaded_files.create_index([("client_id", 1), ("file_category", 1)], name="client_category_compound_idx")
        
        logger.info("Creating indexes for 'platform_credentials' collection...")
        await db.platform_credentials.create_index(
            [("organization_id", 1), ("platform", 1)],
            unique=True,
            name="org_platform_unique"
        )
        await db.platform_credentials.create_index("client_id", name="client_id_idx")
        await db.platform_credentials.create_index("platform", name="platform_idx")
        await db.platform_credentials.create_index("is_active", name="is_active_idx")
        
        logger.info("Creating indexes for 'campaign_ideas' collection...")
        await db.campaign_ideas.create_index("client_id", name="client_id_idx")
        await db.campaign_ideas.create_index([("created_at", -1)], name="created_at_desc_idx")
        await db.campaign_ideas.create_index([("client_id", 1), ("created_at", -1)], name="client_created_compound_idx")
        
        # Legal document acceptances
        logger.info("Creating indexes for 'user_legal_acceptances' collection...")
        await db.user_legal_acceptances.create_index("user_id", name="user_id_idx")
        await db.user_legal_acceptances.create_index("document_type", name="document_type_idx")
        await db.user_legal_acceptances.create_index([("user_id", 1), ("document_type", 1), ("version", 1)], name="user_doc_version_compound_idx")
        await db.user_legal_acceptances.create_index([("accepted_at", -1)], name="accepted_at_desc_idx")
        
        logger.info("✅ All indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())

