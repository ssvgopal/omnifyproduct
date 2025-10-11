"""
AgentKit Configuration for OmnifyProduct
Defines the 7 core agents for the 4-week revolutionary implementation

AgentKit enables visual development with 70% cost reduction and 8x faster time to market.
This configuration replaces 8 months of custom development with 4 weeks of agent building.
"""

AGENTKIT_AGENTS_CONFIG = {
    "creative_intelligence_agent": {
        "name": "Creative Intelligence Agent",
        "type": "creative_intelligence",
        "description": "AI-powered creative repurposing and analysis agent",
        "capabilities": [
            "creative_asset_analysis",
            "content_repurposing",
            "aida_framework_analysis",
            "brand_compliance_checking",
            "creative_fatigue_detection",
            "performance_prediction",
            "optimization_recommendations"
        ],
        "prompt_template": """
        You are the Creative Intelligence Agent for OmnifyProduct, a campaign intelligence platform.

        Your role is to analyze creative assets, provide repurposing suggestions, and ensure brand compliance.

        Capabilities:
        - Analyze creative assets using AIDA framework (Attention, Interest, Desire, Action)
        - Detect creative fatigue and suggest refresh cycles
        - Provide content repurposing recommendations for different platforms
        - Ensure brand compliance and consistency
        - Predict creative performance based on historical data
        - Generate optimization recommendations

        Always provide structured, actionable insights with confidence scores.
        """,
        "input_schema": {
            "creative_asset": "string (URL, base64, or description)",
            "target_platforms": "array of strings",
            "brand_guidelines": "object (colors, fonts, voice, restrictions)",
            "campaign_context": "object (goals, target_audience, budget)"
        },
        "output_schema": {
            "analysis_score": "number (0-100)",
            "recommendations": "array of strings",
            "repurposing_suggestions": "array of objects",
            "compliance_status": "string (compliant/requires_review/violates)",
            "predicted_performance": "object with ctr, engagement, conversion estimates"
        }
    },

    "marketing_automation_agent": {
        "name": "Marketing Automation Agent",
        "type": "marketing_automation",
        "description": "Campaign management and marketing automation agent",
        "capabilities": [
            "campaign_creation",
            "audience_targeting",
            "bid_optimization",
            "performance_monitoring",
            "budget_management",
            "multi_platform_deployment",
            "gohighlevel_integration"
        ],
        "prompt_template": """
        You are the Marketing Automation Agent for OmnifyProduct, specializing in campaign management and optimization.

        Your role is to create, optimize, and manage marketing campaigns across multiple platforms.

        Capabilities:
        - Create and deploy campaigns on Google Ads, Meta Ads, LinkedIn, etc.
        - Optimize audience targeting based on performance data
        - Manage bids and budgets for optimal ROAS
        - Monitor campaign performance in real-time
        - Provide automated optimization recommendations
        - Integrate with GoHighLevel for CRM automation

        Focus on data-driven decisions and measurable results.
        """,
        "input_schema": {
            "campaign_brief": "object with goals, budget, timeline, target_audience",
            "platforms": "array of strings (google_ads, meta_ads, linkedin, etc.)",
            "current_performance": "object with metrics from existing campaigns",
            "budget_constraints": "object with daily/monthly limits",
            "gohighlevel_config": "object with CRM integration settings"
        },
        "output_schema": {
            "campaign_plan": "object with platform breakdown and strategy",
            "optimization_recommendations": "array of prioritized actions",
            "budget_allocation": "object with platform-specific budgets",
            "performance_predictions": "object with expected metrics",
            "automation_triggers": "array of conditional actions"
        }
    },

    "client_management_agent": {
        "name": "Client Management Agent",
        "type": "client_management",
        "description": "Agency client management and CRM integration agent",
        "capabilities": [
            "client_profile_analysis",
            "engagement_tracking",
            "relationship_management",
            "contract_management",
            "billing_integration",
            "communication_automation",
            "satisfaction_monitoring"
        ],
        "prompt_template": """
        You are the Client Management Agent for OmnifyProduct, focused on agency-client relationships.

        Your role is to analyze client data, predict satisfaction, and optimize agency-client interactions.

        Capabilities:
        - Analyze client profiles and predict success likelihood
        - Track client engagement and satisfaction metrics
        - Automate client communications and reporting
        - Manage contracts and billing relationships
        - Identify upsell and expansion opportunities
        - Monitor client health and retention risk

        Prioritize client satisfaction and long-term relationship value.
        """,
        "input_schema": {
            "client_data": "object with profile, history, current_campaigns",
            "engagement_metrics": "object with interaction data, response times",
            "contract_details": "object with terms, pricing, renewals",
            "communication_history": "array of recent interactions",
            "satisfaction_indicators": "object with NPS, feedback, usage patterns"
        },
        "output_schema": {
            "client_health_score": "number (0-100)",
            "engagement_recommendations": "array of actions",
            "retention_risk": "string (low/medium/high) with confidence score",
            "upsell_opportunities": "array of potential services",
            "communication_plan": "object with suggested interactions"
        }
    },

    "analytics_agent": {
        "name": "Analytics Agent",
        "type": "analytics",
        "description": "Business intelligence and analytics agent",
        "capabilities": [
            "performance_analytics",
            "attribution_modeling",
            "trend_analysis",
            "forecasting",
            "competitive_intelligence",
            "roi_analysis",
            "custom_reporting"
        ],
        "prompt_template": """
        You are the Analytics Agent for OmnifyProduct, providing business intelligence and insights.

        Your role is to analyze campaign data, identify trends, and provide actionable insights.

        Capabilities:
        - Perform multi-platform campaign analytics
        - Build attribution models (first-touch, last-touch, linear, time-decay)
        - Identify performance trends and anomalies
        - Generate forecasts and predictions
        - Provide competitive intelligence insights
        - Calculate ROI and profitability metrics
        - Create custom reports and visualizations

        Focus on actionable insights that drive business decisions.
        """,
        "input_schema": {
            "campaign_data": "array of campaign performance objects",
            "platform_metrics": "object with data from different platforms",
            "time_range": "object with start_date, end_date, granularity",
            "attribution_model": "string (first_touch, last_touch, linear, time_decay)",
            "comparison_baseline": "object with previous period data"
        },
        "output_schema": {
            "key_metrics": "object with roi, revenue, profit, growth rates",
            "performance_insights": "array of prioritized insights",
            "trend_analysis": "object with growth trends and seasonality",
            "forecasts": "object with predictions and confidence intervals",
            "recommendations": "array of data-driven actions",
            "custom_report": "object with charts, tables, and narratives"
        }
    },

    "workflow_orchestration_agent": {
        "name": "Workflow Orchestration Agent",
        "type": "workflow_orchestration",
        "description": "Complex multi-step workflow automation agent",
        "capabilities": [
            "workflow_design",
            "multi_agent_coordination",
            "conditional_logic",
            "error_handling",
            "workflow_optimization",
            "real_time_monitoring",
            "performance_tracking"
        ],
        "prompt_template": """
        You are the Workflow Orchestration Agent for OmnifyProduct, managing complex multi-agent workflows.

        Your role is to coordinate multiple agents, manage workflow logic, and ensure successful execution.

        Capabilities:
        - Design and execute multi-step workflows
        - Coordinate communication between different agents
        - Implement conditional logic and branching
        - Handle errors and provide recovery mechanisms
        - Optimize workflow performance and efficiency
        - Monitor workflow execution in real-time
        - Track and report on workflow success metrics

        Ensure reliable, efficient, and maintainable workflow execution.
        """,
        "input_schema": {
            "workflow_definition": "object with steps, conditions, dependencies",
            "agent_sequence": "array of agent execution steps",
            "input_data": "object with initial workflow data",
            "error_handling": "object with retry logic and failure handling",
            "performance_requirements": "object with timeouts and SLAs"
        },
        "output_schema": {
            "workflow_status": "string (running/completed/failed)",
            "execution_results": "object with results from each step",
            "performance_metrics": "object with execution times and efficiency",
            "error_log": "array of errors and recovery actions",
            "optimization_suggestions": "array of workflow improvements"
        }
    },

    "compliance_agent": {
        "name": "Compliance Agent",
        "type": "compliance",
        "description": "Enterprise compliance and security agent",
        "capabilities": [
            "soc2_compliance",
            "iso27001_compliance",
            "audit_logging",
            "data_retention",
            "security_monitoring",
            "risk_assessment",
            "policy_enforcement"
        ],
        "prompt_template": """
        You are the Compliance Agent for OmnifyProduct, ensuring enterprise-grade security and compliance.

        Your role is to maintain SOC 2 and ISO 27001 compliance while monitoring security and data handling.

        Capabilities:
        - Ensure SOC 2 compliance with comprehensive audit logging
        - Maintain ISO 27001 information security standards
        - Monitor data retention policies (7-year retention for SOC 2)
        - Assess security risks and vulnerabilities
        - Enforce data handling policies and procedures
        - Generate compliance reports and documentation
        - Provide security recommendations and alerts

        Compliance is non-negotiable - always prioritize security and regulatory requirements.
        """,
        "input_schema": {
            "operation_context": "object with user, action, data involved",
            "security_scan": "object with system vulnerabilities and threats",
            "compliance_check": "object with policies to validate against",
            "audit_request": "object with time range and scope for audit"
        },
        "output_schema": {
            "compliance_status": "string (compliant/requires_attention/non_compliant)",
            "security_assessment": "object with risk levels and findings",
            "audit_log": "array of compliance-relevant events",
            "recommendations": "array of security and compliance actions",
            "certification_status": "object with SOC2 and ISO27001 status"
        }
    },

    "performance_agent": {
        "name": "Performance Optimization Agent",
        "type": "performance",
        "description": "System optimization and performance monitoring agent",
        "capabilities": [
            "system_monitoring",
            "bottleneck_detection",
            "resource_optimization",
            "scalability_analysis",
            "performance_forecasting",
            "cost_optimization",
            "infrastructure_recommendations"
        ],
        "prompt_template": """
        You are the Performance Optimization Agent for OmnifyProduct, maximizing system efficiency and scalability.

        Your role is to monitor system performance, identify bottlenecks, and provide optimization recommendations.

        Capabilities:
        - Monitor system resources and application performance
        - Detect performance bottlenecks and inefficiencies
        - Analyze scalability requirements and limitations
        - Forecast performance needs based on growth projections
        - Optimize resource utilization and costs
        - Provide infrastructure scaling recommendations
        - Monitor and alert on performance degradation

        Focus on maintaining optimal performance while controlling costs.
        """,
        "input_schema": {
            "system_metrics": "object with CPU, memory, disk, network usage",
            "application_metrics": "object with response times, error rates, throughput",
            "usage_patterns": "object with peak times, user behavior, load distribution",
            "infrastructure_config": "object with current server, database, cache setup",
            "cost_constraints": "object with budget limits and optimization goals"
        },
        "output_schema": {
            "performance_score": "number (0-100) overall system health",
            "bottlenecks": "array of identified performance issues",
            "optimization_recommendations": "array of prioritized improvements",
            "scalability_plan": "object with growth projections and infrastructure needs",
            "cost_savings": "object with optimization opportunities and savings estimates"
        }
    }
}

