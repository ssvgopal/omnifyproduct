"""
Magical Customer Onboarding Wizard
Based on refs/ analysis - Modern, role-based, gamified onboarding experience
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for personalized onboarding"""
    CEO = "ceo"
    CMO = "cmo"
    MARKETING_MANAGER = "marketing_manager"
    MARKETING_SPECIALIST = "marketing_specialist"
    AGENCY_OWNER = "agency_owner"
    FREELANCER = "freelancer"

class OnboardingStep(Enum):
    """Onboarding wizard steps"""
    WELCOME = "welcome"
    ROLE_SELECTION = "role_selection"
    COMPANY_INFO = "company_info"
    PLATFORM_CONNECTION = "platform_connection"
    BRAND_SETUP = "brand_setup"
    FIRST_CAMPAIGN = "first_campaign"
    SUCCESS_DEMO = "success_demo"
    COMPLETION = "completion"

class OnboardingStatus(Enum):
    """Onboarding completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class OnboardingProgress:
    """User's onboarding progress tracking"""
    user_id: str
    organization_id: str
    current_step: OnboardingStep
    completed_steps: List[OnboardingStep] = field(default_factory=list)
    skipped_steps: List[OnboardingStep] = field(default_factory=list)
    step_data: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: float = 0.0
    estimated_time_remaining: int = 0  # minutes
    achievements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OnboardingStepData:
    """Data collected during onboarding steps"""
    step: OnboardingStep
    data: Dict[str, Any]
    completed_at: datetime = field(default_factory=datetime.utcnow)
    time_spent: int = 0  # seconds

