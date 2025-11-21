"""
Configuration Validator
Validates environment variables on application startup
"""

import os
import sys
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates required environment variables"""
    
    REQUIRED_VARS = {
        "critical": [
            "MONGO_URL",
            "DB_NAME",
            "JWT_SECRET_KEY",
            "OPENAI_API_KEY",
        ],
        "important": [
            "CORS_ORIGINS",
            "SENTRY_DSN",
            "SENDGRID_API_KEY",
        ],
        "optional": [
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CLIENT_ID",
            "GOOGLE_ADS_CLIENT_SECRET",
            "META_APP_ID",
            "META_APP_SECRET",
            "TRIPLEWHALE_API_KEY",
            "HUBSPOT_API_KEY",
            "KLAVIYO_API_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY",
            "LINKEDIN_CLIENT_ID",
            "LINKEDIN_CLIENT_SECRET",
            "TIKTOK_APP_ID",
            "TIKTOK_APP_SECRET",
            "SHOPIFY_API_KEY",
            "SHOPIFY_ACCESS_TOKEN",
            "GOHIGHLEVEL_API_KEY",
            "YOUTUBE_API_KEY",
        ]
    }
    
    @classmethod
    def validate(cls) -> Dict[str, List[str]]:
        """
        Validate environment variables
        
        Returns:
            Dictionary with missing variables categorized by priority
        """
        missing = {
            "critical": [],
            "important": [],
            "optional": []
        }
        
        for level, vars_list in cls.REQUIRED_VARS.items():
            for var in vars_list:
                value = os.getenv(var)
                if not value or value.strip() == "":
                    missing[level].append(var)
        
        return missing
    
    @classmethod
    def validate_and_exit(cls, exit_on_critical: bool = True):
        """
        Validate configuration and exit if critical variables are missing
        
        Args:
            exit_on_critical: If True, exit with code 1 if critical vars are missing
        """
        missing = cls.validate()
        
        if missing["critical"]:
            logger.error("❌ CRITICAL: Missing required environment variables:")
            for var in missing["critical"]:
                logger.error(f"   - {var}")
            
            if exit_on_critical:
                logger.error("Application cannot start without critical variables.")
                sys.exit(1)
        
        if missing["important"]:
            logger.warning("⚠️  WARNING: Missing important environment variables:")
            for var in missing["important"]:
                logger.warning(f"   - {var}")
            logger.warning("Some features may not work correctly.")
        
        if missing["optional"]:
            logger.info("ℹ️  INFO: Missing optional environment variables (integrations may not work):")
            for var in missing["optional"]:
                logger.info(f"   - {var}")
        
        if not missing["critical"]:
            logger.info("✅ Configuration validation passed")
        
        return missing
    
    @classmethod
    def get_missing_critical(cls) -> List[str]:
        """Get list of missing critical variables"""
        missing = cls.validate()
        return missing["critical"]
    
    @classmethod
    def is_valid(cls) -> bool:
        """Check if all critical variables are present"""
        missing = cls.validate()
        return len(missing["critical"]) == 0