# Workflow orchestration templates
AGENTKIT_WORKFLOWS = {
    "campaign_launch_workflow": {
        "name": "Campaign Launch Workflow",
        "description": "End-to-end campaign creation and launch orchestration",
        "sequence": [
            {
                "step_name": "brief_analysis",
                "agent_id": "creative_intelligence_agent",
                "depends_on": [],
                "share_output": True,
                "parameters": {"analysis_type": "campaign_brief"}
            },
            {
                "step_name": "audience_targeting",
                "agent_id": "marketing_automation_agent",
                "depends_on": ["brief_analysis"],
                "share_output": True,
                "parameters": {"task": "audience_optimization"}
            },
            {
                "step_name": "creative_optimization",
                "agent_id": "creative_intelligence_agent",
                "depends_on": ["brief_analysis", "audience_targeting"],
                "share_output": True,
                "parameters": {"task": "creative_optimization"}
            },
            {
                "step_name": "campaign_deployment",
                "agent_id": "marketing_automation_agent",
                "depends_on": ["audience_targeting", "creative_optimization"],
                "share_output": True,
                "parameters": {"task": "campaign_deployment"}
            },
            {
                "step_name": "performance_monitoring",
                "agent_id": "analytics_agent",
                "depends_on": ["campaign_deployment"],
                "share_output": False,
                "parameters": {"task": "initial_monitoring"}
            }
        ]
    },

    "client_onboarding_workflow": {
        "name": "Client Onboarding Workflow",
        "description": "Comprehensive client onboarding and setup process",
        "sequence": [
            {
                "step_name": "client_analysis",
                "agent_id": "client_management_agent",
                "depends_on": [],
                "share_output": True,
                "parameters": {"task": "initial_assessment"}
            },
            {
                "step_name": "brand_setup",
                "agent_id": "creative_intelligence_agent",
                "depends_on": ["client_analysis"],
                "share_output": True,
                "parameters": {"task": "brand_guidelines_setup"}
            },
            {
                "step_name": "platform_integration",
                "agent_id": "marketing_automation_agent",
                "depends_on": ["client_analysis"],
                "share_output": True,
                "parameters": {"task": "platform_setup"}
            },
            {
                "step_name": "compliance_check",
                "agent_id": "compliance_agent",
                "depends_on": ["client_analysis", "brand_setup", "platform_integration"],
                "share_output": True,
                "parameters": {"task": "onboarding_compliance"}
            },
            {
                "step_name": "welcome_package",
                "agent_id": "client_management_agent",
                "depends_on": ["compliance_check"],
                "share_output": False,
                "parameters": {"task": "welcome_communications"}
            }
        ]
    },

    "monthly_reporting_workflow": {
        "name": "Monthly Performance Reporting",
        "description": "Automated monthly performance analysis and reporting",
        "sequence": [
            {
                "step_name": "data_collection",
                "agent_id": "analytics_agent",
                "depends_on": [],
                "share_output": True,
                "parameters": {"task": "monthly_data_aggregation"}
            },
            {
                "step_name": "performance_analysis",
                "agent_id": "analytics_agent",
                "depends_on": ["data_collection"],
                "share_output": True,
                "parameters": {"task": "performance_analysis"}
            },
            {
                "step_name": "client_segmentation",
                "agent_id": "client_management_agent",
                "depends_on": ["performance_analysis"],
                "share_output": True,
                "parameters": {"task": "client_performance_segmentation"}
            },
            {
                "step_name": "report_generation",
                "agent_id": "analytics_agent",
                "depends_on": ["performance_analysis", "client_segmentation"],
                "share_output": True,
                "parameters": {"task": "report_generation"}
            },
            {
                "step_name": "client_communication",
                "agent_id": "client_management_agent",
                "depends_on": ["report_generation"],
                "share_output": False,
                "parameters": {"task": "report_delivery"}
            }
        ]
    }
}

# AgentKit integration settings
AGENTKIT_INTEGRATION_CONFIG = {
    "openai_enterprise": {
        "enabled": True,
        "features": [
            "advanced_reasoning",
            "multi_modal_processing",
            "real_time_responses",
            "enterprise_security"
        ]
    },
    "gohighlevel_integration": {
        "enabled": True,
        "features": [
            "crm_sync",
            "workflow_triggers",
            "contact_management",
            "pipeline_automation"
        ]
    },
    "platform_integrations": {
        "google_ads": {"enabled": False, "status": "planned"},
        "meta_ads": {"enabled": False, "status": "planned"},
        "linkedin_ads": {"enabled": False, "status": "planned"},
        "shopify": {"enabled": False, "status": "planned"},
        "google_analytics": {"enabled": False, "status": "planned"}
    },
    "compliance_features": {
        "soc2_compliance": True,
        "iso27001_compliance": True,
        "audit_logging": True,
        "data_encryption": True,
        "access_controls": True
    }
}
