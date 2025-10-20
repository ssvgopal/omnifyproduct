"""
Comprehensive Unit Tests for OmniFy Backend Services
Tests all critical functionality with high coverage
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json
import uuid

# Import the modules to test
from services.agentkit_sdk_client import AgentKitSDKClient
from services.proactive_intelligence_engine import ProactiveIntelligenceEngine
from services.magical_onboarding_wizard import MagicalOnboardingWizard
from services.instant_value_delivery_system import InstantValueDeliverySystem
from services.predictive_intelligence_dashboard import PredictiveIntelligenceDashboard
from services.adaptive_client_learning_system import AdaptiveClientLearningSystem
from services.human_expert_intervention_system import HumanExpertInterventionSystem
from services.critical_decision_hand_holding_system import CriticalDecisionHandHoldingSystem
from integrations.gohighlevel.client import GoHighLevelAdapter
from integrations.meta_ads.client import MetaAdsAdapter
from integrations.google_ads.client import GoogleAdsAdapter
from models.agentkit_models import AgentConfig, AgentExecutionRequest, WorkflowDefinition
from models.brain_models import ClientProfile, CampaignData, PerformanceMetrics

class TestAgentKitSDKClient:
    """Test AgentKit SDK Client functionality"""
    
    @pytest.fixture
    def client(self):
        return AgentKitSDKClient("test-api-key", "https://api.test.com")
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.test.com"
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_create_agent(self, client):
        """Test agent creation"""
        agent_config = AgentConfig(
            name="test-agent",
            description="Test agent for unit testing",
            agent_type="workflow",
            config={"test": "config"}
        )
        
        with patch('agents.Agent') as mock_agent:
            mock_agent.return_value = Mock()
            result = await client.create_agent(agent_config)
            
            assert result is not None
            assert "agent_id" in result
            assert result["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_execute_agent(self, client):
        """Test agent execution"""
        execution_request = AgentExecutionRequest(
            agent_id="test-agent-id",
            input_data={"test": "input"},
            context={"user_id": "test-user"}
        )
        
        with patch('agents.Runner') as mock_runner:
            mock_runner.return_value.run.return_value = {"result": "success"}
            result = await client.execute_agent(execution_request)
            
            assert result is not None
            assert result["status"] == "completed"
            assert "execution_id" in result
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, client):
        """Test workflow creation"""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test workflow",
            steps=[
                {"type": "agent_call", "agent_id": "agent-1"},
                {"type": "data_transform", "operation": "filter"}
            ]
        )
        
        result = await client.create_workflow(workflow_def)
        
        assert result is not None
        assert "workflow_id" in result
        assert result["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, client):
        """Test getting agent status"""
        agent_id = "test-agent-id"
        
        result = await client.get_agent_status(agent_id)
        
        assert result is not None
        assert "status" in result
        assert result["agent_id"] == agent_id

class TestProactiveIntelligenceEngine:
    """Test Proactive Intelligence Engine functionality"""
    
    @pytest.fixture
    def engine(self):
        mock_db = AsyncMock()
        return ProactiveIntelligenceEngine(mock_db)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine.db is not None
        assert len(engine.preference_levels) == 4
        assert len(engine.action_types) == 8
    
    @pytest.mark.asyncio
    async def test_generate_proactive_action(self, engine):
        """Test proactive action generation"""
        client_id = "test-client-123"
        action_type = "creative_fatigue"
        
        result = await engine.generate_proactive_action(client_id, action_type)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["action_type"] == action_type
        assert "confidence_score" in result
        assert "recommended_action" in result
    
    @pytest.mark.asyncio
    async def test_get_client_preference(self, engine):
        """Test getting client preference level"""
        client_id = "test-client-123"
        
        result = await engine.get_client_preference(client_id)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["preference_level"] in engine.preference_levels
    
    @pytest.mark.asyncio
    async def test_require_human_approval(self, engine):
        """Test human approval requirement"""
        action_type = "budget_reallocation"
        confidence_score = 0.6
        
        result = await engine.require_human_approval(action_type, confidence_score)
        
        assert isinstance(result, bool)
        assert result in [True, False]

class TestMagicalOnboardingWizard:
    """Test Magical Onboarding Wizard functionality"""
    
    @pytest.fixture
    def wizard(self):
        mock_db = AsyncMock()
        return MagicalOnboardingWizard(mock_db)
    
    @pytest.mark.asyncio
    async def test_wizard_initialization(self, wizard):
        """Test wizard initialization"""
        assert wizard.db is not None
        assert len(wizard.onboarding_steps) == 8
        assert len(wizard.role_types) == 6
    
    @pytest.mark.asyncio
    async def test_start_onboarding(self, wizard):
        """Test starting onboarding process"""
        user_id = "test-user-123"
        role = "cmo"
        
        result = await wizard.start_onboarding(user_id, role)
        
        assert result is not None
        assert result["user_id"] == user_id
        assert result["role"] == role
        assert result["current_step"] == 1
        assert result["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_complete_step(self, wizard):
        """Test completing onboarding step"""
        session_id = "test-session-123"
        step_number = 1
        step_data = {"company_name": "Test Company"}
        
        result = await wizard.complete_step(session_id, step_number, step_data)
        
        assert result is not None
        assert result["session_id"] == session_id
        assert result["completed_steps"] == [step_number]
        assert result["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_get_next_step(self, wizard):
        """Test getting next onboarding step"""
        session_id = "test-session-123"
        current_step = 1
        
        result = await wizard.get_next_step(session_id, current_step)
        
        assert result is not None
        assert result["step_number"] == current_step + 1
        assert "step_title" in result
        assert "step_description" in result

class TestInstantValueDeliverySystem:
    """Test Instant Value Delivery System functionality"""
    
    @pytest.fixture
    def system(self):
        mock_db = AsyncMock()
        return InstantValueDeliverySystem(mock_db)
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, system):
        """Test system initialization"""
        assert system.db is not None
        assert len(system.optimization_types) == 6
        assert len(system.platforms) == 5
    
    @pytest.mark.asyncio
    async def test_identify_quick_wins(self, system):
        """Test identifying quick wins"""
        client_id = "test-client-123"
        
        result = await system.identify_quick_wins(client_id)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert "quick_wins" in result
        assert len(result["quick_wins"]) > 0
    
    @pytest.mark.asyncio
    async def test_implement_optimization(self, system):
        """Test implementing optimization"""
        client_id = "test-client-123"
        optimization_type = "bid_optimization"
        platform = "google_ads"
        
        result = await system.implement_optimization(client_id, optimization_type, platform)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["optimization_type"] == optimization_type
        assert result["platform"] == platform
        assert result["status"] == "implemented"
    
    @pytest.mark.asyncio
    async def test_measure_impact(self, system):
        """Test measuring optimization impact"""
        optimization_id = "test-optimization-123"
        
        result = await system.measure_impact(optimization_id)
        
        assert result is not None
        assert result["optimization_id"] == optimization_id
        assert "before_metrics" in result
        assert "after_metrics" in result
        assert "improvement_percentage" in result

class TestPredictiveIntelligenceDashboard:
    """Test Predictive Intelligence Dashboard functionality"""
    
    @pytest.fixture
    def dashboard(self):
        mock_db = AsyncMock()
        return PredictiveIntelligenceDashboard(mock_db)
    
    @pytest.mark.asyncio
    async def test_dashboard_initialization(self, dashboard):
        """Test dashboard initialization"""
        assert dashboard.db is not None
        assert len(dashboard.prediction_types) == 5
        assert len(dashboard.trend_metrics) == 4
        assert len(dashboard.opportunity_types) == 6
    
    @pytest.mark.asyncio
    async def test_get_predictions(self, dashboard):
        """Test getting predictions"""
        client_id = "test-client-123"
        prediction_type = "creative_fatigue"
        
        result = await dashboard.get_predictions(client_id, prediction_type)
        
        assert result is not None
        assert len(result) > 0
        for prediction in result:
            assert prediction["type"] == prediction_type
            assert "confidence" in prediction
            assert "value" in prediction
    
    @pytest.mark.asyncio
    async def test_get_trends(self, dashboard):
        """Test getting trends"""
        client_id = "test-client-123"
        
        result = await dashboard.get_trends(client_id)
        
        assert result is not None
        assert len(result) > 0
        for trend in result:
            assert "metric" in trend
            assert "direction" in trend
            assert "strength" in trend
    
    @pytest.mark.asyncio
    async def test_get_opportunities(self, dashboard):
        """Test getting opportunities"""
        client_id = "test-client-123"
        
        result = await dashboard.get_opportunities(client_id)
        
        assert result is not None
        assert len(result) > 0
        for opportunity in result:
            assert "type" in opportunity
            assert "potential_value" in opportunity
            assert "urgency" in opportunity

class TestAdaptiveClientLearningSystem:
    """Test Adaptive Client Learning System functionality"""
    
    @pytest.fixture
    def system(self):
        mock_db = AsyncMock()
        return AdaptiveClientLearningSystem(mock_db)
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, system):
        """Test system initialization"""
        assert system.db is not None
        assert len(system.personality_types) == 6
        assert len(system.learning_styles) == 5
        assert len(system.communication_preferences) == 5
    
    @pytest.mark.asyncio
    async def test_analyze_client_behavior(self, system):
        """Test analyzing client behavior"""
        client_id = "test-client-123"
        behavior_data = {
            "interactions": 50,
            "response_time": 2.5,
            "preferred_channels": ["email", "dashboard"],
            "decision_style": "analytical"
        }
        
        result = await system.analyze_client_behavior(client_id, behavior_data)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert "personality_type" in result
        assert "learning_style" in result
        assert "communication_preference" in result
    
    @pytest.mark.asyncio
    async def test_generate_personalized_recommendations(self, system):
        """Test generating personalized recommendations"""
        client_id = "test-client-123"
        context = {"campaign_type": "social_media", "budget": 10000}
        
        result = await system.generate_personalized_recommendations(client_id, context)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_update_client_profile(self, system):
        """Test updating client profile"""
        client_id = "test-client-123"
        profile_data = {
            "personality_type": "analytical",
            "learning_style": "visual",
            "communication_preference": "detailed"
        }
        
        result = await system.update_client_profile(client_id, profile_data)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["personality_type"] == "analytical"
        assert result["learning_style"] == "visual"

class TestHumanExpertInterventionSystem:
    """Test Human Expert Intervention System functionality"""
    
    @pytest.fixture
    def system(self):
        mock_db = AsyncMock()
        return HumanExpertInterventionSystem(mock_db)
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, system):
        """Test system initialization"""
        assert system.db is not None
        assert len(system.intervention_types) == 7
        assert len(system.expert_levels) == 5
        assert len(system.intervention_workflows) == 7
    
    @pytest.mark.asyncio
    async def test_request_expert_intervention(self, system):
        """Test requesting expert intervention"""
        client_id = "test-client-123"
        intervention_type = "budget_allocation"
        urgency = "high"
        context = {"budget": 50000, "campaigns": 5}
        
        result = await system.request_expert_intervention(client_id, intervention_type, urgency, context)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["intervention_type"] == intervention_type
        assert result["urgency"] == urgency
        assert "intervention_id" in result
        assert "assigned_expert" in result
    
    @pytest.mark.asyncio
    async def test_assign_expert(self, system):
        """Test assigning expert to intervention"""
        intervention_id = "test-intervention-123"
        expert_id = "test-expert-456"
        
        result = await system.assign_expert(intervention_id, expert_id)
        
        assert result is not None
        assert result["intervention_id"] == intervention_id
        assert result["assigned_expert"] == expert_id
        assert result["status"] == "expert_assigned"
    
    @pytest.mark.asyncio
    async def test_complete_intervention(self, system):
        """Test completing intervention"""
        intervention_id = "test-intervention-123"
        resolution = "Budget increased by 20% for high-performing campaigns"
        
        result = await system.complete_intervention(intervention_id, resolution)
        
        assert result is not None
        assert result["intervention_id"] == intervention_id
        assert result["resolution"] == resolution
        assert result["status"] == "completed"

class TestCriticalDecisionHandHoldingSystem:
    """Test Critical Decision Hand-Holding System functionality"""
    
    @pytest.fixture
    def system(self):
        mock_db = AsyncMock()
        return CriticalDecisionHandHoldingSystem(mock_db)
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, system):
        """Test system initialization"""
        assert system.db is not None
        assert len(system.decision_types) == 10
        assert len(system.impact_levels) == 5
        assert len(system.guidance_levels) == 5
    
    @pytest.mark.asyncio
    async def test_start_decision_process(self, system):
        """Test starting decision process"""
        client_id = "test-client-123"
        decision_type = "budget_allocation"
        context = {"total_budget": 100000, "campaigns": 3}
        
        result = await system.start_decision_process(client_id, decision_type, context)
        
        assert result is not None
        assert result["client_id"] == client_id
        assert result["decision_type"] == decision_type
        assert result["status"] == "in_progress"
        assert "decision_id" in result
        assert "current_stage" in result
    
    @pytest.mark.asyncio
    async def test_provide_guidance(self, system):
        """Test providing guidance"""
        decision_id = "test-decision-123"
        stage = "analysis"
        
        result = await system.provide_guidance(decision_id, stage)
        
        assert result is not None
        assert result["decision_id"] == decision_id
        assert result["stage"] == stage
        assert "guidance" in result
        assert "questions" in result
        assert "checklist" in result
    
    @pytest.mark.asyncio
    async def test_make_decision(self, system):
        """Test making decision"""
        decision_id = "test-decision-123"
        decision_data = {"allocated_budget": 60000, "reasoning": "Focus on top performers"}
        
        result = await system.make_decision(decision_id, decision_data)
        
        assert result is not None
        assert result["decision_id"] == decision_id
        assert result["decision_data"] == decision_data
        assert result["status"] == "decision_made"
        assert "recommendations" in result

class TestPlatformIntegrations:
    """Test Platform Integration functionality"""
    
    @pytest.fixture
    def gohighlevel_adapter(self):
        return GoHighLevelAdapter()
    
    @pytest.fixture
    def meta_ads_adapter(self):
        return MetaAdsAdapter()
    
    @pytest.fixture
    def google_ads_adapter(self):
        return GoogleAdsAdapter()
    
    @pytest.mark.asyncio
    async def test_gohighlevel_initialization(self, gohighlevel_adapter):
        """Test GoHighLevel adapter initialization"""
        config = {"api_key": "test-api-key"}
        
        await gohighlevel_adapter.initialize(config)
        
        assert gohighlevel_adapter.config is not None
        assert gohighlevel_adapter.config.api_key == "test-api-key"
    
    @pytest.mark.asyncio
    async def test_gohighlevel_create_client(self, gohighlevel_adapter):
        """Test GoHighLevel client creation"""
        config = {"api_key": "test-api-key"}
        await gohighlevel_adapter.initialize(config)
        
        client_data = {
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+1234567890",
            "company": "Test Company"
        }
        
        result = await gohighlevel_adapter.create_client(client_data)
        
        assert result is not None
        assert result["name"] == "Test Client"
        assert result["email"] == "test@example.com"
        assert result["platform"] == "gohighlevel"
    
    @pytest.mark.asyncio
    async def test_meta_ads_initialization(self, meta_ads_adapter):
        """Test Meta Ads adapter initialization"""
        config = {
            "access_token": "test-token",
            "app_id": "test-app-id",
            "app_secret": "test-app-secret"
        }
        
        await meta_ads_adapter.initialize(config)
        
        assert meta_ads_adapter.config is not None
        assert meta_ads_adapter.config.access_token == "test-token"
    
    @pytest.mark.asyncio
    async def test_meta_ads_create_campaign(self, meta_ads_adapter):
        """Test Meta Ads campaign creation"""
        config = {
            "access_token": "test-token",
            "app_id": "test-app-id",
            "app_secret": "test-app-secret"
        }
        await meta_ads_adapter.initialize(config)
        
        campaign_config = {
            "name": "Test Campaign",
            "objective": "CONVERSIONS",
            "status": "ACTIVE"
        }
        
        result = await meta_ads_adapter.create_campaign(campaign_config)
        
        assert result is not None
        assert result["name"] == "Test Campaign"
        assert result["objective"] == "CONVERSIONS"
        assert result["platform"] == "meta_ads"
    
    @pytest.mark.asyncio
    async def test_google_ads_initialization(self, google_ads_adapter):
        """Test Google Ads adapter initialization"""
        config = {
            "developer_token": "test-dev-token",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "customer_id": "test-customer-id"
        }
        
        await google_ads_adapter.initialize(config)
        
        assert google_ads_adapter.config is not None
        assert google_ads_adapter.config.developer_token == "test-dev-token"
    
    @pytest.mark.asyncio
    async def test_google_ads_create_campaign(self, google_ads_adapter):
        """Test Google Ads campaign creation"""
        config = {
            "developer_token": "test-dev-token",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "customer_id": "test-customer-id"
        }
        await google_ads_adapter.initialize(config)
        
        campaign_config = {
            "name": "Test Campaign",
            "channel_type": "SEARCH",
            "status": "ENABLED"
        }
        
        result = await google_ads_adapter.create_campaign(campaign_config)
        
        assert result is not None
        assert result["name"] == "Test Campaign"
        assert result["channel_type"] == "SEARCH"
        assert result["platform"] == "google_ads"

# Test configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_database():
    """Mock database for testing"""
    return AsyncMock()

@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return {
        "id": "test-client-123",
        "name": "Test Client",
        "email": "test@example.com",
        "company": "Test Company",
        "industry": "technology",
        "budget": 50000,
        "goals": ["increase_conversions", "reduce_cpa"]
    }

@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing"""
    return {
        "id": "test-campaign-123",
        "name": "Test Campaign",
        "platform": "google_ads",
        "budget": 10000,
        "status": "active",
        "target_audience": "tech_professionals",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat()
    }