class MagicalOnboardingWizard:
    """
    Magical Customer Onboarding Wizard
    Modern, role-based, gamified onboarding experience
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_sessions: Dict[str, OnboardingProgress] = {}
        
        # Step configurations
        self.step_configs = self._create_step_configurations()
        
        # Role-based experiences
        self.role_experiences = self._create_role_experiences()
        
        # Gamification elements
        self.achievements = self._create_achievements()
        
        logger.info("Magical Onboarding Wizard initialized")

    def _create_step_configurations(self) -> Dict[OnboardingStep, Dict[str, Any]]:
        """Create step configurations with modern design elements"""
        return {
            OnboardingStep.WELCOME: {
                "title": "Welcome to OmniFy! 🎉",
                "subtitle": "Your AI-powered marketing intelligence platform",
                "description": "Let's get you set up in just 5 minutes and show you the magic!",
                "estimated_time": 1,
                "features": [
                    "AI-powered campaign optimization",
                    "Multi-platform integration",
                    "Real-time performance insights",
                    "Proactive intelligence engine"
                ],
                "visual_elements": {
                    "icon": "🎯",
                    "background_gradient": "from-blue-500 to-purple-600",
                    "animation": "fade-in-up"
                }
            },
            OnboardingStep.ROLE_SELECTION: {
                "title": "Tell us about your role 👤",
                "subtitle": "We'll personalize your experience",
                "description": "This helps us show you the most relevant features and insights",
                "estimated_time": 1,
                "options": [
                    {
                        "role": UserRole.CEO,
                        "title": "CEO / Founder",
                        "description": "High-level insights and ROI tracking",
                        "icon": "👔",
                        "features": ["Executive dashboards", "ROI analytics", "Strategic insights"]
                    },
                    {
                        "role": UserRole.CMO,
                        "title": "CMO / Marketing Director",
                        "description": "Campaign performance and team management",
                        "icon": "📊",
                        "features": ["Campaign analytics", "Team collaboration", "Performance tracking"]
                    },
                    {
                        "role": UserRole.MARKETING_MANAGER,
                        "title": "Marketing Manager",
                        "description": "Campaign execution and optimization",
                        "icon": "🎯",
                        "features": ["Campaign management", "Creative optimization", "Platform integration"]
                    },
                    {
                        "role": UserRole.MARKETING_SPECIALIST,
                        "title": "Marketing Specialist",
                        "description": "Creative development and platform management",
                        "icon": "🎨",
                        "features": ["Creative tools", "Social media management", "Content optimization"]
                    },
                    {
                        "role": UserRole.AGENCY_OWNER,
                        "title": "Agency Owner",
                        "description": "Client management and multi-brand operations",
                        "icon": "🏢",
                        "features": ["Client dashboards", "Multi-brand management", "White-label options"]
                    },
                    {
                        "role": UserRole.FREELANCER,
                        "title": "Freelancer / Consultant",
                        "description": "Client projects and portfolio management",
                        "icon": "💼",
                        "features": ["Project management", "Client reporting", "Portfolio tracking"]
                    }
                ],
                "visual_elements": {
                    "layout": "grid",
                    "animation": "stagger-fade-in"
                }
            },
            OnboardingStep.COMPANY_INFO: {
                "title": "About your company 🏢",
                "subtitle": "Help us understand your business",
                "description": "This information helps us provide better insights and recommendations",
                "estimated_time": 2,
                "fields": [
                    {
                        "name": "company_name",
                        "label": "Company Name",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter your company name"
                    },
                    {
                        "name": "industry",
                        "label": "Industry",
                        "type": "select",
                        "required": True,
                        "options": [
                            "Technology", "Healthcare", "Finance", "Retail", "Education",
                            "Manufacturing", "Real Estate", "Food & Beverage", "Fashion",
                            "Automotive", "Travel", "Entertainment", "Other"
                        ]
                    },
                    {
                        "name": "company_size",
                        "label": "Company Size",
                        "type": "select",
                        "required": True,
                        "options": [
                            "1-10 employees", "11-50 employees", "51-200 employees",
                            "201-500 employees", "501-1000 employees", "1000+ employees"
                        ]
                    },
                    {
                        "name": "monthly_marketing_budget",
                        "label": "Monthly Marketing Budget",
                        "type": "select",
                        "required": False,
                        "options": [
                            "Under $1,000", "$1,000 - $5,000", "$5,000 - $10,000",
                            "$10,000 - $25,000", "$25,000 - $50,000", "$50,000+"
                        ]
                    }
                ],
                "visual_elements": {
                    "icon": "🏢",
                    "background_gradient": "from-green-500 to-teal-600"
                }
            },
            OnboardingStep.PLATFORM_CONNECTION: {
                "title": "Connect your platforms 🔗",
                "subtitle": "Link your marketing channels",
                "description": "Connect your existing platforms to get started with real data",
                "estimated_time": 3,
                "platforms": [
                    {
                        "name": "google_ads",
                        "title": "Google Ads",
                        "description": "Search and display advertising",
                        "icon": "🔍",
                        "color": "blue",
                        "features": ["Campaign data", "Performance metrics", "Budget optimization"]
                    },
                    {
                        "name": "meta_ads",
                        "title": "Meta Ads (Facebook/Instagram)",
                        "description": "Social media advertising",
                        "icon": "📱",
                        "color": "purple",
                        "features": ["Ad performance", "Audience insights", "Creative optimization"]
                    },
                    {
                        "name": "linkedin_ads",
                        "title": "LinkedIn Ads",
                        "description": "Professional network advertising",
                        "icon": "💼",
                        "color": "blue",
                        "features": ["B2B campaigns", "Professional targeting", "Lead generation"]
                    },
                    {
                        "name": "tiktok_ads",
                        "title": "TikTok Ads",
                        "description": "Short-form video advertising",
                        "icon": "🎵",
                        "color": "black",
                        "features": ["Video campaigns", "Trending content", "Gen Z targeting"]
                    },
                    {
                        "name": "shopify",
                        "title": "Shopify",
                        "description": "E-commerce platform",
                        "icon": "🛒",
                        "color": "green",
                        "features": ["Sales data", "Product performance", "Customer insights"]
                    },
                    {
                        "name": "gohighlevel",
                        "title": "GoHighLevel",
                        "description": "CRM and marketing automation",
                        "icon": "📈",
                        "color": "orange",
                        "features": ["Lead management", "Email campaigns", "Sales tracking"]
                    }
                ],
                "visual_elements": {
                    "layout": "grid",
                    "animation": "scale-in"
                }
            },
            OnboardingStep.BRAND_SETUP: {
                "title": "Brand guidelines 🎨",
                "subtitle": "Set up your brand identity",
                "description": "Upload your brand assets for AI-powered creative generation",
                "estimated_time": 2,
                "upload_types": [
                    {
                        "name": "logo",
                        "label": "Company Logo",
                        "description": "Upload your logo for branded content",
                        "accepted_types": ["image/png", "image/jpeg", "image/svg"],
                        "max_size": "5MB"
                    },
                    {
                        "name": "brand_colors",
                        "label": "Brand Colors",
                        "description": "Define your brand color palette",
                        "type": "color_picker",
                        "default_colors": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
                    },
                    {
                        "name": "brand_fonts",
                        "label": "Brand Fonts",
                        "description": "Specify your brand typography",
                        "type": "font_selector",
                        "options": ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat"]
                    },
                    {
                        "name": "brand_voice",
                        "label": "Brand Voice",
                        "description": "Describe your brand personality",
                        "type": "textarea",
                        "placeholder": "Professional, friendly, innovative, trustworthy..."
                    }
                ],
                "visual_elements": {
                    "icon": "🎨",
                    "background_gradient": "from-pink-500 to-rose-600"
                }
            },
            OnboardingStep.FIRST_CAMPAIGN: {
                "title": "Create your first campaign 🚀",
                "subtitle": "Let's see the magic in action",
                "description": "We'll create a sample campaign to demonstrate OmniFy's capabilities",
                "estimated_time": 3,
                "campaign_types": [
                    {
                        "name": "awareness",
                        "title": "Brand Awareness",
                        "description": "Increase brand visibility and reach",
                        "icon": "👁️",
                        "sample_data": {
                            "objective": "Brand Awareness",
                            "target_audience": "Tech-savvy millennials",
                            "budget": "$5,000",
                            "platforms": ["Meta Ads", "Google Ads"]
                        }
                    },
                    {
                        "name": "conversion",
                        "title": "Lead Generation",
                        "description": "Generate leads and drive conversions",
                        "icon": "🎯",
                        "sample_data": {
                            "objective": "Lead Generation",
                            "target_audience": "B2B decision makers",
                            "budget": "$10,000",
                            "platforms": ["LinkedIn Ads", "Google Ads"]
                        }
                    },
                    {
                        "name": "engagement",
                        "title": "Social Engagement",
                        "description": "Boost social media engagement",
                        "icon": "💬",
                        "sample_data": {
                            "objective": "Social Engagement",
                            "target_audience": "Social media active users",
                            "budget": "$3,000",
                            "platforms": ["TikTok", "Instagram"]
                        }
                    }
                ],
                "visual_elements": {
                    "icon": "🚀",
                    "background_gradient": "from-orange-500 to-red-600"
                }
            },
            OnboardingStep.SUCCESS_DEMO: {
                "title": "See the magic! ✨",
                "subtitle": "Your campaign is optimized and running",
                "description": "Watch as OmniFy's AI analyzes and optimizes your campaign in real-time",
                "estimated_time": 2,
                "demo_features": [
                    {
                        "name": "real_time_optimization",
                        "title": "Real-time Optimization",
                        "description": "AI automatically adjusts bids and targeting",
                        "icon": "⚡",
                        "animation": "pulse"
                    },
                    {
                        "name": "performance_insights",
                        "title": "Performance Insights",
                        "description": "Get actionable insights and recommendations",
                        "icon": "📊",
                        "animation": "fade-in"
                    },
                    {
                        "name": "proactive_alerts",
                        "title": "Proactive Alerts",
                        "description": "Get notified before issues occur",
                        "icon": "🔔",
                        "animation": "bounce"
                    },
                    {
                        "name": "creative_optimization",
                        "title": "Creative Optimization",
                        "description": "AI suggests creative improvements",
                        "icon": "🎨",
                        "animation": "rotate"
                    }
                ],
                "visual_elements": {
                    "icon": "✨",
                    "background_gradient": "from-purple-500 to-indigo-600",
                    "animation": "sparkle"
                }
            },
            OnboardingStep.COMPLETION: {
                "title": "You're all set! 🎉",
                "subtitle": "Welcome to the future of marketing",
                "description": "Your OmniFy account is ready. Let's start optimizing your campaigns!",
                "estimated_time": 1,
                "next_steps": [
                    "Explore your personalized dashboard",
                    "Connect additional platforms",
                    "Create your first real campaign",
                    "Invite team members",
                    "Schedule a demo with our experts"
                ],
                "achievements": [
                    "First Steps", "Platform Connector", "Brand Builder", "Campaign Creator", "OmniFy Master"
                ],
                "visual_elements": {
                    "icon": "🎉",
                    "background_gradient": "from-green-500 to-emerald-600",
                    "animation": "celebration"
                }
            }
        }

    def _create_role_experiences(self) -> Dict[UserRole, Dict[str, Any]]:
        """Create role-based personalized experiences"""
        return {
            UserRole.CEO: {
                "dashboard_focus": "executive",
                "key_metrics": ["ROI", "Revenue Impact", "Cost Efficiency", "Market Share"],
                "insights_priority": "strategic",
                "communication_style": "concise",
                "demo_emphasis": "business_impact"
            },
            UserRole.CMO: {
                "dashboard_focus": "strategic",
                "key_metrics": ["Brand Awareness", "Campaign Performance", "Team Efficiency", "Market Position"],
                "insights_priority": "tactical",
                "communication_style": "detailed",
                "demo_emphasis": "performance_optimization"
            },
            UserRole.MARKETING_MANAGER: {
                "dashboard_focus": "operational",
                "key_metrics": ["Campaign ROI", "Conversion Rates", "Audience Growth", "Creative Performance"],
                "insights_priority": "actionable",
                "communication_style": "practical",
                "demo_emphasis": "campaign_management"
            },
            UserRole.MARKETING_SPECIALIST: {
                "dashboard_focus": "creative",
                "key_metrics": ["Engagement Rates", "Creative Performance", "Content Reach", "Social Metrics"],
                "insights_priority": "creative",
                "communication_style": "inspirational",
                "demo_emphasis": "creative_tools"
            },
            UserRole.AGENCY_OWNER: {
                "dashboard_focus": "client_management",
                "key_metrics": ["Client Satisfaction", "Revenue per Client", "Campaign Success Rate", "Team Productivity"],
                "insights_priority": "client_focused",
                "communication_style": "professional",
                "demo_emphasis": "multi_client_management"
            },
            UserRole.FREELANCER: {
                "dashboard_focus": "project_focused",
                "key_metrics": ["Project Success", "Client Retention", "Portfolio Growth", "Efficiency Metrics"],
                "insights_priority": "project_specific",
                "communication_style": "personal",
                "demo_emphasis": "project_management"
            }
        }

    def _create_achievements(self) -> Dict[str, Dict[str, Any]]:
        """Create gamification achievements"""
        return {
            "first_steps": {
                "title": "First Steps",
                "description": "Completed the welcome step",
                "icon": "👶",
                "points": 10
            },
            "role_master": {
                "title": "Role Master",
                "description": "Selected your role and personalized experience",
                "icon": "🎭",
                "points": 15
            },
            "company_builder": {
                "title": "Company Builder",
                "description": "Set up your company information",
                "icon": "🏢",
                "points": 20
            },
            "platform_connector": {
                "title": "Platform Connector",
                "description": "Connected your first marketing platform",
                "icon": "🔗",
                "points": 25
            },
            "brand_artist": {
                "title": "Brand Artist",
                "description": "Uploaded brand assets and guidelines",
                "icon": "🎨",
                "points": 20
            },
            "campaign_creator": {
                "title": "Campaign Creator",
                "description": "Created your first campaign",
                "icon": "🚀",
                "points": 30
            },
            "magic_witness": {
                "title": "Magic Witness",
                "description": "Witnessed OmniFy's AI optimization in action",
                "icon": "✨",
                "points": 25
            },
            "omnify_master": {
                "title": "OmniFy Master",
                "description": "Completed the full onboarding experience",
                "icon": "👑",
                "points": 50
            }
        }

    async def start_onboarding(self, user_id: str, organization_id: str) -> Dict[str, Any]:
        """Start the magical onboarding experience"""
        try:
            # Create onboarding progress
            progress = OnboardingProgress(
                user_id=user_id,
                organization_id=organization_id,
                current_step=OnboardingStep.WELCOME,
                progress_percentage=0.0,
                estimated_time_remaining=15  # Total estimated time
            )
            
            self.active_sessions[user_id] = progress
            
            # Get welcome step configuration
            welcome_config = self.step_configs[OnboardingStep.WELCOME]
            
            logger.info(f"Onboarding started for user {user_id}", extra={
                "organization_id": organization_id,
                "current_step": OnboardingStep.WELCOME.value
            })
            
            return {
                "success": True,
                "session_id": user_id,
                "current_step": OnboardingStep.WELCOME.value,
                "step_config": welcome_config,
                "progress": {
                    "percentage": progress.progress_percentage,
                    "estimated_time_remaining": progress.estimated_time_remaining,
                    "achievements": progress.achievements
                }
            }
            
        except Exception as e:
            logger.error(f"Onboarding start failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def complete_step(
        self, 
        user_id: str, 
        step: OnboardingStep, 
        step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete an onboarding step and move to next"""
        try:
            progress = self.active_sessions.get(user_id)
            if not progress:
                return {"success": False, "error": "Onboarding session not found"}
            
            # Validate step completion
            validation_result = await self._validate_step_completion(step, step_data)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Store step data
            progress.step_data[step.value] = step_data
            progress.completed_steps.append(step)
            progress.updated_at = datetime.utcnow()
            
            # Calculate progress
            total_steps = len(OnboardingStep)
            completed_steps = len(progress.completed_steps)
            progress.progress_percentage = (completed_steps / total_steps) * 100
            
            # Update estimated time remaining
            step_config = self.step_configs[step]
            progress.estimated_time_remaining -= step_config.get("estimated_time", 1)
            
            # Check for achievements
            new_achievements = await self._check_achievements(progress)
            progress.achievements.extend(new_achievements)
            
            # Determine next step
            next_step = await self._determine_next_step(progress)
            progress.current_step = next_step
            
            # Get next step configuration
            next_step_config = self.step_configs[next_step]
            
            # Personalize next step based on role
            if step == OnboardingStep.ROLE_SELECTION:
                user_role = UserRole(step_data.get("role"))
                next_step_config = await self._personalize_step_config(next_step_config, user_role)
            
            logger.info(f"Step completed: {step.value} for user {user_id}", extra={
                "next_step": next_step.value,
                "progress_percentage": progress.progress_percentage,
                "new_achievements": new_achievements
            })
            
            return {
                "success": True,
                "current_step": next_step.value,
                "step_config": next_step_config,
                "progress": {
                    "percentage": progress.progress_percentage,
                    "estimated_time_remaining": max(0, progress.estimated_time_remaining),
                    "achievements": progress.achievements,
                    "completed_steps": [s.value for s in progress.completed_steps]
                },
                "achievements_unlocked": new_achievements
            }
            
        except Exception as e:
            logger.error(f"Step completion failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def skip_step(self, user_id: str, step: OnboardingStep) -> Dict[str, Any]:
        """Skip an onboarding step"""
        try:
            progress = self.active_sessions.get(user_id)
            if not progress:
                return {"success": False, "error": "Onboarding session not found"}
            
            # Add to skipped steps
            progress.skipped_steps.append(step)
            progress.updated_at = datetime.utcnow()
            
            # Determine next step
            next_step = await self._determine_next_step(progress)
            progress.current_step = next_step
            
            # Get next step configuration
            next_step_config = self.step_configs[next_step]
            
            logger.info(f"Step skipped: {step.value} for user {user_id}", extra={
                "next_step": next_step.value
            })
            
            return {
                "success": True,
                "current_step": next_step.value,
                "step_config": next_step_config,
                "progress": {
                    "percentage": progress.progress_percentage,
                    "estimated_time_remaining": max(0, progress.estimated_time_remaining),
                    "achievements": progress.achievements,
                    "skipped_steps": [s.value for s in progress.skipped_steps]
                }
            }
            
        except Exception as e:
            logger.error(f"Step skip failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Get current onboarding status"""
        try:
            progress = self.active_sessions.get(user_id)
            if not progress:
                return {"success": False, "error": "Onboarding session not found"}
            
            return {
                "success": True,
                "status": {
                    "current_step": progress.current_step.value,
                    "progress_percentage": progress.progress_percentage,
                    "estimated_time_remaining": max(0, progress.estimated_time_remaining),
                    "achievements": progress.achievements,
                    "completed_steps": [s.value for s in progress.completed_steps],
                    "skipped_steps": [s.value for s in progress.skipped_steps],
                    "created_at": progress.created_at.isoformat(),
                    "updated_at": progress.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def complete_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Complete the onboarding process"""
        try:
            progress = self.active_sessions.get(user_id)
            if not progress:
                return {"success": False, "error": "Onboarding session not found"}
            
            # Mark as completed
            progress.current_step = OnboardingStep.COMPLETION
            progress.progress_percentage = 100.0
            progress.estimated_time_remaining = 0
            progress.updated_at = datetime.utcnow()
            
            # Add completion achievement
            if "omnify_master" not in progress.achievements:
                progress.achievements.append("omnify_master")
            
            # Save to database
            await self._save_onboarding_progress(progress)
            
            # Generate personalized recommendations
            recommendations = await self._generate_personalized_recommendations(progress)
            
            logger.info(f"Onboarding completed for user {user_id}", extra={
                "total_steps_completed": len(progress.completed_steps),
                "total_achievements": len(progress.achievements)
            })
            
            return {
                "success": True,
                "completion": {
                    "achievements": progress.achievements,
                    "total_steps_completed": len(progress.completed_steps),
                    "completion_time": (progress.updated_at - progress.created_at).total_seconds(),
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Onboarding completion failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _validate_step_completion(self, step: OnboardingStep, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate step completion data"""
        try:
            step_config = self.step_configs[step]
            
            if step == OnboardingStep.ROLE_SELECTION:
                if "role" not in step_data:
                    return {"valid": False, "error": "Role selection is required"}
                
                try:
                    UserRole(step_data["role"])
                except ValueError:
                    return {"valid": False, "error": "Invalid role selected"}
            
            elif step == OnboardingStep.COMPANY_INFO:
                required_fields = ["company_name", "industry", "company_size"]
                for field in required_fields:
                    if field not in step_data or not step_data[field]:
                        return {"valid": False, "error": f"{field} is required"}
            
            elif step == OnboardingStep.PLATFORM_CONNECTION:
                if "connected_platforms" not in step_data:
                    return {"valid": False, "error": "At least one platform must be connected"}
                
                if not step_data["connected_platforms"]:
                    return {"valid": False, "error": "At least one platform must be connected"}
            
            elif step == OnboardingStep.BRAND_SETUP:
                if "brand_assets" not in step_data:
                    return {"valid": False, "error": "Brand setup is required"}
            
            elif step == OnboardingStep.FIRST_CAMPAIGN:
                if "campaign_type" not in step_data:
                    return {"valid": False, "error": "Campaign type selection is required"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def _determine_next_step(self, progress: OnboardingProgress) -> OnboardingStep:
        """Determine the next onboarding step"""
        completed_steps = set(progress.completed_steps)
        skipped_steps = set(progress.skipped_steps)
        
        # Define step order
        step_order = [
            OnboardingStep.WELCOME,
            OnboardingStep.ROLE_SELECTION,
            OnboardingStep.COMPANY_INFO,
            OnboardingStep.PLATFORM_CONNECTION,
            OnboardingStep.BRAND_SETUP,
            OnboardingStep.FIRST_CAMPAIGN,
            OnboardingStep.SUCCESS_DEMO,
            OnboardingStep.COMPLETION
        ]
        
        # Find next incomplete step
        for step in step_order:
            if step not in completed_steps and step not in skipped_steps:
                return step
        
        # If all steps are done, return completion
        return OnboardingStep.COMPLETION

    async def _check_achievements(self, progress: OnboardingProgress) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        completed_steps = set(progress.completed_steps)
        
        # Check step-based achievements
        achievement_mapping = {
            OnboardingStep.WELCOME: "first_steps",
            OnboardingStep.ROLE_SELECTION: "role_master",
            OnboardingStep.COMPANY_INFO: "company_builder",
            OnboardingStep.PLATFORM_CONNECTION: "platform_connector",
            OnboardingStep.BRAND_SETUP: "brand_artist",
            OnboardingStep.FIRST_CAMPAIGN: "campaign_creator",
            OnboardingStep.SUCCESS_DEMO: "magic_witness"
        }
        
        for step, achievement in achievement_mapping.items():
            if step in completed_steps and achievement not in progress.achievements:
                new_achievements.append(achievement)
        
        return new_achievements

    async def _personalize_step_config(
        self, 
        step_config: Dict[str, Any], 
        user_role: UserRole
    ) -> Dict[str, Any]:
        """Personalize step configuration based on user role"""
        role_experience = self.role_experiences[user_role]
        
        # Personalize based on role
        if "platforms" in step_config:
            # Prioritize platforms based on role
            platform_priority = {
                UserRole.CEO: ["google_ads", "meta_ads"],  # High-level platforms
                UserRole.CMO: ["google_ads", "meta_ads", "linkedin_ads"],  # Strategic platforms
                UserRole.MARKETING_MANAGER: ["google_ads", "meta_ads", "linkedin_ads", "tiktok_ads"],  # Full platform mix
                UserRole.MARKETING_SPECIALIST: ["meta_ads", "tiktok_ads", "shopify"],  # Creative platforms
                UserRole.AGENCY_OWNER: ["gohighlevel", "google_ads", "meta_ads"],  # Client management focus
                UserRole.FREELANCER: ["meta_ads", "shopify", "gohighlevel"]  # Project-focused platforms
            }
            
            if user_role in platform_priority:
                # Reorder platforms based on role priority
                prioritized_platforms = []
                for platform_name in platform_priority[user_role]:
                    for platform in step_config["platforms"]:
                        if platform["name"] == platform_name:
                            prioritized_platforms.append(platform)
                            break
                
                # Add remaining platforms
                for platform in step_config["platforms"]:
                    if platform not in prioritized_platforms:
                        prioritized_platforms.append(platform)
                
                step_config["platforms"] = prioritized_platforms
        
        return step_config

    async def _generate_personalized_recommendations(self, progress: OnboardingProgress) -> List[str]:
        """Generate personalized recommendations based on onboarding data"""
        recommendations = []
        
        # Get user role from step data
        role_data = progress.step_data.get("role_selection", {})
        user_role = role_data.get("role")
        
        if user_role:
            role_experience = self.role_experiences.get(UserRole(user_role), {})
            
            if role_experience.get("dashboard_focus") == "executive":
                recommendations.extend([
                    "Set up executive dashboard for high-level insights",
                    "Configure ROI tracking and revenue impact metrics",
                    "Schedule weekly performance reviews"
                ])
            elif role_experience.get("dashboard_focus") == "strategic":
                recommendations.extend([
                    "Create strategic campaign overview dashboard",
                    "Set up brand awareness and market position tracking",
                    "Configure team collaboration features"
                ])
            elif role_experience.get("dashboard_focus") == "operational":
                recommendations.extend([
                    "Set up campaign management workflows",
                    "Configure conversion tracking and optimization",
                    "Create performance monitoring alerts"
                ])
        
        # Add platform-specific recommendations
        platform_data = progress.step_data.get("platform_connection", {})
        connected_platforms = platform_data.get("connected_platforms", [])
        
        if "google_ads" in connected_platforms:
            recommendations.append("Optimize Google Ads campaigns with AI-powered bid management")
        
        if "meta_ads" in connected_platforms:
            recommendations.append("Set up Facebook and Instagram creative optimization")
        
        if "linkedin_ads" in connected_platforms:
            recommendations.append("Configure LinkedIn B2B targeting and lead generation")
        
        return recommendations[:5]  # Limit to top 5 recommendations

    async def _save_onboarding_progress(self, progress: OnboardingProgress):
        """Save onboarding progress to database"""
        try:
            await self.db.onboarding_progress.update_one(
                {"user_id": progress.user_id},
                {"$set": progress.__dict__},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save onboarding progress: {str(e)}")

# Global instance
onboarding_wizard = None

def get_onboarding_wizard(db: AsyncIOMotorDatabase) -> MagicalOnboardingWizard:
    """Get or create onboarding wizard instance"""
    global onboarding_wizard
    if onboarding_wizard is None:
        onboarding_wizard = MagicalOnboardingWizard(db)
    return onboarding_wizard
