"""
Real-Time Personalization Engine
Production-grade personalization with dynamic content, audience segmentation, and behavioral targeting
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import numpy as np
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import redis
import hashlib

logger = logging.getLogger(__name__)

class PersonalizationType(str, Enum):
    """Types of personalization"""
    CONTENT = "content"
    CREATIVE = "creative"
    TARGETING = "targeting"
    PRICING = "pricing"
    TIMING = "timing"
    CHANNEL = "channel"

class AudienceSegment(str, Enum):
    """Audience segment types"""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    TECHNOLOGICAL = "technological"
    CUSTOM = "custom"

class ContentType(str, Enum):
    """Content types for personalization"""
    EMAIL = "email"
    AD_CREATIVE = "ad_creative"
    LANDING_PAGE = "landing_page"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    NOTIFICATION = "notification"
    BANNER = "banner"

class BehavioralEvent(str, Enum):
    """Behavioral events for tracking"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    CONVERSION = "conversion"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    CART_ADD = "cart_add"
    CART_ABANDON = "cart_abandon"
    SEARCH = "search"
    DOWNLOAD = "download"
    VIDEO_VIEW = "video_view"

@dataclass
class UserProfile:
    """User profile data"""
    user_id: str
    demographics: Dict[str, Any]
    behaviors: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    segments: List[str]
    engagement_score: float
    last_updated: datetime

@dataclass
class AudienceSegment:
    """Audience segment definition"""
    segment_id: str
    name: str
    segment_type: AudienceSegment
    criteria: Dict[str, Any]
    size: int
    description: str
    created_at: datetime

@dataclass
class PersonalizedContent:
    """Personalized content item"""
    content_id: str
    content_type: ContentType
    user_id: str
    segment_id: str
    content_data: Dict[str, Any]
    personalization_rules: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class BehavioralEvent:
    """Behavioral event data"""
    event_id: str
    user_id: str
    event_type: BehavioralEvent
    properties: Dict[str, Any]
    timestamp: datetime
    session_id: str
    page_url: Optional[str]