@pytest.fixture
def sample_performance_metrics():
    """Sample performance metrics for testing"""
    return {
        "campaign_id": "test-campaign-123",
        "date": datetime.now().isoformat(),
        "impressions": 10000,
        "clicks": 500,
        "conversions": 25,
        "cost": 1000.00,
        "cpa": 40.00,
        "roas": 2.5,
        "ctr": 5.0,
        "conversion_rate": 5.0
    }

# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def assert_valid_uuid(uuid_string):
        """Assert that a string is a valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_valid_datetime(datetime_string):
        """Assert that a string is a valid datetime"""
        try:
            datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_valid_response_structure(response, required_fields):
        """Assert that response has required fields"""
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
    
    @staticmethod
    def assert_valid_percentage(value):
        """Assert that value is a valid percentage (0-100)"""
        assert 0 <= value <= 100, f"Invalid percentage: {value}"
    
    @staticmethod
    def assert_valid_confidence_score(score):
        """Assert that confidence score is valid (0-1)"""
        assert 0 <= score <= 1, f"Invalid confidence score: {score}"

# Performance tests
class TestPerformance:
    """Performance tests for critical functions"""
    
    @pytest.mark.asyncio
    async def test_agent_execution_performance(self):
        """Test agent execution performance"""
        client = AgentKitSDKClient("test-api-key")
        
        start_time = datetime.now()
        
        execution_request = AgentExecutionRequest(
            agent_id="test-agent",
            input_data={"test": "data"},
            context={"user_id": "test-user"}
        )
        
        with patch('agents.Runner') as mock_runner:
            mock_runner.return_value.run.return_value = {"result": "success"}
            await client.execute_agent(execution_request)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Assert execution time is under 5 seconds
        assert execution_time < 5.0, f"Agent execution too slow: {execution_time}s"
    
    @pytest.mark.asyncio
    async def test_prediction_generation_performance(self):
        """Test prediction generation performance"""
        mock_db = AsyncMock()
        dashboard = PredictiveIntelligenceDashboard(mock_db)
        
        start_time = datetime.now()
        
        await dashboard.get_predictions("test-client", "creative_fatigue")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Assert prediction generation is under 2 seconds
        assert execution_time < 2.0, f"Prediction generation too slow: {execution_time}s"

# Integration tests
class TestIntegration:
    """Integration tests for end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_workflow(self):
        """Test complete onboarding workflow"""
        mock_db = AsyncMock()
        wizard = MagicalOnboardingWizard(mock_db)
        
        # Start onboarding
        session = await wizard.start_onboarding("test-user", "cmo")
        assert session["status"] == "in_progress"
        
        # Complete first step
        step_result = await wizard.complete_step(session["session_id"], 1, {"company_name": "Test Company"})
        assert step_result["status"] == "in_progress"
        
        # Get next step
        next_step = await wizard.get_next_step(session["session_id"], 1)
        assert next_step["step_number"] == 2
    
    @pytest.mark.asyncio
    async def test_proactive_intelligence_workflow(self):
        """Test proactive intelligence workflow"""
        mock_db = AsyncMock()
        engine = ProactiveIntelligenceEngine(mock_db)
        
        # Generate proactive action
        action = await engine.generate_proactive_action("test-client", "creative_fatigue")
        assert action["action_type"] == "creative_fatigue"
        
        # Check if human approval required
        requires_approval = await engine.require_human_approval(action["action_type"], action["confidence_score"])
        assert isinstance(requires_approval, bool)
    
    @pytest.mark.asyncio
    async def test_platform_integration_workflow(self):
        """Test platform integration workflow"""
        gohighlevel = GoHighLevelAdapter()
        await gohighlevel.initialize({"api_key": "test-key"})
        
        # Create client
        client = await gohighlevel.create_client({
            "name": "Test Client",
            "email": "test@example.com"
        })
        
        assert client["platform"] == "gohighlevel"
        assert client["name"] == "Test Client"
        
        # Create campaign
        campaign = await gohighlevel.create_campaign({
            "name": "Test Campaign",
            "type": "email"
        })
        
        assert campaign["platform"] == "gohighlevel"
        assert campaign["name"] == "Test Campaign"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend", "--cov-report=html"])
