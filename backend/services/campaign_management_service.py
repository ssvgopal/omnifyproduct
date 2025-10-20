"""
Campaign Management Interface
Production-grade campaign creation, management, and optimization system
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
import io
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
from PIL import Image
import mimetypes
import os

logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    """Campaign status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignType(str, Enum):
    """Campaign type options"""
    SEARCH = "search"
    DISPLAY = "display"
    SOCIAL = "social"
    VIDEO = "video"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class CreativeType(str, Enum):
    """Creative type options"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    CAROUSEL = "carousel"
    COLLECTION = "collection"
    STORY = "story"

class AssetType(str, Enum):
    """Asset type options"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ICON = "icon"
    LOGO = "logo"

@dataclass
class CampaignTargeting:
    """Campaign targeting configuration"""
    demographics: Dict[str, Any] = None
    interests: List[str] = None
    behaviors: List[str] = None
    locations: List[str] = None
    devices: List[str] = None
    custom_audiences: List[str] = None
    lookalike_audiences: List[str] = None

@dataclass
class CampaignBudget:
    """Campaign budget configuration"""
    daily_budget: float = 0.0
    lifetime_budget: float = 0.0
    bid_strategy: str = "manual"
    bid_amount: float = 0.0
    optimization_goal: str = "conversions"

@dataclass
class CampaignSchedule:
    """Campaign scheduling configuration"""
    start_date: datetime = None
    end_date: datetime = None
    time_zones: List[str] = None
    day_parting: Dict[str, Any] = None
    frequency_capping: Dict[str, Any] = None

@dataclass
class CreativeAsset:
    """Creative asset information"""
    asset_id: str
    asset_type: AssetType
    file_name: str
    file_size: int
    mime_type: str
    dimensions: Dict[str, int] = None
    url: str = None
    thumbnail_url: str = None
    tags: List[str] = None
    created_at: datetime = None