class UserProfileManager:
    """Manages user profiles and behavioral data"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.profile_cache_ttl = 3600  # 1 hour
    
    async def create_user_profile(self, user_id: str, initial_data: Dict[str, Any]) -> UserProfile:
        """Create a new user profile"""
        try:
            profile = UserProfile(
                user_id=user_id,
                demographics=initial_data.get("demographics", {}),
                behaviors=[],
                preferences=initial_data.get("preferences", {}),
                segments=[],
                engagement_score=0.0,
                last_updated=datetime.utcnow()
            )
            
            # Save to database
            await self._save_profile(profile)
            
            # Cache in Redis
            await self._cache_profile(profile)
            
            logger.info(f"Created user profile for {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile with caching"""
        try:
            # Try cache first
            cached_profile = await self._get_cached_profile(user_id)
            if cached_profile:
                return cached_profile
            
            # Get from database
            profile_doc = await self.db.user_profiles.find_one({"user_id": user_id})
            if not profile_doc:
                return None
            
            profile = self._doc_to_profile(profile_doc)
            
            # Cache the profile
            await self._cache_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """Update user profile with new data"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile {user_id} not found")
            
            # Update profile fields
            if "demographics" in updates:
                profile.demographics.update(updates["demographics"])
            
            if "preferences" in updates:
                profile.preferences.update(updates["preferences"])
            
            if "behaviors" in updates:
                profile.behaviors.extend(updates["behaviors"])
            
            profile.last_updated = datetime.utcnow()
            
            # Recalculate engagement score
            profile.engagement_score = await self._calculate_engagement_score(profile)
            
            # Save updated profile
            await self._save_profile(profile)
            await self._cache_profile(profile)
            
            logger.info(f"Updated user profile for {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    async def track_behavioral_event(self, user_id: str, event: BehavioralEvent) -> None:
        """Track a behavioral event for a user"""
        try:
            # Save event to database
            event_doc = {
                "event_id": event.event_id,
                "user_id": user_id,
                "event_type": event.event_type.value,
                "properties": event.properties,
                "timestamp": event.timestamp.isoformat(),
                "session_id": event.session_id,
                "page_url": event.page_url
            }
            
            await self.db.behavioral_events.insert_one(event_doc)
            
            # Update user profile with event
            await self._update_profile_with_event(user_id, event)
            
            # Update real-time segments
            await self._update_real_time_segments(user_id, event)
            
            logger.info(f"Tracked behavioral event {event.event_type.value} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking behavioral event: {e}")
            raise
    
    async def _update_profile_with_event(self, user_id: str, event: BehavioralEvent):
        """Update user profile based on behavioral event"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return
            
            # Add event to behaviors
            behavior_data = {
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "properties": event.properties
            }
            
            profile.behaviors.append(behavior_data)
            
            # Keep only last 100 behaviors
            if len(profile.behaviors) > 100:
                profile.behaviors = profile.behaviors[-100:]
            
            # Update preferences based on event
            await self._update_preferences_from_event(profile, event)
            
            # Save updated profile
            await self._save_profile(profile)
            await self._cache_profile(profile)
            
        except Exception as e:
            logger.error(f"Error updating profile with event: {e}")
    
    async def _update_preferences_from_event(self, profile: UserProfile, event: BehavioralEvent):
        """Update user preferences based on behavioral event"""
        try:
            if event.event_type == BehavioralEvent.CLICK:
                # Update click preferences
                clicked_item = event.properties.get("item_type")
                if clicked_item:
                    if "click_preferences" not in profile.preferences:
                        profile.preferences["click_preferences"] = {}
                    
                    profile.preferences["click_preferences"][clicked_item] = \
                        profile.preferences["click_preferences"].get(clicked_item, 0) + 1
            
            elif event.event_type == BehavioralEvent.CONVERSION:
                # Update conversion preferences
                product_category = event.properties.get("product_category")
                if product_category:
                    if "conversion_preferences" not in profile.preferences:
                        profile.preferences["conversion_preferences"] = {}
                    
                    profile.preferences["conversion_preferences"][product_category] = \
                        profile.preferences["conversion_preferences"].get(product_category, 0) + 1
            
            elif event.event_type == BehavioralEvent.SEARCH:
                # Update search preferences
                search_query = event.properties.get("query")
                if search_query:
                    if "search_preferences" not in profile.preferences:
                        profile.preferences["search_preferences"] = []
                    
                    profile.preferences["search_preferences"].append(search_query)
                    
                    # Keep only last 20 searches
                    if len(profile.preferences["search_preferences"]) > 20:
                        profile.preferences["search_preferences"] = \
                            profile.preferences["search_preferences"][-20:]
            
        except Exception as e:
            logger.error(f"Error updating preferences from event: {e}")
    
    async def _calculate_engagement_score(self, profile: UserProfile) -> float:
        """Calculate user engagement score"""
        try:
            score = 0.0
            
            # Base score from demographics
            if profile.demographics.get("age"):
                age = profile.demographics["age"]
                if 25 <= age <= 45:
                    score += 0.2  # Prime demographic
            
            # Behavioral score
            recent_behaviors = [
                b for b in profile.behaviors 
                if datetime.fromisoformat(b["timestamp"]) > datetime.utcnow() - timedelta(days=30)
            ]
            
            score += min(0.5, len(recent_behaviors) * 0.05)  # Activity score
            
            # Conversion score
            conversions = [b for b in recent_behaviors if b["event_type"] == "conversion"]
            score += min(0.3, len(conversions) * 0.1)
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    async def _update_real_time_segments(self, user_id: str, event: BehavioralEvent):
        """Update real-time audience segments"""
        try:
            # Get active segments
            segments = await self.db.audience_segments.find({"active": True}).to_list(length=None)
            
            for segment_doc in segments:
                segment = self._doc_to_segment(segment_doc)
                
                # Check if user matches segment criteria
                if await self._user_matches_segment(user_id, segment):
                    # Add user to segment
                    await self.redis.sadd(f"segment:{segment.segment_id}", user_id)
                else:
                    # Remove user from segment
                    await self.redis.srem(f"segment:{segment.segment_id}", user_id)
            
        except Exception as e:
            logger.error(f"Error updating real-time segments: {e}")
    
    async def _user_matches_segment(self, user_id: str, segment: AudienceSegment) -> bool:
        """Check if user matches segment criteria"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return False
            
            criteria = segment.criteria
            
            # Demographic criteria
            if "demographics" in criteria:
                demo_criteria = criteria["demographics"]
                for field, value in demo_criteria.items():
                    if profile.demographics.get(field) != value:
                        return False
            
            # Behavioral criteria
            if "behaviors" in criteria:
                behavior_criteria = criteria["behaviors"]
                for behavior in behavior_criteria:
                    if not self._check_behavior_criteria(profile, behavior):
                        return False
            
            # Engagement criteria
            if "min_engagement_score" in criteria:
                if profile.engagement_score < criteria["min_engagement_score"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user segment match: {e}")
            return False
    
    def _check_behavior_criteria(self, profile: UserProfile, criteria: Dict[str, Any]) -> bool:
        """Check if user meets behavioral criteria"""
        try:
            event_type = criteria.get("event_type")
            min_count = criteria.get("min_count", 1)
            time_window = criteria.get("time_window_days", 30)
            
            cutoff_date = datetime.utcnow() - timedelta(days=time_window)
            
            matching_behaviors = [
                b for b in profile.behaviors
                if b["event_type"] == event_type and
                datetime.fromisoformat(b["timestamp"]) > cutoff_date
            ]
            
            return len(matching_behaviors) >= min_count
            
        except Exception as e:
            logger.error(f"Error checking behavior criteria: {e}")
            return False
    
    async def _save_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            profile_doc = {
                "user_id": profile.user_id,
                "demographics": profile.demographics,
                "behaviors": profile.behaviors,
                "preferences": profile.preferences,
                "segments": profile.segments,
                "engagement_score": profile.engagement_score,
                "last_updated": profile.last_updated.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.db.user_profiles.replace_one(
                {"user_id": profile.user_id},
                profile_doc,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            raise
    
    async def _cache_profile(self, profile: UserProfile):
        """Cache user profile in Redis"""
        try:
            profile_data = json.dumps(profile.__dict__, default=str)
            await self.redis.setex(
                f"profile:{profile.user_id}",
                self.profile_cache_ttl,
                profile_data
            )
            
        except Exception as e:
            logger.error(f"Error caching profile: {e}")
    
    async def _get_cached_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get cached user profile from Redis"""
        try:
            cached_data = await self.redis.get(f"profile:{user_id}")
            if cached_data:
                profile_dict = json.loads(cached_data)
                return UserProfile(**profile_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached profile: {e}")
            return None
    
    def _doc_to_profile(self, doc: Dict[str, Any]) -> UserProfile:
        """Convert database document to UserProfile"""
        return UserProfile(
            user_id=doc["user_id"],
            demographics=doc["demographics"],
            behaviors=doc["behaviors"],
            preferences=doc["preferences"],
            segments=doc["segments"],
            engagement_score=doc["engagement_score"],
            last_updated=datetime.fromisoformat(doc["last_updated"])
        )
    
    def _doc_to_segment(self, doc: Dict[str, Any]) -> AudienceSegment:
        """Convert database document to AudienceSegment"""
        return AudienceSegment(
            segment_id=doc["segment_id"],
            name=doc["name"],
            segment_type=AudienceSegment(doc["segment_type"]),
            criteria=doc["criteria"],
            size=doc["size"],
            description=doc["description"],
            created_at=datetime.fromisoformat(doc["created_at"])
        )

class AudienceSegmentationEngine:
    """Engine for audience segmentation and analysis"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.segmentation_models = {}
    
    async def create_audience_segment(self, segment_data: Dict[str, Any]) -> str:
        """Create a new audience segment"""
        try:
            segment_id = str(uuid.uuid4())
            
            segment = AudienceSegment(
                segment_id=segment_id,
                name=segment_data["name"],
                segment_type=AudienceSegment(segment_data["segment_type"]),
                criteria=segment_data["criteria"],
                size=0,  # Will be calculated
                description=segment_data.get("description", ""),
                created_at=datetime.utcnow()
            )
            
            # Calculate segment size
            segment.size = await self._calculate_segment_size(segment)
            
            # Save segment
            await self._save_segment(segment)
            
            # Populate segment with users
            await self._populate_segment(segment)
            
            logger.info(f"Created audience segment {segment_id}: {segment.name}")
            return segment_id
            
        except Exception as e:
            logger.error(f"Error creating audience segment: {e}")
            raise
    
    async def _calculate_segment_size(self, segment: AudienceSegment) -> int:
        """Calculate the size of an audience segment"""
        try:
            # Get all users
            users = await self.db.user_profiles.find({}).to_list(length=None)
            
            matching_users = 0
            for user_doc in users:
                user_id = user_doc["user_id"]
                if await self._user_matches_segment_criteria(user_id, segment.criteria):
                    matching_users += 1
            
            return matching_users
            
        except Exception as e:
            logger.error(f"Error calculating segment size: {e}")
            return 0
    
    async def _user_matches_segment_criteria(self, user_id: str, criteria: Dict[str, Any]) -> bool:
        """Check if user matches segment criteria"""
        try:
            profile_doc = await self.db.user_profiles.find_one({"user_id": user_id})
            if not profile_doc:
                return False
            
            # Check demographic criteria
            if "demographics" in criteria:
                demo_criteria = criteria["demographics"]
                for field, value in demo_criteria.items():
                    if profile_doc["demographics"].get(field) != value:
                        return False
            
            # Check behavioral criteria
            if "behaviors" in criteria:
                behavior_criteria = criteria["behaviors"]
                for behavior in behavior_criteria:
                    if not self._check_behavior_criteria(profile_doc, behavior):
                        return False
            
            # Check engagement criteria
            if "min_engagement_score" in criteria:
                if profile_doc["engagement_score"] < criteria["min_engagement_score"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user segment criteria: {e}")
            return False
    
    def _check_behavior_criteria(self, profile_doc: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if user meets behavioral criteria"""
        try:
            event_type = criteria.get("event_type")
            min_count = criteria.get("min_count", 1)
            time_window = criteria.get("time_window_days", 30)
            
            cutoff_date = datetime.utcnow() - timedelta(days=time_window)
            
            matching_behaviors = [
                b for b in profile_doc["behaviors"]
                if b["event_type"] == event_type and
                datetime.fromisoformat(b["timestamp"]) > cutoff_date
            ]
            
            return len(matching_behaviors) >= min_count
            
        except Exception as e:
            logger.error(f"Error checking behavior criteria: {e}")
            return False
    
    async def _populate_segment(self, segment: AudienceSegment):
        """Populate segment with matching users"""
        try:
            # Get all users
            users = await self.db.user_profiles.find({}).to_list(length=None)
            
            matching_users = []
            for user_doc in users:
                user_id = user_doc["user_id"]
                if await self._user_matches_segment_criteria(user_id, segment.criteria):
                    matching_users.append(user_id)
            
            # Store in Redis for fast access
            if matching_users:
                await self.redis.sadd(f"segment:{segment.segment_id}", *matching_users)
            
        except Exception as e:
            logger.error(f"Error populating segment: {e}")
    
    async def get_segment_users(self, segment_id: str) -> List[str]:
        """Get users in a segment"""
        try:
            users = await self.redis.smembers(f"segment:{segment_id}")
            return [user.decode('utf-8') for user in users]
            
        except Exception as e:
            logger.error(f"Error getting segment users: {e}")
            return []
    
    async def analyze_segment_performance(self, segment_id: str) -> Dict[str, Any]:
        """Analyze segment performance metrics"""
        try:
            users = await self.get_segment_users(segment_id)
            
            if not users:
                return {"error": "No users in segment"}
            
            # Get behavioral data for segment users
            behaviors = await self.db.behavioral_events.find({
                "user_id": {"$in": users}
            }).to_list(length=None)
            
            # Calculate metrics
            total_events = len(behaviors)
            unique_users = len(set(b["user_id"] for b in behaviors))
            
            # Event type distribution
            event_types = {}
            for behavior in behaviors:
                event_type = behavior["event_type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Conversion rate
            conversions = [b for b in behaviors if b["event_type"] == "conversion"]
            conversion_rate = len(conversions) / len(users) if users else 0
            
            return {
                "segment_id": segment_id,
                "total_users": len(users),
                "total_events": total_events,
                "events_per_user": total_events / len(users) if users else 0,
                "conversion_rate": conversion_rate,
                "event_type_distribution": event_types,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing segment performance: {e}")
            return {}
    
    async def _save_segment(self, segment: AudienceSegment):
        """Save audience segment to database"""
        try:
            segment_doc = {
                "segment_id": segment.segment_id,
                "name": segment.name,
                "segment_type": segment.segment_type.value,
                "criteria": segment.criteria,
                "size": segment.size,
                "description": segment.description,
                "created_at": segment.created_at.isoformat(),
                "active": True
            }
            
            await self.db.audience_segments.insert_one(segment_doc)
            
        except Exception as e:
            logger.error(f"Error saving segment: {e}")
            raise

class ContentPersonalizationEngine:
    """Engine for content personalization"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis, profile_manager: UserProfileManager):
        self.db = db
        self.redis = redis_client
        self.profile_manager = profile_manager
        self.content_templates = {}
        self.personalization_rules = {}
    
    async def personalize_content(self, user_id: str, content_type: ContentType, base_content: Dict[str, Any]) -> PersonalizedContent:
        """Personalize content for a specific user"""
        try:
            # Get user profile
            profile = await self.profile_manager.get_user_profile(user_id)
            if not profile:
                # Return base content if no profile
                return PersonalizedContent(
                    content_id=str(uuid.uuid4()),
                    content_type=content_type,
                    user_id=user_id,
                    segment_id="",
                    content_data=base_content,
                    personalization_rules=[],
                    created_at=datetime.utcnow()
                )
            
            # Determine user segments
            segments = await self._get_user_segments(user_id)
            
            # Apply personalization rules
            personalized_content = await self._apply_personalization_rules(
                base_content, profile, segments, content_type
            )
            
            # Create personalized content record
            personalized = PersonalizedContent(
                content_id=str(uuid.uuid4()),
                content_type=content_type,
                user_id=user_id,
                segment_id=segments[0] if segments else "",
                content_data=personalized_content,
                personalization_rules=self._get_applied_rules(profile, segments),
                created_at=datetime.utcnow()
            )
            
            # Save personalized content
            await self._save_personalized_content(personalized)
            
            return personalized
            
        except Exception as e:
            logger.error(f"Error personalizing content: {e}")
            raise
    
    async def _get_user_segments(self, user_id: str) -> List[str]:
        """Get user's audience segments"""
        try:
            # Get all active segments
            segments = await self.db.audience_segments.find({"active": True}).to_list(length=None)
            
            user_segments = []
            for segment_doc in segments:
                segment_id = segment_doc["segment_id"]
                
                # Check if user is in segment
                is_member = await self.redis.sismember(f"segment:{segment_id}", user_id)
                if is_member:
                    user_segments.append(segment_id)
            
            return user_segments
            
        except Exception as e:
            logger.error(f"Error getting user segments: {e}")
            return []
    
    async def _apply_personalization_rules(self, base_content: Dict[str, Any], profile: UserProfile, segments: List[str], content_type: ContentType) -> Dict[str, Any]:
        """Apply personalization rules to content"""
        try:
            personalized_content = base_content.copy()
            
            # Apply demographic personalization
            personalized_content = await self._apply_demographic_personalization(
                personalized_content, profile.demographics, content_type
            )
            
            # Apply behavioral personalization
            personalized_content = await self._apply_behavioral_personalization(
                personalized_content, profile.behaviors, content_type
            )
            
            # Apply preference personalization
            personalized_content = await self._apply_preference_personalization(
                personalized_content, profile.preferences, content_type
            )
            
            # Apply segment-based personalization
            personalized_content = await self._apply_segment_personalization(
                personalized_content, segments, content_type
            )
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying personalization rules: {e}")
            return base_content
    
    async def _apply_demographic_personalization(self, content: Dict[str, Any], demographics: Dict[str, Any], content_type: ContentType) -> Dict[str, Any]:
        """Apply demographic-based personalization"""
        try:
            personalized_content = content.copy()
            
            # Age-based personalization
            age = demographics.get("age")
            if age:
                if age < 25:
                    # Gen Z preferences
                    personalized_content["tone"] = "casual"
                    personalized_content["style"] = "modern"
                elif age < 40:
                    # Millennial preferences
                    personalized_content["tone"] = "professional"
                    personalized_content["style"] = "contemporary"
                else:
                    # Gen X+ preferences
                    personalized_content["tone"] = "formal"
                    personalized_content["style"] = "traditional"
            
            # Gender-based personalization
            gender = demographics.get("gender")
            if gender:
                if gender == "female":
                    personalized_content["color_scheme"] = "warm"
                elif gender == "male":
                    personalized_content["color_scheme"] = "cool"
            
            # Location-based personalization
            location = demographics.get("location")
            if location:
                personalized_content["timezone"] = self._get_timezone_from_location(location)
                personalized_content["currency"] = self._get_currency_from_location(location)
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying demographic personalization: {e}")
            return content
    
    async def _apply_behavioral_personalization(self, content: Dict[str, Any], behaviors: List[Dict[str, Any]], content_type: ContentType) -> Dict[str, Any]:
        """Apply behavioral-based personalization"""
        try:
            personalized_content = content.copy()
            
            # Analyze recent behaviors
            recent_behaviors = [
                b for b in behaviors
                if datetime.fromisoformat(b["timestamp"]) > datetime.utcnow() - timedelta(days=30)
            ]
            
            # Click behavior analysis
            click_behaviors = [b for b in recent_behaviors if b["event_type"] == "click"]
            if click_behaviors:
                # Personalize based on clicked content types
                clicked_types = [b["properties"].get("content_type") for b in click_behaviors]
                most_clicked = max(set(clicked_types), key=clicked_types.count) if clicked_types else None
                
                if most_clicked:
                    personalized_content["preferred_content_type"] = most_clicked
            
            # Conversion behavior analysis
            conversion_behaviors = [b for b in recent_behaviors if b["event_type"] == "conversion"]
            if conversion_behaviors:
                # Personalize based on conversion patterns
                personalized_content["urgency_level"] = "high"
                personalized_content["call_to_action"] = "strong"
            
            # Search behavior analysis
            search_behaviors = [b for b in recent_behaviors if b["event_type"] == "search"]
            if search_behaviors:
                # Personalize based on search queries
                search_queries = [b["properties"].get("query") for b in search_behaviors]
                personalized_content["search_keywords"] = search_queries[:5]  # Top 5
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying behavioral personalization: {e}")
            return content
    
    async def _apply_preference_personalization(self, content: Dict[str, Any], preferences: Dict[str, Any], content_type: ContentType) -> Dict[str, Any]:
        """Apply preference-based personalization"""
        try:
            personalized_content = content.copy()
            
            # Click preferences
            click_preferences = preferences.get("click_preferences", {})
            if click_preferences:
                most_preferred = max(click_preferences.items(), key=lambda x: x[1])
                personalized_content["primary_content_type"] = most_preferred[0]
            
            # Conversion preferences
            conversion_preferences = preferences.get("conversion_preferences", {})
            if conversion_preferences:
                most_converted = max(conversion_preferences.items(), key=lambda x: x[1])
                personalized_content["recommended_category"] = most_converted[0]
            
            # Search preferences
            search_preferences = preferences.get("search_preferences", [])
            if search_preferences:
                personalized_content["related_keywords"] = search_preferences[-5:]  # Last 5 searches
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying preference personalization: {e}")
            return content
    
    async def _apply_segment_personalization(self, content: Dict[str, Any], segments: List[str], content_type: ContentType) -> Dict[str, Any]:
        """Apply segment-based personalization"""
        try:
            personalized_content = content.copy()
            
            for segment_id in segments:
                # Get segment-specific personalization rules
                segment_rules = await self._get_segment_personalization_rules(segment_id)
                
                for rule in segment_rules:
                    if rule["content_type"] == content_type.value:
                        # Apply segment rule
                        personalized_content.update(rule["personalization"])
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying segment personalization: {e}")
            return content
    
    async def _get_segment_personalization_rules(self, segment_id: str) -> List[Dict[str, Any]]:
        """Get personalization rules for a segment"""
        try:
            rules = await self.db.personalization_rules.find({
                "segment_id": segment_id,
                "active": True
            }).to_list(length=None)
            
            return rules
            
        except Exception as e:
            logger.error(f"Error getting segment personalization rules: {e}")
            return []
    
    def _get_applied_rules(self, profile: UserProfile, segments: List[str]) -> List[Dict[str, Any]]:
        """Get list of applied personalization rules"""
        try:
            rules = []
            
            # Demographic rules
            if profile.demographics:
                rules.append({
                    "type": "demographic",
                    "criteria": profile.demographics,
                    "applied": True
                })
            
            # Behavioral rules
            if profile.behaviors:
                recent_behaviors = [
                    b for b in profile.behaviors
                    if datetime.fromisoformat(b["timestamp"]) > datetime.utcnow() - timedelta(days=30)
                ]
                rules.append({
                    "type": "behavioral",
                    "criteria": {"recent_behaviors": len(recent_behaviors)},
                    "applied": True
                })
            
            # Segment rules
            for segment_id in segments:
                rules.append({
                    "type": "segment",
                    "criteria": {"segment_id": segment_id},
                    "applied": True
                })
            
            return rules
            
        except Exception as e:
            logger.error(f"Error getting applied rules: {e}")
            return []
    
    def _get_timezone_from_location(self, location: str) -> str:
        """Get timezone from location"""
        # Simplified timezone mapping
        timezone_map = {
            "US": "America/New_York",
            "UK": "Europe/London",
            "DE": "Europe/Berlin",
            "FR": "Europe/Paris",
            "JP": "Asia/Tokyo",
            "AU": "Australia/Sydney"
        }
        
        return timezone_map.get(location, "UTC")
    
    def _get_currency_from_location(self, location: str) -> str:
        """Get currency from location"""
        # Simplified currency mapping
        currency_map = {
            "US": "USD",
            "UK": "GBP",
            "DE": "EUR",
            "FR": "EUR",
            "JP": "JPY",
            "AU": "AUD"
        }
        
        return currency_map.get(location, "USD")
    
    async def _save_personalized_content(self, personalized: PersonalizedContent):
        """Save personalized content to database"""
        try:
            content_doc = {
                "content_id": personalized.content_id,
                "content_type": personalized.content_type.value,
                "user_id": personalized.user_id,
                "segment_id": personalized.segment_id,
                "content_data": personalized.content_data,
                "personalization_rules": personalized.personalization_rules,
                "created_at": personalized.created_at.isoformat()
            }
            
            await self.db.personalized_content.insert_one(content_doc)
            
        except Exception as e:
            logger.error(f"Error saving personalized content: {e}")
            raise

class RealTimePersonalizationService:
    """Main service for real-time personalization"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.profile_manager = UserProfileManager(db, redis_client)
        self.segmentation_engine = AudienceSegmentationEngine(db, redis_client)
        self.content_engine = ContentPersonalizationEngine(db, redis_client, self.profile_manager)
    
    async def track_user_event(self, user_id: str, event_type: BehavioralEvent, properties: Dict[str, Any], session_id: str, page_url: Optional[str] = None) -> None:
        """Track a user behavioral event"""
        try:
            event = BehavioralEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                event_type=event_type,
                properties=properties,
                timestamp=datetime.utcnow(),
                session_id=session_id,
                page_url=page_url
            )
            
            await self.profile_manager.track_behavioral_event(user_id, event)
            
        except Exception as e:
            logger.error(f"Error tracking user event: {e}")
            raise
    
    async def personalize_for_user(self, user_id: str, content_type: ContentType, base_content: Dict[str, Any]) -> PersonalizedContent:
        """Personalize content for a user"""
        return await self.content_engine.personalize_content(user_id, content_type, base_content)
    
    async def create_audience_segment(self, segment_data: Dict[str, Any]) -> str:
        """Create a new audience segment"""
        return await self.segmentation_engine.create_audience_segment(segment_data)
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return await self.profile_manager.get_user_profile(user_id)
    
    async def get_personalization_dashboard(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive personalization dashboard"""
        try:
            # Get user statistics
            total_users = await self.db.user_profiles.count_documents({})
            active_users = await self.db.user_profiles.count_documents({
                "last_updated": {"$gte": (datetime.utcnow() - timedelta(days=30)).isoformat()}
            })
            
            # Get segment statistics
            total_segments = await self.db.audience_segments.count_documents({})
            active_segments = await self.db.audience_segments.count_documents({"active": True})
            
            # Get behavioral event statistics
            total_events = await self.db.behavioral_events.count_documents({})
            recent_events = await self.db.behavioral_events.count_documents({
                "timestamp": {"$gte": (datetime.utcnow() - timedelta(days=7)).isoformat()}
            })
            
            # Get personalized content statistics
            total_personalized_content = await self.db.personalized_content.count_documents({})
            
            return {
                "client_id": client_id,
                "user_statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "engagement_rate": active_users / total_users if total_users > 0 else 0
                },
                "segment_statistics": {
                    "total_segments": total_segments,
                    "active_segments": active_segments
                },
                "behavioral_statistics": {
                    "total_events": total_events,
                    "recent_events": recent_events,
                    "events_per_user": total_events / total_users if total_users > 0 else 0
                },
                "personalization_statistics": {
                    "total_personalized_content": total_personalized_content,
                    "personalization_rate": total_personalized_content / total_users if total_users > 0 else 0
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting personalization dashboard: {e}")
            raise

# Global instance
real_time_personalization_service = None

def get_real_time_personalization_service(db: AsyncIOMotorClient, redis_client: redis.Redis) -> RealTimePersonalizationService:
    """Get real-time personalization service instance"""
    global real_time_personalization_service
    if real_time_personalization_service is None:
        real_time_personalization_service = RealTimePersonalizationService(db, redis_client)
    return real_time_personalization_service
