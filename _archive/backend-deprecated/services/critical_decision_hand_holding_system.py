"""
Critical Decision Hand-Holding System
Implements comprehensive guidance and hand-holding for critical decisions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Types of critical decisions"""
    BUDGET_ALLOCATION = "budget_allocation"
    CAMPAIGN_LAUNCH = "campaign_launch"
    CREATIVE_CHANGE = "creative_change"
    PLATFORM_EXPANSION = "platform_expansion"
    AUDIENCE_TARGETING = "audience_targeting"
    PRICING_STRATEGY = "pricing_strategy"
    PARTNERSHIP_DECISION = "partnership_decision"
    TECHNOLOGY_INVESTMENT = "technology_investment"
    TEAM_SCALING = "team_scaling"
    CRISIS_MANAGEMENT = "crisis_management"

class DecisionImpact(Enum):
    """Impact levels of decisions"""
    LOW = "low"  # Minimal impact
    MEDIUM = "medium"  # Moderate impact
    HIGH = "high"  # Significant impact
    CRITICAL = "critical"  # Critical impact
    TRANSFORMATIONAL = "transformational"  # Business-transforming impact

class GuidanceLevel(Enum):
    """Levels of guidance provided"""
    BASIC = "basic"  # Basic information and tips
    DETAILED = "detailed"  # Comprehensive guidance with examples
    INTERACTIVE = "interactive"  # Step-by-step interactive guidance
    EXPERT_LED = "expert_led"  # Expert-guided decision making
    HAND_HOLDING = "hand_holding"  # Full hand-holding with expert support

class DecisionStage(Enum):
    """Stages of decision making process"""
    ANALYSIS = "analysis"  # Analyzing the situation
    OPTIONS = "options"  # Exploring options
    EVALUATION = "evaluation"  # Evaluating alternatives
    DECISION = "decision"  # Making the decision
    IMPLEMENTATION = "implementation"  # Implementing the decision
    MONITORING = "monitoring"  # Monitoring results

@dataclass
class DecisionContext:
    """Context for critical decision"""
    decision_id: str
    client_id: str
    decision_type: DecisionType
    impact_level: DecisionImpact
    guidance_level: GuidanceLevel
    current_stage: DecisionStage
    title: str
    description: str
    context_data: Dict[str, Any]
    stakeholders: List[str]
    timeline: Optional[datetime]
    budget_impact: Optional[float]
    risk_level: str
    success_criteria: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class GuidanceStep:
    """Step in decision guidance process"""
    step_id: str
    decision_id: str
    stage: DecisionStage
    title: str
    description: str
    instructions: List[str]
    questions: List[str]
    examples: List[Dict[str, Any]]
    resources: List[str]
    checklist: List[str]
    is_completed: bool
    completion_criteria: List[str]
    expert_tips: List[str]
    common_pitfalls: List[str]

@dataclass
class DecisionRecommendation:
    """Recommendation for critical decision"""
    recommendation_id: str
    decision_id: str
    option_name: str
    description: str
    pros: List[str]
    cons: List[str]
    risk_assessment: str
    success_probability: float
    expected_outcome: str
    implementation_steps: List[str]
    resource_requirements: Dict[str, Any]
    timeline_estimate: str
    cost_estimate: Optional[float]
    confidence_score: float

@dataclass
class ExpertGuidance:
    """Expert guidance for critical decision"""
    guidance_id: str
    decision_id: str
    expert_id: str
    guidance_type: str
    content: str
    recommendations: List[str]
    warnings: List[str]
    best_practices: List[str]
    case_studies: List[Dict[str, Any]]
    created_at: datetime

