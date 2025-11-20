"""
VOICE - Marketing Automation Brain Module
Multi-platform campaign coordination, automated optimization
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationAction(str, Enum):
    """Campaign optimization actions"""
    INCREASE_BID = "increase_bid"
    DECREASE_BID = "decrease_bid"
    PAUSE_CAMPAIGN = "pause_campaign"
    RESUME_CAMPAIGN = "resume_campaign"
    REALLOCATE_BUDGET = "reallocate_budget"
    UPDATE_TARGETING = "update_targeting"
    REFRESH_CREATIVE = "refresh_creative"


class VoiceAutomationService:
    """VOICE - Marketing Automation Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.platform_adapters = {}  # Will be injected
    
    async def coordinate_multi_platform_campaign(
        self,
        campaign_config: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Coordinate campaign across multiple platforms"""
        try:
            results = {}
            
            for platform in platforms:
                try:
                    # Get platform adapter
                    adapter = self.platform_adapters.get(platform)
                    if not adapter:
                        results[platform] = {
                            "status": "error",
                            "message": f"Platform adapter not found: {platform}"
                        }
                        continue
                    
                    # Create campaign on platform
                    platform_campaign = await adapter.create_campaign(campaign_config)
                    
                    results[platform] = {
                        "status": "success",
                        "campaign_id": platform_campaign.get("id"),
                        "platform_campaign_id": platform_campaign.get("google_campaign_id") or platform_campaign.get("meta_campaign_id")
                    }
                    
                except Exception as e:
                    logger.error(f"Error creating campaign on {platform}: {e}")
                    results[platform] = {
                        "status": "error",
                        "message": str(e)
                    }
            
            return {
                "coordinated_campaign_id": campaign_config.get("campaign_id"),
                "platforms": results,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error coordinating multi-platform campaign: {e}")
            raise
    
    async def optimize_campaign_budget(
        self,
        campaign_id: str,
        platform: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Automatically optimize campaign budget allocation"""
        try:
            # Get current budget
            campaign = await self.db.campaigns.find_one({"campaign_id": campaign_id})
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            current_budget = campaign.get("budget", {}).get("daily_budget", 0)
            roas = performance_data.get("roas", 0)
            cost_per_conversion = performance_data.get("cost_per_conversion", 0)
            conversions = performance_data.get("conversions", 0)
            
            # Optimization logic
            new_budget = current_budget
            action = None
            reason = ""
            
            if roas > 3.0 and conversions > 10:
                # High performing - increase budget
                new_budget = current_budget * 1.2
                action = OptimizationAction.INCREASE_BID
                reason = f"High ROAS ({roas:.2f}x) and good conversion volume. Increasing budget by 20%."
            elif roas < 1.5 and cost_per_conversion > 100:
                # Underperforming - decrease budget
                new_budget = current_budget * 0.8
                action = OptimizationAction.DECREASE_BID
                reason = f"Low ROAS ({roas:.2f}x) and high cost per conversion. Decreasing budget by 20%."
            elif roas < 1.0:
                # Very poor performance - pause
                action = OptimizationAction.PAUSE_CAMPAIGN
                reason = f"ROAS below 1.0 ({roas:.2f}x). Pausing campaign for review."
            else:
                # Stable performance - no change
                reason = "Campaign performing within acceptable range. No changes needed."
            
            # Apply optimization if action is determined
            optimization_result = {
                "campaign_id": campaign_id,
                "platform": platform,
                "action": action.value if action else "no_action",
                "current_budget": current_budget,
                "recommended_budget": new_budget if action else current_budget,
                "reason": reason,
                "performance_data": performance_data,
                "optimized_at": datetime.utcnow().isoformat()
            }
            
            # Store optimization record
            await self.db.campaign_optimizations.insert_one(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing campaign budget: {e}")
            raise
    
    async def reallocate_budget_across_campaigns(
        self,
        organization_id: str,
        total_budget: float
    ) -> Dict[str, Any]:
        """Reallocate budget across multiple campaigns based on performance"""
        try:
            # Get all active campaigns
            campaigns = await self.db.campaigns.find({
                "organization_id": organization_id,
                "status": "active"
            }).to_list(length=100)
            
            if not campaigns:
                return {"message": "No active campaigns found"}
            
            # Calculate performance scores
            campaign_scores = []
            for campaign in campaigns:
                performance = campaign.get("performance", {})
                roas = performance.get("roas", 0)
                conversions = performance.get("conversions", 0)
                
                # Score = ROAS * log(conversions + 1) to balance ROAS and volume
                import math
                score = roas * math.log(conversions + 1)
                campaign_scores.append({
                    "campaign_id": campaign["campaign_id"],
                    "score": score,
                    "current_budget": campaign.get("budget", {}).get("daily_budget", 0),
                    "roas": roas
                })
            
            # Sort by score
            campaign_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Allocate budget proportionally to scores
            total_score = sum(c["score"] for c in campaign_scores)
            if total_score == 0:
                # Equal allocation if no performance data
                budget_per_campaign = total_budget / len(campaign_scores)
                allocations = [
                    {
                        "campaign_id": c["campaign_id"],
                        "allocated_budget": budget_per_campaign,
                        "percentage": 100 / len(campaign_scores)
                    }
                    for c in campaign_scores
                ]
            else:
                allocations = [
                    {
                        "campaign_id": c["campaign_id"],
                        "allocated_budget": (c["score"] / total_score) * total_budget,
                        "percentage": (c["score"] / total_score) * 100
                    }
                    for c in campaign_scores
                ]
            
            return {
                "total_budget": total_budget,
                "allocations": allocations,
                "reallocated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reallocating budget: {e}")
            raise
    
    async def execute_optimization_actions(
        self,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute optimization actions across platforms"""
        try:
            results = []
            
            for action in optimization_plan.get("actions", []):
                platform = action.get("platform")
                action_type = action.get("action")
                campaign_id = action.get("campaign_id")
                
                adapter = self.platform_adapters.get(platform)
                if not adapter:
                    results.append({
                        "platform": platform,
                        "status": "error",
                        "message": "Adapter not found"
                    })
                    continue
                
                try:
                    if action_type == OptimizationAction.INCREASE_BID.value:
                        # Increase bid logic
                        result = await adapter.update_campaign_bids(
                            campaign_id,
                            {"bid_multiplier": 1.2}
                        )
                    elif action_type == OptimizationAction.DECREASE_BID.value:
                        # Decrease bid logic
                        result = await adapter.update_campaign_bids(
                            campaign_id,
                            {"bid_multiplier": 0.8}
                        )
                    elif action_type == OptimizationAction.PAUSE_CAMPAIGN.value:
                        result = await adapter.pause_campaign(campaign_id)
                    elif action_type == OptimizationAction.RESUME_CAMPAIGN.value:
                        result = await adapter.resume_campaign(campaign_id)
                    else:
                        result = {"status": "skipped", "reason": "Action not implemented"}
                    
                    results.append({
                        "platform": platform,
                        "campaign_id": campaign_id,
                        "action": action_type,
                        "status": "success",
                        "result": result
                    })
                    
                except Exception as e:
                    logger.error(f"Error executing action {action_type} on {platform}: {e}")
                    results.append({
                        "platform": platform,
                        "campaign_id": campaign_id,
                        "action": action_type,
                        "status": "error",
                        "message": str(e)
                    })
            
            return {
                "execution_id": str(datetime.utcnow().timestamp()),
                "results": results,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing optimization actions: {e}")
            raise