class CampaignTemplate:
    """Campaign template for quick creation"""
    
    def __init__(self, template_id: str, name: str, description: str, template_data: Dict[str, Any]):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.template_data = template_data
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template_data": self.template_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class AssetManager:
    """Manages creative assets and media files"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.supported_formats = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
            'video': ['mp4', 'mov', 'avi', 'webm', 'mkv'],
            'audio': ['mp3', 'wav', 'aac', 'ogg'],
            'document': ['pdf', 'doc', 'docx', 'txt'],
            'icon': ['ico', 'png', 'svg'],
            'logo': ['png', 'svg', 'jpg', 'jpeg']
        }
        self.max_file_sizes = {
            'image': 10 * 1024 * 1024,  # 10MB
            'video': 100 * 1024 * 1024,  # 100MB
            'audio': 50 * 1024 * 1024,   # 50MB
            'document': 25 * 1024 * 1024,  # 25MB
            'icon': 5 * 1024 * 1024,     # 5MB
            'logo': 10 * 1024 * 1024     # 10MB
        }
    
    async def upload_asset(self, client_id: str, file_data: bytes, file_name: str, asset_type: AssetType) -> CreativeAsset:
        """Upload and process a creative asset"""
        try:
            # Validate file
            file_extension = file_name.split('.')[-1].lower()
            if file_extension not in self.supported_formats[asset_type.value]:
                raise ValueError(f"Unsupported file format for {asset_type.value}: {file_extension}")
            
            # Check file size
            file_size = len(file_data)
            if file_size > self.max_file_sizes[asset_type.value]:
                raise ValueError(f"File too large for {asset_type.value}: {file_size} bytes")
            
            # Generate asset ID and URLs
            asset_id = str(uuid.uuid4())
            file_url = f"/assets/{client_id}/{asset_id}/{file_name}"
            thumbnail_url = f"/assets/{client_id}/{asset_id}/thumbnail_{file_name}"
            
            # Process asset based on type
            dimensions = None
            if asset_type in [AssetType.IMAGE, AssetType.VIDEO]:
                dimensions = await self._get_asset_dimensions(file_data, asset_type)
            
            # Create thumbnail for images
            if asset_type == AssetType.IMAGE:
                thumbnail_data = await self._create_thumbnail(file_data)
                # In production, this would be saved to storage
                logger.info(f"Created thumbnail for asset {asset_id}")
            
            # Create asset record
            asset = CreativeAsset(
                asset_id=asset_id,
                asset_type=asset_type,
                file_name=file_name,
                file_size=file_size,
                mime_type=mimetypes.guess_type(file_name)[0] or 'application/octet-stream',
                dimensions=dimensions,
                url=file_url,
                thumbnail_url=thumbnail_url,
                tags=[],
                created_at=datetime.utcnow()
            )
            
            # Save to database
            asset_doc = {
                "asset_id": asset.asset_id,
                "client_id": client_id,
                "asset_type": asset.asset_type.value,
                "file_name": asset.file_name,
                "file_size": asset.file_size,
                "mime_type": asset.mime_type,
                "dimensions": asset.dimensions,
                "url": asset.url,
                "thumbnail_url": asset.thumbnail_url,
                "tags": asset.tags,
                "created_at": asset.created_at.isoformat(),
                "is_active": True
            }
            
            await self.db.creative_assets.insert_one(asset_doc)
            
            logger.info(f"Uploaded asset {asset_id} for client {client_id}")
            return asset
            
        except Exception as e:
            logger.error(f"Error uploading asset: {e}")
            raise
    
    async def _get_asset_dimensions(self, file_data: bytes, asset_type: AssetType) -> Dict[str, int]:
        """Get asset dimensions"""
        try:
            if asset_type == AssetType.IMAGE:
                image = Image.open(io.BytesIO(file_data))
                return {"width": image.width, "height": image.height}
            elif asset_type == AssetType.VIDEO:
                # In production, use ffprobe or similar to get video dimensions
                return {"width": 1920, "height": 1080}  # Placeholder
            return None
        except Exception as e:
            logger.error(f"Error getting asset dimensions: {e}")
            return None
    
    async def _create_thumbnail(self, image_data: bytes) -> bytes:
        """Create thumbnail for image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return image_data
    
    async def get_client_assets(self, client_id: str, asset_type: Optional[AssetType] = None) -> List[CreativeAsset]:
        """Get all assets for a client"""
        try:
            query = {"client_id": client_id, "is_active": True}
            if asset_type:
                query["asset_type"] = asset_type.value
            
            assets_docs = await self.db.creative_assets.find(query).to_list(length=None)
            
            assets = []
            for doc in assets_docs:
                asset = CreativeAsset(
                    asset_id=doc["asset_id"],
                    asset_type=AssetType(doc["asset_type"]),
                    file_name=doc["file_name"],
                    file_size=doc["file_size"],
                    mime_type=doc["mime_type"],
                    dimensions=doc.get("dimensions"),
                    url=doc["url"],
                    thumbnail_url=doc["thumbnail_url"],
                    tags=doc["tags"],
                    created_at=datetime.fromisoformat(doc["created_at"])
                )
                assets.append(asset)
            
            return assets
            
        except Exception as e:
            logger.error(f"Error getting client assets: {e}")
            raise
    
    async def delete_asset(self, asset_id: str, client_id: str) -> bool:
        """Delete an asset (soft delete)"""
        try:
            result = await self.db.creative_assets.update_one(
                {"asset_id": asset_id, "client_id": client_id},
                {"$set": {"is_active": False, "deleted_at": datetime.utcnow().isoformat()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {e}")
            raise

class CampaignBuilder:
    """Builds and manages campaigns"""
    
    def __init__(self, db: AsyncIOMotorClient, asset_manager: AssetManager):
        self.db = db
        self.asset_manager = asset_manager
        self.campaign_templates = self._load_default_templates()
    
    def _load_default_templates(self) -> List[CampaignTemplate]:
        """Load default campaign templates"""
        templates = [
            CampaignTemplate(
                template_id="search_brand_awareness",
                name="Search Brand Awareness",
                description="High-intent search campaigns for brand awareness",
                template_data={
                    "campaign_type": CampaignType.SEARCH.value,
                    "budget": {"daily_budget": 100.0, "bid_strategy": "target_cpa"},
                    "targeting": {"demographics": {"age_range": "25-54"}, "locations": ["US"]},
                    "optimization_goal": "brand_awareness",
                    "schedule": {"start_date": "immediate", "end_date": "30_days"}
                }
            ),
            CampaignTemplate(
                template_id="social_conversion",
                name="Social Conversion Campaign",
                description="Social media campaigns optimized for conversions",
                template_data={
                    "campaign_type": CampaignType.SOCIAL.value,
                    "budget": {"daily_budget": 50.0, "bid_strategy": "target_roas"},
                    "targeting": {"interests": ["technology", "business"], "behaviors": ["online_shoppers"]},
                    "optimization_goal": "conversions",
                    "schedule": {"start_date": "immediate", "end_date": "14_days"}
                }
            ),
            CampaignTemplate(
                template_id="video_engagement",
                name="Video Engagement Campaign",
                description="Video campaigns for engagement and brand awareness",
                template_data={
                    "campaign_type": CampaignType.VIDEO.value,
                    "budget": {"daily_budget": 75.0, "bid_strategy": "target_cpm"},
                    "targeting": {"demographics": {"age_range": "18-34"}, "interests": ["entertainment"]},
                    "optimization_goal": "video_views",
                    "schedule": {"start_date": "immediate", "end_date": "21_days"}
                }
            ),
            CampaignTemplate(
                template_id="email_nurture",
                name="Email Nurture Campaign",
                description="Email campaigns for lead nurturing",
                template_data={
                    "campaign_type": CampaignType.EMAIL.value,
                    "budget": {"daily_budget": 25.0, "bid_strategy": "manual"},
                    "targeting": {"custom_audiences": ["email_subscribers"]},
                    "optimization_goal": "email_opens",
                    "schedule": {"start_date": "immediate", "end_date": "7_days"}
                }
            )
        ]
        return templates
    
    async def create_campaign_from_template(self, client_id: str, template_id: str, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign from template with customizations"""
        try:
            # Find template
            template = next((t for t in self.campaign_templates if t.template_id == template_id), None)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Generate campaign ID
            campaign_id = str(uuid.uuid4())
            
            # Merge template data with customizations
            campaign_data = template.template_data.copy()
            campaign_data.update(customizations)
            
            # Create campaign document
            campaign_doc = {
                "campaign_id": campaign_id,
                "client_id": client_id,
                "name": customizations.get("name", f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d')}"),
                "description": customizations.get("description", template.description),
                "template_id": template_id,
                "campaign_type": campaign_data["campaign_type"],
                "status": CampaignStatus.DRAFT.value,
                "budget": campaign_data["budget"],
                "targeting": campaign_data["targeting"],
                "schedule": campaign_data["schedule"],
                "optimization_goal": campaign_data["optimization_goal"],
                "creatives": [],
                "performance": {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "cost": 0.0,
                    "revenue": 0.0
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Save to database
            await self.db.campaigns.insert_one(campaign_doc)
            
            logger.info(f"Created campaign {campaign_id} from template {template_id} for client {client_id}")
            
            return {
                "campaign_id": campaign_id,
                "name": campaign_doc["name"],
                "description": campaign_doc["description"],
                "template_id": template_id,
                "campaign_type": campaign_doc["campaign_type"],
                "status": campaign_doc["status"],
                "created_at": campaign_doc["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign from template: {e}")
            raise
    
    async def create_custom_campaign(self, client_id: str, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom campaign from scratch"""
        try:
            campaign_id = str(uuid.uuid4())
            
            # Validate required fields
            required_fields = ["name", "campaign_type", "budget", "targeting"]
            for field in required_fields:
                if field not in campaign_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create campaign document
            campaign_doc = {
                "campaign_id": campaign_id,
                "client_id": client_id,
                "name": campaign_config["name"],
                "description": campaign_config.get("description", ""),
                "template_id": None,
                "campaign_type": campaign_config["campaign_type"],
                "status": CampaignStatus.DRAFT.value,
                "budget": campaign_config["budget"],
                "targeting": campaign_config["targeting"],
                "schedule": campaign_config.get("schedule", {}),
                "optimization_goal": campaign_config.get("optimization_goal", "conversions"),
                "creatives": campaign_config.get("creatives", []),
                "performance": {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "cost": 0.0,
                    "revenue": 0.0
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Save to database
            await self.db.campaigns.insert_one(campaign_doc)
            
            logger.info(f"Created custom campaign {campaign_id} for client {client_id}")
            
            return {
                "campaign_id": campaign_id,
                "name": campaign_doc["name"],
                "description": campaign_doc["description"],
                "campaign_type": campaign_doc["campaign_type"],
                "status": campaign_doc["status"],
                "created_at": campaign_doc["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error creating custom campaign: {e}")
            raise
    
    async def get_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Get campaign details"""
        try:
            campaign = await self.db.campaigns.find_one({
                "campaign_id": campaign_id,
                "client_id": client_id,
                "is_active": True
            })
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error getting campaign {campaign_id}: {e}")
            raise
    
    async def update_campaign(self, campaign_id: str, client_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign configuration"""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db.campaigns.update_one(
                {"campaign_id": campaign_id, "client_id": client_id, "is_active": True},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Get updated campaign
            updated_campaign = await self.get_campaign(campaign_id, client_id)
            
            logger.info(f"Updated campaign {campaign_id}")
            
            return updated_campaign
            
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {e}")
            raise
    
    async def get_client_campaigns(self, client_id: str, status: Optional[CampaignStatus] = None) -> List[Dict[str, Any]]:
        """Get all campaigns for a client"""
        try:
            query = {"client_id": client_id, "is_active": True}
            if status:
                query["status"] = status.value
            
            campaigns = await self.db.campaigns.find(query).sort("created_at", -1).to_list(length=None)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting client campaigns: {e}")
            raise
    
    async def launch_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Launch a campaign"""
        try:
            # Get campaign
            campaign = await self.get_campaign(campaign_id, client_id)
            
            # Validate campaign is ready to launch
            if not campaign.get("creatives"):
                raise ValueError("Campaign must have creatives before launching")
            
            # Update status to active
            updates = {
                "status": CampaignStatus.ACTIVE.value,
                "launched_at": datetime.utcnow().isoformat()
            }
            
            updated_campaign = await self.update_campaign(campaign_id, client_id, updates)
            
            logger.info(f"Launched campaign {campaign_id}")
            
            return updated_campaign
            
        except Exception as e:
            logger.error(f"Error launching campaign {campaign_id}: {e}")
            raise
    
    async def pause_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Pause a campaign"""
        try:
            updates = {
                "status": CampaignStatus.PAUSED.value,
                "paused_at": datetime.utcnow().isoformat()
            }
            
            updated_campaign = await self.update_campaign(campaign_id, client_id, updates)
            
            logger.info(f"Paused campaign {campaign_id}")
            
            return updated_campaign
            
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {e}")
            raise
    
    async def archive_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Archive a campaign"""
        try:
            updates = {
                "status": CampaignStatus.ARCHIVED.value,
                "archived_at": datetime.utcnow().isoformat(),
                "is_active": False
            }
            
            await self.db.campaigns.update_one(
                {"campaign_id": campaign_id, "client_id": client_id},
                {"$set": updates}
            )
            
            logger.info(f"Archived campaign {campaign_id}")
            
            return {"campaign_id": campaign_id, "status": "archived"}
            
        except Exception as e:
            logger.error(f"Error archiving campaign {campaign_id}: {e}")
            raise

class A_BTestingManager:
    """Manages A/B testing for campaigns"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def create_ab_test(self, client_id: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create A/B test for campaigns"""
        try:
            test_id = str(uuid.uuid4())
            
            ab_test_doc = {
                "test_id": test_id,
                "client_id": client_id,
                "name": test_config["name"],
                "description": test_config.get("description", ""),
                "test_type": test_config["test_type"],  # creative, audience, budget, etc.
                "variants": test_config["variants"],
                "traffic_split": test_config.get("traffic_split", 50),  # 50/50 split
                "success_metric": test_config.get("success_metric", "conversions"),
                "minimum_sample_size": test_config.get("minimum_sample_size", 1000),
                "test_duration_days": test_config.get("test_duration_days", 14),
                "status": "draft",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            await self.db.ab_tests.insert_one(ab_test_doc)
            
            logger.info(f"Created A/B test {test_id} for client {client_id}")
            
            return {
                "test_id": test_id,
                "name": ab_test_doc["name"],
                "test_type": ab_test_doc["test_type"],
                "status": ab_test_doc["status"],
                "created_at": ab_test_doc["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            raise
    
    async def get_ab_test_results(self, test_id: str, client_id: str) -> Dict[str, Any]:
        """Get A/B test results"""
        try:
            test = await self.db.ab_tests.find_one({
                "test_id": test_id,
                "client_id": client_id,
                "is_active": True
            })
            
            if not test:
                raise ValueError(f"A/B test {test_id} not found")
            
            # Get performance data for each variant
            results = []
            for variant in test["variants"]:
                variant_performance = await self._get_variant_performance(test_id, variant["variant_id"])
                results.append({
                    "variant_id": variant["variant_id"],
                    "variant_name": variant["name"],
                    "performance": variant_performance
                })
            
            # Calculate statistical significance
            significance = await self._calculate_significance(results)
            
            return {
                "test_id": test_id,
                "name": test["name"],
                "test_type": test["test_type"],
                "status": test["status"],
                "results": results,
                "significance": significance,
                "recommendation": self._get_recommendation(results, significance)
            }
            
        except Exception as e:
            logger.error(f"Error getting A/B test results: {e}")
            raise
    
    async def _get_variant_performance(self, test_id: str, variant_id: str) -> Dict[str, Any]:
        """Get performance data for a variant"""
        # This would query actual performance data
        # For now, return mock data
        return {
            "impressions": 10000,
            "clicks": 500,
            "conversions": 25,
            "cost": 1000.0,
            "revenue": 2500.0,
            "ctr": 5.0,
            "conversion_rate": 5.0,
            "cpa": 40.0,
            "roas": 2.5
        }
    
    async def _calculate_significance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistical significance"""
        # This would implement proper statistical significance testing
        # For now, return mock data
        return {
            "is_significant": True,
            "confidence_level": 95.0,
            "p_value": 0.03,
            "effect_size": 0.15
        }
    
    def _get_recommendation(self, results: List[Dict[str, Any]], significance: Dict[str, Any]) -> str:
        """Get recommendation based on results"""
        if not significance["is_significant"]:
            return "Test is not statistically significant. Continue testing or increase sample size."
        
        # Find best performing variant
        best_variant = max(results, key=lambda x: x["performance"]["roas"])
        return f"Variant '{best_variant['variant_name']}' is performing best with {best_variant['performance']['roas']:.2f}x ROAS. Consider implementing this variant."

class CampaignManagementService:
    """Main service for campaign management"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.asset_manager = AssetManager(db)
        self.campaign_builder = CampaignBuilder(db, self.asset_manager)
        self.ab_testing_manager = A_BTestingManager(db)
    
    async def get_campaign_templates(self) -> List[Dict[str, Any]]:
        """Get available campaign templates"""
        return [template.to_dict() for template in self.campaign_builder.campaign_templates]
    
    async def create_campaign_from_template(self, client_id: str, template_id: str, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign from template"""
        return await self.campaign_builder.create_campaign_from_template(client_id, template_id, customizations)
    
    async def create_custom_campaign(self, client_id: str, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom campaign"""
        return await self.campaign_builder.create_custom_campaign(client_id, campaign_config)
    
    async def get_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Get campaign details"""
        return await self.campaign_builder.get_campaign(campaign_id, client_id)
    
    async def update_campaign(self, campaign_id: str, client_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign"""
        return await self.campaign_builder.update_campaign(campaign_id, client_id, updates)
    
    async def get_client_campaigns(self, client_id: str, status: Optional[CampaignStatus] = None) -> List[Dict[str, Any]]:
        """Get client campaigns"""
        return await self.campaign_builder.get_client_campaigns(client_id, status)
    
    async def launch_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Launch campaign"""
        return await self.campaign_builder.launch_campaign(campaign_id, client_id)
    
    async def pause_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Pause campaign"""
        return await self.campaign_builder.pause_campaign(campaign_id, client_id)
    
    async def archive_campaign(self, campaign_id: str, client_id: str) -> Dict[str, Any]:
        """Archive campaign"""
        return await self.campaign_builder.archive_campaign(campaign_id, client_id)
    
    async def upload_asset(self, client_id: str, file_data: bytes, file_name: str, asset_type: AssetType) -> CreativeAsset:
        """Upload creative asset"""
        return await self.asset_manager.upload_asset(client_id, file_data, file_name, asset_type)
    
    async def get_client_assets(self, client_id: str, asset_type: Optional[AssetType] = None) -> List[CreativeAsset]:
        """Get client assets"""
        return await self.asset_manager.get_client_assets(client_id, asset_type)
    
    async def delete_asset(self, asset_id: str, client_id: str) -> bool:
        """Delete asset"""
        return await self.asset_manager.delete_asset(asset_id, client_id)
    
    async def create_ab_test(self, client_id: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create A/B test"""
        return await self.ab_testing_manager.create_ab_test(client_id, test_config)
    
    async def get_ab_test_results(self, test_id: str, client_id: str) -> Dict[str, Any]:
        """Get A/B test results"""
        return await self.ab_testing_manager.get_ab_test_results(test_id, client_id)

# Global instance
campaign_management_service = None

def get_campaign_management_service(db: AsyncIOMotorClient) -> CampaignManagementService:
    """Get campaign management service instance"""
    global campaign_management_service
    if campaign_management_service is None:
        campaign_management_service = CampaignManagementService(db)
    return campaign_management_service