class CriticalDecisionHandHoldingSystem:
    """Core system for critical decision hand-holding"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_decisions: Dict[str, DecisionContext] = {}
        self.guidance_steps: Dict[str, List[GuidanceStep]] = {}
        self.decision_recommendations: Dict[str, List[DecisionRecommendation]] = {}
        self.expert_guidance: Dict[str, List[ExpertGuidance]] = {}
        
        # Decision templates
        self.decision_templates = {}
        self.guidance_templates = {}
        
        # Configuration
        self.default_guidance_level = GuidanceLevel.DETAILED
        self.max_guidance_steps = 10
        self.expert_threshold_impact = DecisionImpact.HIGH
        
        # Initialize templates
        self._initialize_decision_templates()
        self._initialize_guidance_templates()

    async def initialize_system(self):
        """Initialize the critical decision hand-holding system"""
        try:
            # Load existing decisions
            await self._load_active_decisions()
            
            # Load guidance steps
            await self._load_guidance_steps()
            
            logger.info("✅ Critical Decision Hand-Holding System initialized", extra={
                "active_decisions": len(self.active_decisions),
                "decision_templates": len(self.decision_templates),
                "guidance_templates": len(self.guidance_templates)
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Critical Decision Hand-Holding System: {e}")
            raise

    def _initialize_decision_templates(self):
        """Initialize decision templates for different decision types"""
        self.decision_templates = {
            DecisionType.BUDGET_ALLOCATION: {
                "title": "Budget Allocation Decision",
                "description": "Deciding how to allocate marketing budget across channels",
                "stages": [
                    DecisionStage.ANALYSIS,
                    DecisionStage.OPTIONS,
                    DecisionStage.EVALUATION,
                    DecisionStage.DECISION,
                    DecisionStage.IMPLEMENTATION,
                    DecisionStage.MONITORING
                ],
                "success_criteria": [
                    "ROI improvement of at least 20%",
                    "Cost per acquisition reduction",
                    "Revenue growth",
                    "Market share increase"
                ],
                "common_risks": [
                    "Over-investing in underperforming channels",
                    "Under-investing in high-potential channels",
                    "Ignoring seasonal trends",
                    "Not considering competitor actions"
                ]
            },
            DecisionType.CAMPAIGN_LAUNCH: {
                "title": "Campaign Launch Decision",
                "description": "Deciding whether and how to launch a new marketing campaign",
                "stages": [
                    DecisionStage.ANALYSIS,
                    DecisionStage.OPTIONS,
                    DecisionStage.EVALUATION,
                    DecisionStage.DECISION,
                    DecisionStage.IMPLEMENTATION,
                    DecisionStage.MONITORING
                ],
                "success_criteria": [
                    "Achieve target reach and frequency",
                    "Meet conversion rate goals",
                    "Stay within budget constraints",
                    "Generate positive brand sentiment"
                ],
                "common_risks": [
                    "Launching without proper testing",
                    "Insufficient budget allocation",
                    "Poor timing",
                    "Inadequate creative assets"
                ]
            },
            DecisionType.CREATIVE_CHANGE: {
                "title": "Creative Change Decision",
                "description": "Deciding when and how to refresh creative assets",
                "stages": [
                    DecisionStage.ANALYSIS,
                    DecisionStage.OPTIONS,
                    DecisionStage.EVALUATION,
                    DecisionStage.DECISION,
                    DecisionStage.IMPLEMENTATION,
                    DecisionStage.MONITORING
                ],
                "success_criteria": [
                    "Improved engagement rates",
                    "Higher conversion rates",
                    "Better brand recall",
                    "Reduced creative fatigue"
                ],
                "common_risks": [
                    "Changing too frequently",
                    "Not testing new creatives",
                    "Losing brand consistency",
                    "Ignoring audience feedback"
                ]
            }
        }

    def _initialize_guidance_templates(self):
        """Initialize guidance templates for different stages"""
        self.guidance_templates = {
            DecisionStage.ANALYSIS: {
                "title": "Situation Analysis",
                "description": "Analyze the current situation and identify key factors",
                "instructions": [
                    "Gather relevant data and metrics",
                    "Identify key stakeholders and their interests",
                    "Analyze market conditions and trends",
                    "Assess current performance and gaps",
                    "Define the problem clearly"
                ],
                "questions": [
                    "What is the current performance baseline?",
                    "What are the key market trends affecting this decision?",
                    "Who are the main stakeholders and what are their priorities?",
                    "What are the main constraints and limitations?",
                    "What success looks like for this decision?"
                ],
                "checklist": [
                    "Data collection completed",
                    "Stakeholder analysis done",
                    "Market analysis completed",
                    "Problem statement defined",
                    "Success criteria established"
                ]
            },
            DecisionStage.OPTIONS: {
                "title": "Option Generation",
                "description": "Generate and explore different options for the decision",
                "instructions": [
                    "Brainstorm multiple options",
                    "Consider both conventional and innovative approaches",
                    "Evaluate feasibility of each option",
                    "Consider short-term and long-term implications",
                    "Get input from relevant stakeholders"
                ],
                "questions": [
                    "What are all possible options available?",
                    "Which options align with our strategic goals?",
                    "What are the resource requirements for each option?",
                    "How does each option address our constraints?",
                    "What are the potential outcomes of each option?"
                ],
                "checklist": [
                    "Multiple options generated",
                    "Options evaluated for feasibility",
                    "Stakeholder input gathered",
                    "Resource requirements assessed",
                    "Outcomes projected"
                ]
            },
            DecisionStage.EVALUATION: {
                "title": "Option Evaluation",
                "description": "Evaluate and compare different options",
                "instructions": [
                    "Develop evaluation criteria",
                    "Score each option against criteria",
                    "Consider risks and uncertainties",
                    "Analyze trade-offs between options",
                    "Get expert opinions if needed"
                ],
                "questions": [
                    "What criteria should we use to evaluate options?",
                    "How does each option score against our criteria?",
                  "What are the main risks associated with each option?",
                    "What are the key trade-offs we need to consider?",
                    "Do we need expert input for this evaluation?"
                ],
                "checklist": [
                    "Evaluation criteria defined",
                    "Options scored against criteria",
                    "Risk analysis completed",
                    "Trade-offs analyzed",
                    "Expert input obtained if needed"
                ]
            },
            DecisionStage.DECISION: {
                "title": "Decision Making",
                "description": "Make the final decision based on analysis",
                "instructions": [
                    "Review all analysis and evaluation",
                    "Consider intuition and gut feeling",
                    "Make the decision with confidence",
                    "Document the decision and reasoning",
                    "Communicate the decision to stakeholders"
                ],
                "questions": [
                    "Based on all analysis, which option is best?",
                    "What is our confidence level in this decision?",
                    "How will we communicate this decision?",
                    "What are the next steps after this decision?",
                    "How will we monitor the results?"
                ],
                "checklist": [
                    "Decision made and documented",
                    "Reasoning clearly articulated",
                    "Stakeholders informed",
                    "Implementation plan created",
                    "Monitoring plan established"
                ]
            }
        }

    async def _load_active_decisions(self):
        """Load active decisions from database"""
        try:
            decisions_collection = self.db.critical_decisions
            async for decision_doc in decisions_collection.find():
                decision = DecisionContext(
                    decision_id=decision_doc['decision_id'],
                    client_id=decision_doc['client_id'],
                    decision_type=DecisionType(decision_doc['decision_type']),
                    impact_level=DecisionImpact(decision_doc['impact_level']),
                    guidance_level=GuidanceLevel(decision_doc['guidance_level']),
                    current_stage=DecisionStage(decision_doc['current_stage']),
                    title=decision_doc['title'],
                    description=decision_doc['description'],
                    context_data=decision_doc['context_data'],
                    stakeholders=decision_doc['stakeholders'],
                    timeline=decision_doc.get('timeline'),
                    budget_impact=decision_doc.get('budget_impact'),
                    risk_level=decision_doc['risk_level'],
                    success_criteria=decision_doc['success_criteria'],
                    created_at=decision_doc['created_at'],
                    updated_at=decision_doc['updated_at']
                )
                self.active_decisions[decision.decision_id] = decision
                
        except Exception as e:
            logger.error(f"Error loading active decisions: {e}")

    async def _load_guidance_steps(self):
        """Load guidance steps from database"""
        try:
            steps_collection = self.db.guidance_steps
            async for step_doc in steps_collection.find():
                step = GuidanceStep(
                    step_id=step_doc['step_id'],
                    decision_id=step_doc['decision_id'],
                    stage=DecisionStage(step_doc['stage']),
                    title=step_doc['title'],
                    description=step_doc['description'],
                    instructions=step_doc['instructions'],
                    questions=step_doc['questions'],
                    examples=step_doc['examples'],
                    resources=step_doc['resources'],
                    checklist=step_doc['checklist'],
                    is_completed=step_doc['is_completed'],
                    completion_criteria=step_doc['completion_criteria'],
                    expert_tips=step_doc['expert_tips'],
                    common_pitfalls=step_doc['common_pitfalls']
                )
                
                if step.decision_id not in self.guidance_steps:
                    self.guidance_steps[step.decision_id] = []
                self.guidance_steps[step.decision_id].append(step)
                
        except Exception as e:
            logger.error(f"Error loading guidance steps: {e}")

    async def start_decision_guidance(self, client_id: str, decision_type: DecisionType,
                                    title: str, description: str, context_data: Dict[str, Any],
                                    impact_level: DecisionImpact = DecisionImpact.MEDIUM,
                                    guidance_level: Optional[GuidanceLevel] = None,
                                    stakeholders: Optional[List[str]] = None,
                                    timeline: Optional[datetime] = None,
                                    budget_impact: Optional[float] = None) -> str:
        """Start critical decision guidance process"""
        try:
            decision_id = str(uuid.uuid4())
            
            # Determine guidance level if not specified
            if not guidance_level:
                if impact_level in [DecisionImpact.CRITICAL, DecisionImpact.TRANSFORMATIONAL]:
                    guidance_level = GuidanceLevel.EXPERT_LED
                elif impact_level == DecisionImpact.HIGH:
                    guidance_level = GuidanceLevel.INTERACTIVE
                else:
                    guidance_level = self.default_guidance_level
            
            # Get decision template
            template = self.decision_templates.get(decision_type, {})
            
            # Create decision context
            decision = DecisionContext(
                decision_id=decision_id,
                client_id=client_id,
                decision_type=decision_type,
                impact_level=impact_level,
                guidance_level=guidance_level,
                current_stage=DecisionStage.ANALYSIS,
                title=title,
                description=description,
                context_data=context_data,
                stakeholders=stakeholders or [],
                timeline=timeline,
                budget_impact=budget_impact,
                risk_level=self._assess_risk_level(impact_level, context_data),
                success_criteria=template.get('success_criteria', []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Generate guidance steps
            await self._generate_guidance_steps(decision)
            
            # Generate initial recommendations
            await self._generate_initial_recommendations(decision)
            
            # Save decision
            await self._save_decision_context(decision)
            self.active_decisions[decision_id] = decision
            
            logger.info(f"Started decision guidance for {decision_id}", extra={
                "client_id": client_id,
                "decision_type": decision_type.value,
                "impact_level": impact_level.value,
                "guidance_level": guidance_level.value
            })
            
            return decision_id
            
        except Exception as e:
            logger.error(f"Error starting decision guidance: {e}")
            raise

    async def _generate_guidance_steps(self, decision: DecisionContext):
        """Generate guidance steps for decision"""
        try:
            steps = []
            template = self.decision_templates.get(decision.decision_type, {})
            stages = template.get('stages', [DecisionStage.ANALYSIS, DecisionStage.OPTIONS, DecisionStage.EVALUATION, DecisionStage.DECISION])
            
            for i, stage in enumerate(stages):
                step_template = self.guidance_templates.get(stage, {})
                
                step = GuidanceStep(
                    step_id=str(uuid.uuid4()),
                    decision_id=decision.decision_id,
                    stage=stage,
                    title=step_template.get('title', f"Step {i+1}: {stage.value.title()}"),
                    description=step_template.get('description', f"Complete {stage.value} stage"),
                    instructions=step_template.get('instructions', []),
                    questions=step_template.get('questions', []),
                    examples=self._generate_examples(decision.decision_type, stage),
                    resources=self._generate_resources(decision.decision_type, stage),
                    checklist=step_template.get('checklist', []),
                    is_completed=False,
                    completion_criteria=self._generate_completion_criteria(stage),
                    expert_tips=self._generate_expert_tips(decision.decision_type, stage),
                    common_pitfalls=template.get('common_risks', [])
                )
                
                steps.append(step)
            
            # Save steps
            for step in steps:
                await self._save_guidance_step(step)
            
            self.guidance_steps[decision.decision_id] = steps
            
        except Exception as e:
            logger.error(f"Error generating guidance steps: {e}")

    async def _generate_initial_recommendations(self, decision: DecisionContext):
        """Generate initial recommendations for decision"""
        try:
            recommendations = []
            
            # Generate recommendations based on decision type and context
            if decision.decision_type == DecisionType.BUDGET_ALLOCATION:
                recommendations = await self._generate_budget_recommendations(decision)
            elif decision.decision_type == DecisionType.CAMPAIGN_LAUNCH:
                recommendations = await self._generate_campaign_recommendations(decision)
            elif decision.decision_type == DecisionType.CREATIVE_CHANGE:
                recommendations = await self._generate_creative_recommendations(decision)
            else:
                recommendations = await self._generate_generic_recommendations(decision)
            
            # Save recommendations
            for recommendation in recommendations:
                await self._save_decision_recommendation(recommendation)
            
            self.decision_recommendations[decision.decision_id] = recommendations
            
        except Exception as e:
            logger.error(f"Error generating initial recommendations: {e}")

    async def _generate_budget_recommendations(self, decision: DecisionContext) -> List[DecisionRecommendation]:
        """Generate budget allocation recommendations"""
        return [
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Conservative Reallocation",
                description="Gradually shift 20% of budget from underperforming to high-performing channels",
                pros=["Low risk", "Measurable impact", "Easy to reverse"],
                cons=["Slower results", "May miss opportunities"],
                risk_assessment="Low risk with moderate upside potential",
                success_probability=0.75,
                expected_outcome="15-25% improvement in ROAS within 3 months",
                implementation_steps=[
                    "Identify top and bottom performing channels",
                    "Allocate 20% budget shift",
                    "Monitor performance weekly",
                    "Adjust based on results"
                ],
                resource_requirements={"time": "2 weeks", "team": "Marketing team"},
                timeline_estimate="3 months",
                cost_estimate=decision.budget_impact * 0.2 if decision.budget_impact else None,
                confidence_score=0.8
            ),
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Aggressive Reallocation",
                description="Shift 50% of budget to highest-performing channels immediately",
                pros=["Fast results", "Maximum impact", "Clear winners"],
                cons=["High risk", "Hard to reverse", "May over-optimize"],
                risk_assessment="High risk with high upside potential",
                success_probability=0.6,
                expected_outcome="30-50% improvement in ROAS within 1 month",
                implementation_steps=[
                    "Analyze channel performance data",
                    "Identify top 2-3 channels",
                    "Reallocate 50% budget",
                    "Monitor daily for first month"
                ],
                resource_requirements={"time": "1 week", "team": "Marketing team + Analytics"},
                timeline_estimate="1 month",
                cost_estimate=decision.budget_impact * 0.5 if decision.budget_impact else None,
                confidence_score=0.6
            )
        ]

    async def _generate_campaign_recommendations(self, decision: DecisionContext) -> List[DecisionRecommendation]:
        """Generate campaign launch recommendations"""
        return [
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Soft Launch",
                description="Launch campaign with limited budget and audience to test performance",
                pros=["Low risk", "Test and learn", "Easy to optimize"],
                cons=["Limited reach", "Slower growth", "May miss momentum"],
                risk_assessment="Low risk with moderate growth potential",
                success_probability=0.8,
                expected_outcome="Validated campaign ready for scaling within 2 weeks",
                implementation_steps=[
                    "Define test audience segment",
                    "Set limited budget (10-20% of total)",
                    "Launch with basic creative",
                    "Monitor performance closely",
                    "Scale if successful"
                ],
                resource_requirements={"time": "1 week", "team": "Campaign team"},
                timeline_estimate="2 weeks",
                cost_estimate=decision.budget_impact * 0.15 if decision.budget_impact else None,
                confidence_score=0.8
            ),
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Full Launch",
                description="Launch campaign with full budget and broad audience targeting",
                pros=["Maximum reach", "Fast growth", "Strong market presence"],
                cons=["High risk", "Hard to optimize", "High cost"],
                risk_assessment="High risk with high growth potential",
                success_probability=0.5,
                expected_outcome="Strong market presence with potential for high returns",
                implementation_steps=[
                    "Finalize creative assets",
                    "Set up full budget allocation",
                    "Launch across all channels",
                    "Monitor performance daily",
                    "Optimize based on data"
                ],
                resource_requirements={"time": "2 weeks", "team": "Full marketing team"},
                timeline_estimate="1 month",
                cost_estimate=decision.budget_impact if decision.budget_impact else None,
                confidence_score=0.5
            )
        ]

    async def _generate_creative_recommendations(self, decision: DecisionContext) -> List[DecisionRecommendation]:
        """Generate creative change recommendations"""
        return [
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Gradual Refresh",
                description="Introduce new creative elements gradually while maintaining brand consistency",
                pros=["Maintains brand consistency", "Low risk", "Easy to measure"],
                cons=["Slower impact", "May not address all issues"],
                risk_assessment="Low risk with steady improvement",
                success_probability=0.7,
                expected_outcome="Gradual improvement in engagement and conversion rates",
                implementation_steps=[
                    "Audit current creative performance",
                    "Identify underperforming elements",
                    "Create new versions with improvements",
                    "A/B test new vs old creative",
                    "Gradually roll out winners"
                ],
                resource_requirements={"time": "3 weeks", "team": "Creative team"},
                timeline_estimate="6 weeks",
                cost_estimate=decision.budget_impact * 0.3 if decision.budget_impact else None,
                confidence_score=0.7
            ),
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Complete Overhaul",
                description="Replace all creative assets with completely new designs and messaging",
                pros=["Fresh brand image", "High impact potential", "Addresses all issues"],
                cons=["High risk", "Brand consistency risk", "High cost"],
                risk_assessment="High risk with high impact potential",
                success_probability=0.4,
                expected_outcome="Significant improvement in brand perception and performance",
                implementation_steps=[
                    "Conduct comprehensive creative audit",
                    "Develop new creative strategy",
                    "Create all new assets",
                    "Test with focus groups",
                    "Launch across all channels"
                ],
                resource_requirements={"time": "6 weeks", "team": "Full creative team"},
                timeline_estimate="8 weeks",
                cost_estimate=decision.budget_impact if decision.budget_impact else None,
                confidence_score=0.4
            )
        ]

    async def _generate_generic_recommendations(self, decision: DecisionContext) -> List[DecisionRecommendation]:
        """Generate generic recommendations for any decision type"""
        return [
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Conservative Approach",
                description="Take a cautious, well-researched approach to the decision",
                pros=["Low risk", "Well-researched", "Stakeholder buy-in"],
                cons=["May miss opportunities", "Slower implementation"],
                risk_assessment="Low risk with moderate upside",
                success_probability=0.7,
                expected_outcome="Steady progress with manageable risk",
                implementation_steps=[
                    "Conduct thorough research",
                    "Get stakeholder input",
                    "Develop detailed plan",
                    "Implement gradually",
                    "Monitor results"
                ],
                resource_requirements={"time": "4 weeks", "team": "Project team"},
                timeline_estimate="8 weeks",
                cost_estimate=decision.budget_impact * 0.5 if decision.budget_impact else None,
                confidence_score=0.7
            ),
            DecisionRecommendation(
                recommendation_id=str(uuid.uuid4()),
                decision_id=decision.decision_id,
                option_name="Bold Approach",
                description="Take an aggressive, innovative approach to the decision",
                pros=["High impact potential", "Innovative solution", "Fast results"],
                cons=["High risk", "May face resistance", "Higher cost"],
                risk_assessment="High risk with high upside potential",
                success_probability=0.5,
                expected_outcome="Significant impact if successful",
                implementation_steps=[
                    "Identify innovative opportunities",
                    "Develop bold strategy",
                    "Get leadership support",
                    "Implement quickly",
                    "Monitor closely"
                ],
                resource_requirements={"time": "2 weeks", "team": "Core team"},
                timeline_estimate="4 weeks",
                cost_estimate=decision.budget_impact if decision.budget_impact else None,
                confidence_score=0.5
            )
        ]

    def _assess_risk_level(self, impact_level: DecisionImpact, context_data: Dict[str, Any]) -> str:
        """Assess risk level based on impact and context"""
        if impact_level == DecisionImpact.TRANSFORMATIONAL:
            return "very_high"
        elif impact_level == DecisionImpact.CRITICAL:
            return "high"
        elif impact_level == DecisionImpact.HIGH:
            return "medium"
        else:
            return "low"

    def _generate_examples(self, decision_type: DecisionType, stage: DecisionStage) -> List[Dict[str, Any]]:
        """Generate examples for guidance step"""
        examples = []
        
        if decision_type == DecisionType.BUDGET_ALLOCATION and stage == DecisionStage.ANALYSIS:
            examples.append({
                "title": "Channel Performance Analysis",
                "description": "Analyze which channels are performing best",
                "data": {
                    "facebook": {"cpa": 45, "roas": 2.1, "spend": 10000},
                    "google": {"cpa": 38, "roas": 2.8, "spend": 15000},
                    "tiktok": {"cpa": 32, "roas": 3.2, "spend": 5000}
                }
            })
        
        return examples

    def _generate_resources(self, decision_type: DecisionType, stage: DecisionStage) -> List[str]:
        """Generate resources for guidance step"""
        resources = []
        
        if stage == DecisionStage.ANALYSIS:
            resources.extend([
                "Performance data dashboard",
                "Market research reports",
                "Competitor analysis tools",
                "Stakeholder interview templates"
            ])
        elif stage == DecisionStage.OPTIONS:
            resources.extend([
                "Brainstorming templates",
                "Option evaluation matrix",
                "Resource requirement calculator",
                "Timeline planning tools"
            ])
        
        return resources

    def _generate_completion_criteria(self, stage: DecisionStage) -> List[str]:
        """Generate completion criteria for stage"""
        criteria = []
        
        if stage == DecisionStage.ANALYSIS:
            criteria = [
                "All relevant data collected and analyzed",
                "Key stakeholders identified and consulted",
                "Problem statement clearly defined",
                "Success criteria established"
            ]
        elif stage == DecisionStage.OPTIONS:
            criteria = [
                "Multiple viable options generated",
                "Each option evaluated for feasibility",
                "Resource requirements assessed",
                "Stakeholder input incorporated"
            ]
        
        return criteria

    def _generate_expert_tips(self, decision_type: DecisionType, stage: DecisionStage) -> List[str]:
        """Generate expert tips for guidance step"""
        tips = []
        
        if decision_type == DecisionType.BUDGET_ALLOCATION:
            tips.extend([
                "Always test budget changes with small amounts first",
                "Consider seasonal trends when allocating budget",
                "Monitor competitor spending patterns",
                "Keep some budget flexible for opportunities"
            ])
        elif decision_type == DecisionType.CAMPAIGN_LAUNCH:
            tips.extend([
                "Test creative assets before full launch",
                "Start with a soft launch to validate assumptions",
                "Have a clear measurement plan from day one",
                "Prepare for both success and failure scenarios"
            ])
        
        return tips

    async def get_decision_guidance(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive guidance for decision"""
        try:
            if decision_id not in self.active_decisions:
                return None
            
            decision = self.active_decisions[decision_id]
            steps = self.guidance_steps.get(decision_id, [])
            recommendations = self.decision_recommendations.get(decision_id, [])
            
            return {
                "decision": asdict(decision),
                "steps": [asdict(step) for step in steps],
                "recommendations": [asdict(rec) for rec in recommendations],
                "progress": self._calculate_progress(steps),
                "next_steps": self._get_next_steps(decision, steps)
            }
            
        except Exception as e:
            logger.error(f"Error getting decision guidance: {e}")
            return None

    def _calculate_progress(self, steps: List[GuidanceStep]) -> Dict[str, Any]:
        """Calculate progress through guidance steps"""
        if not steps:
            return {"percentage": 0, "completed": 0, "total": 0}
        
        completed = sum(1 for step in steps if step.is_completed)
        total = len(steps)
        percentage = (completed / total) * 100
        
        return {
            "percentage": percentage,
            "completed": completed,
            "total": total
        }

    def _get_next_steps(self, decision: DecisionContext, steps: List[GuidanceStep]) -> List[str]:
        """Get next steps for decision"""
        next_steps = []
        
        # Find current incomplete step
        current_step = None
        for step in steps:
            if not step.is_completed:
                current_step = step
                break
        
        if current_step:
            next_steps.extend(current_step.instructions[:3])  # First 3 instructions
        
        return next_steps

    async def complete_guidance_step(self, decision_id: str, step_id: str) -> bool:
        """Mark guidance step as completed"""
        try:
            if decision_id not in self.guidance_steps:
                return False
            
            steps = self.guidance_steps[decision_id]
            for step in steps:
                if step.step_id == step_id:
                    step.is_completed = True
                    await self._save_guidance_step(step)
                    
                    # Update decision stage if needed
                    await self._update_decision_stage(decision_id)
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error completing guidance step: {e}")
            return False

    async def _update_decision_stage(self, decision_id: str):
        """Update decision stage based on completed steps"""
        try:
            if decision_id not in self.active_decisions:
                return
            
            decision = self.active_decisions[decision_id]
            steps = self.guidance_steps.get(decision_id, [])
            
            # Find next incomplete step
            for step in steps:
                if not step.is_completed:
                    decision.current_stage = step.stage
                    decision.updated_at = datetime.utcnow()
                    await self._save_decision_context(decision)
                    break
            
        except Exception as e:
            logger.error(f"Error updating decision stage: {e}")

    async def _save_decision_context(self, decision: DecisionContext):
        """Save decision context to database"""
        try:
            decisions_collection = self.db.critical_decisions
            await decisions_collection.replace_one(
                {'decision_id': decision.decision_id},
                asdict(decision),
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving decision context: {e}")

    async def _save_guidance_step(self, step: GuidanceStep):
        """Save guidance step to database"""
        try:
            steps_collection = self.db.guidance_steps
            await steps_collection.replace_one(
                {'step_id': step.step_id},
                asdict(step),
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving guidance step: {e}")

    async def _save_decision_recommendation(self, recommendation: DecisionRecommendation):
        """Save decision recommendation to database"""
        try:
            recommendations_collection = self.db.decision_recommendations
            await recommendations_collection.insert_one(asdict(recommendation))
        except Exception as e:
            logger.error(f"Error saving decision recommendation: {e}")

    async def close(self):
        """Close the critical decision hand-holding system"""
        try:
            # Save any pending data
            for decision in self.active_decisions.values():
                await self._save_decision_context(decision)
            
            logger.info("✅ Critical Decision Hand-Holding System closed")
            
        except Exception as e:
            logger.error(f"Error closing Critical Decision Hand-Holding System: {e}")

# Global instance
_critical_decision_system = None

async def get_critical_decision_system(db: AsyncIOMotorDatabase) -> CriticalDecisionHandHoldingSystem:
    """Get or create critical decision hand-holding system instance"""
    global _critical_decision_system
    if _critical_decision_system is None:
        _critical_decision_system = CriticalDecisionHandHoldingSystem(db)
        await _critical_decision_system.initialize_system()
    return _critical_decision_system
