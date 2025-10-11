"""
AgentKit Service for OmnifyProduct
Manages the 7 core agents and provides unified agent orchestration

This service enables the revolutionary 4-week implementation by replacing
8 months of custom development with visual agent development.
"""

import asyncio
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from platform_adapters.agentkit.adapter import AgentKitAdapter
from config.agentkit.agents import AGENTKIT_AGENTS_CONFIG, AGENTKIT_WORKFLOWS
from services.structured_logging import logger

class AgentKitService:
    """
    Core service for managing AgentKit-powered agents
    Provides the revolutionary 4-week implementation path
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.adapter = AgentKitAdapter(db)
        self.initialized_agents = {}
        self.active_workflows = {}

        logger.info("AgentKit service initialized", extra={
            "event_type": "agentkit_service_init",
            "total_agents_configured": len(AGENTKIT_AGENTS_CONFIG),
            "total_workflows_configured": len(AGENTKIT_WORKFLOWS)
        })

    async def initialize_core_agents(self) -> Dict[str, bool]:
        """
        Initialize all 7 core agents for the revolutionary implementation
        This replaces months of custom development with agent registration
        """
        logger.info("Initializing core AgentKit agents", extra={
            "event_type": "core_agents_initialization_start",
            "agents_to_initialize": list(AGENTKIT_AGENTS_CONFIG.keys())
        })

        results = {}
        for agent_id, agent_config in AGENTKIT_AGENTS_CONFIG.items():
            try:
                success = await self.adapter.register_agent(agent_id, agent_config)
                results[agent_id] = success

                if success:
                    self.initialized_agents[agent_id] = agent_config
                    logger.info("Core agent initialized successfully", extra={
                        "event_type": "agent_initialization_success",
                        "agent_id": agent_id,
                        "agent_type": agent_config["type"],
                        "capabilities": len(agent_config["capabilities"])
                    })
                else:
                    logger.error("Failed to initialize core agent", extra={
                        "event_type": "agent_initialization_failed",
                        "agent_id": agent_id
                    })

            except Exception as e:
                logger.error("Exception during agent initialization", exc_info=e, extra={
                    "event_type": "agent_initialization_exception",
                    "agent_id": agent_id
                })
                results[agent_id] = False

        # Log overall initialization results
        successful_count = sum(1 for success in results.values() if success)
        logger.info("Core agents initialization completed", extra={
            "event_type": "core_agents_initialization_complete",
            "total_agents": len(results),
            "successful_initializations": successful_count,
            "failed_initializations": len(results) - successful_count
        })

        return results

    # ========== INDIVIDUAL AGENT EXECUTION METHODS ==========

    async def execute_creative_agent(
        self,
        creative_asset: str,
        target_platforms: List[str],
        brand_guidelines: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Creative Intelligence Agent
        Provides AI-powered creative analysis and repurposing
        """
        input_data = {
            "creative_asset": creative_asset,
            "target_platforms": target_platforms,
            "brand_guidelines": brand_guidelines or {},
            "campaign_context": campaign_context or {}
        }

        logger.track_feature_usage("agentkit", "creative_agent_execution", {
            "platforms": target_platforms,
            "has_brand_guidelines": bool(brand_guidelines)
        })

        return await self.adapter.execute_agent("creative_intelligence_agent", input_data)

    async def execute_marketing_agent(
        self,
        campaign_brief: Dict[str, Any],
        platforms: List[str],
        current_performance: Optional[Dict[str, Any]] = None,
        budget_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Marketing Automation Agent
        Handles campaign creation and optimization across platforms
        """
        input_data = {
            "campaign_brief": campaign_brief,
            "platforms": platforms,
            "current_performance": current_performance or {},
            "budget_constraints": budget_constraints or {}
        }

        logger.track_feature_usage("agentkit", "marketing_agent_execution", {
            "platforms": platforms,
            "campaign_goals": campaign_brief.get("goals", [])
        })

        return await self.adapter.execute_agent("marketing_automation_agent", input_data)

    async def execute_client_agent(
        self,
        client_data: Dict[str, Any],
        engagement_metrics: Optional[Dict[str, Any]] = None,
        contract_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Client Management Agent
        Analyzes client relationships and provides management insights
        """
        input_data = {
            "client_data": client_data,
            "engagement_metrics": engagement_metrics or {},
            "contract_details": contract_details or {}
        }

        logger.track_feature_usage("agentkit", "client_agent_execution", {
            "client_type": client_data.get("type", "unknown")
        })

        return await self.adapter.execute_agent("client_management_agent", input_data)

    async def execute_analytics_agent(
        self,
        campaign_data: List[Dict[str, Any]],
        platform_metrics: Dict[str, Any],
        time_range: Dict[str, str],
        attribution_model: str = "last_touch"
    ) -> Dict[str, Any]:
        """
        Execute Analytics Agent
        Provides business intelligence and performance insights
        """
        input_data = {
            "campaign_data": campaign_data,
            "platform_metrics": platform_metrics,
            "time_range": time_range,
            "attribution_model": attribution_model
        }

        logger.track_feature_usage("agentkit", "analytics_agent_execution", {
            "campaigns_count": len(campaign_data),
            "attribution_model": attribution_model
        })

        return await self.adapter.execute_agent("analytics_agent", input_data)

    async def execute_workflow_agent(
        self,
        workflow_definition: Dict[str, Any],
        input_data: Dict[str, Any],
        error_handling: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Workflow Orchestration Agent
        Manages complex multi-step workflows
        """
        input_data_full = {
            "workflow_definition": workflow_definition,
            "input_data": input_data,
            "error_handling": error_handling or {"retry_count": 3, "timeout": 300}
        }

        logger.track_feature_usage("agentkit", "workflow_agent_execution", {
            "workflow_steps": len(workflow_definition.get("sequence", []))
        })

        return await self.adapter.execute_agent("workflow_orchestration_agent", input_data_full)

    async def execute_compliance_agent(
        self,
        operation_context: Dict[str, Any],
        security_scan: Optional[Dict[str, Any]] = None,
        audit_request: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Compliance Agent
        Ensures SOC 2 and ISO 27001 compliance
        """
        input_data = {
            "operation_context": operation_context,
            "security_scan": security_scan or {},
            "audit_request": audit_request or {}
        }

        logger.track_feature_usage("agentkit", "compliance_agent_execution", {
            "operation_type": operation_context.get("action", "unknown")
        })

        return await self.adapter.execute_agent("compliance_agent", input_data)

    async def execute_performance_agent(
        self,
        system_metrics: Dict[str, Any],
        application_metrics: Dict[str, Any],
        usage_patterns: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Performance Optimization Agent
        Monitors and optimizes system performance
        """
        input_data = {
            "system_metrics": system_metrics,
            "application_metrics": application_metrics,
            "usage_patterns": usage_patterns or {}
        }

        logger.track_feature_usage("agentkit", "performance_agent_execution", {
            "cpu_usage": system_metrics.get("cpu_percent", 0),
            "memory_usage": system_metrics.get("memory_percent", 0)
        })

        return await self.adapter.execute_agent("performance_agent", input_data)

    # ========== WORKFLOW ORCHESTRATION METHODS ==========

    async def execute_campaign_launch_workflow(
        self,
        campaign_brief: Dict[str, Any],
        creative_assets: List[str],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Execute complete campaign launch workflow
        Orchestrates multiple agents for end-to-end campaign creation
        """
        workflow_config = AGENTKIT_WORKFLOWS["campaign_launch_workflow"]
        input_data = {
            "campaign_brief": campaign_brief,
            "creative_assets": creative_assets,
            "target_platforms": target_platforms
        }

        logger.track_workflow_start("campaign_launch", {
            "platforms": target_platforms,
            "assets_count": len(creative_assets)
        })

        result = await self.adapter.orchestrate_agents(workflow_config, input_data)

        if result["status"] == "completed":
            logger.track_workflow_complete("campaign_launch", {
                "execution_id": result["workflow_id"]
            })
        else:
            logger.track_workflow_error("campaign_launch", result.get("error", "Unknown error"))

        return result

    async def execute_client_onboarding_workflow(
        self,
        client_profile: Dict[str, Any],
        brand_assets: List[str],
        platform_preferences: List[str]
    ) -> Dict[str, Any]:
        """
        Execute client onboarding workflow
        Complete setup process for new agency clients
        """
        workflow_config = AGENTKIT_WORKFLOWS["client_onboarding_workflow"]
        input_data = {
            "client_profile": client_profile,
            "brand_assets": brand_assets,
            "platform_preferences": platform_preferences
        }

        logger.track_workflow_start("client_onboarding", {
            "client_type": client_profile.get("type", "unknown"),
            "platforms": platform_preferences
        })

        result = await self.adapter.orchestrate_agents(workflow_config, input_data)

        if result["status"] == "completed":
            logger.track_workflow_complete("client_onboarding", {
                "execution_id": result["workflow_id"],
                "client_id": client_profile.get("id")
            })
        else:
            logger.track_workflow_error("client_onboarding", result.get("error", "Unknown error"))

        return result

    async def execute_monthly_reporting_workflow(
        self,
        client_id: str,
        reporting_period: Dict[str, str],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute monthly performance reporting workflow
        Automated monthly reporting and client communications
        """
        workflow_config = AGENTKIT_WORKFLOWS["monthly_reporting_workflow"]
        input_data = {
            "client_id": client_id,
            "reporting_period": reporting_period,
            "performance_data": performance_data
        }

        logger.track_workflow_start("monthly_reporting", {
            "client_id": client_id,
            "period": reporting_period
        })

        result = await self.adapter.orchestrate_agents(workflow_config, input_data)

        if result["status"] == "completed":
            logger.track_workflow_complete("monthly_reporting", {
                "execution_id": result["workflow_id"],
                "client_id": client_id
            })
        else:
            logger.track_workflow_error("monthly_reporting", result.get("error", "Unknown error"))

        return result

    # ========== MONITORING AND MANAGEMENT METHODS ==========

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific agent"""
        return await self.adapter.get_agent_status(agent_id)

    async def get_all_agent_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all registered agents"""
        return await self.adapter.list_agents()

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running workflow"""
        return self.active_workflows.get(workflow_id)

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall AgentKit system health
        Calls the performance agent for system monitoring
        """
        try:
            # Get basic system metrics (would be collected from actual monitoring)
            system_metrics = {
                "cpu_percent": 45.2,
                "memory_percent": 62.8,
                "disk_usage": 34.1,
                "network_connections": 150
            }

            application_metrics = {
                "active_users": 25,
                "requests_per_minute": 120,
                "error_rate": 0.02,
                "avg_response_time": 245
            }

            # Execute performance agent for health assessment
            health_result = await self.execute_performance_agent(
                system_metrics, application_metrics
            )

            return {
                "overall_status": "healthy" if health_result["status"] == "completed" else "degraded",
                "agents_registered": len(self.initialized_agents),
                "active_workflows": len(self.active_workflows),
                "performance_score": health_result.get("result", {}).get("performance_score", 0),
                "last_health_check": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error("Failed to get system health", exc_info=e)
            return {
                "overall_status": "error",
                "error": str(e),
                "agents_registered": len(self.initialized_agents),
                "active_workflows": len(self.active_workflows)
            }

    async def get_agent_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics for all agents"""
        agents = await self.adapter.list_agents()

        total_executions = sum(agent.get("execution_count", 0) for agent in agents)
        avg_success_rate = sum(agent.get("success_rate", 0) for agent in agents) / len(agents) if agents else 0

        return {
            "total_agents": len(agents),
            "total_executions": total_executions,
            "average_success_rate": round(avg_success_rate, 3),
            "active_workflows": len(self.active_workflows),
            "agent_breakdown": [
                {
                    "name": agent["name"],
                    "type": agent["type"],
                    "executions": agent.get("execution_count", 0),
                    "success_rate": agent.get("success_rate", 0.0)
                }
                for agent in agents
            ]
        }

    # ========== UTILITY METHODS ==========

    def is_agent_available(self, agent_id: str) -> bool:
        """Check if an agent is available and initialized"""
        return agent_id in self.initialized_agents

    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow templates"""
        return list(AGENTKIT_WORKFLOWS.keys())

    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities of a specific agent"""
        agent_config = self.initialized_agents.get(agent_id)
        return agent_config.get("capabilities", []) if agent_config else []
