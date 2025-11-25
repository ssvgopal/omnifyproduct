export interface BrainModule<TInput, TOutput> {
  name: string;
  process(input: TInput): Promise<TOutput>;
}

export interface ChannelData {
  id: string;
  name: string;
  platform: 'Meta' | 'Google' | 'TikTok' | 'Shopify'; // MVP platforms only
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  cpa: number;
  ctr: number;
}

export interface CreativeData {
  id: string;
  name: string;
  channelId: string;
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  ctr: number;
  roas: number;
  status: 'active' | 'paused';
  launchDate: string;
}

export interface DailyMetric {
  date: string;
  channelId: string;
  spend: number;
  revenue: number;
  roas: number;
  status: 'winner' | 'loser' | 'neutral';
}

export interface MemoryOutput {
  totalSpend: number;
  totalRevenue: number;
  blendedRoas: number;
  channels: {
    id: string;
    name: string;
    roas: number;
    status: 'winner' | 'loser' | 'neutral';
    contribution: number; // % of total revenue
  }[];
  ltvRoas: number; // Simulated LTV multiplier
}

export interface RiskFactor {
  id: string;
  type: 'creative_fatigue' | 'roi_decay' | 'ltv_drift' | 'budget_inefficiency';
  severity: 'high' | 'medium' | 'low';
  message: string;
  entityId?: string; // e.g., Creative ID or Channel ID
  predictionDays?: number; // e.g., "in 3 days"
}

export interface OracleOutput {
  globalRiskScore: number; // 0-100 (Higher is safer? Or Higher is riskier? Let's say 0-100 Risk Score, so 100 is Critical)
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  risks: RiskFactor[];
}

export interface ActionRecommendation {
  id: string;
  type: 'shift_budget' | 'pause_creative' | 'increase_budget' | 'launch_campaign';
  title: string;
  description: string;
  impact: string; // e.g., "+$1,200/day"
  confidence: 'high' | 'medium' | 'low';
  urgency: 'high' | 'medium' | 'low';
  entities: string[]; // IDs involved
}

export interface CuriosityOutput {
  topActions: ActionRecommendation[];
  totalOpportunity: string; // e.g., "+$4,500/week"
}

export interface BrainState {
  timestamp: string;
  memory: MemoryOutput;
  oracle: OracleOutput;
  curiosity: CuriosityOutput;
}

// ============================================
// NEW TYPES (Requirements V3 Alignment)
// ============================================

// Campaign data (per B.3.2.1)
export interface CampaignData {
  id: string;
  channelId: string;
  campaignId: string; // External platform ID
  campaignName: string;
  campaignType: 'prospecting' | 'retargeting' | 'brand' | 'conversion';
  status: 'active' | 'paused' | 'archived';
  dailyBudget?: number;
  lifetimeBudget?: number;
  startDate?: string;
  endDate?: string;
}

// Cohort data for LTV tracking (per B.4.2.3)
export interface CohortData {
  id: string;
  cohortMonth: string; // 'YYYY-MM'
  acquisitionChannel: 'Meta' | 'Google' | 'TikTok' | 'Organic' | 'All';
  customerCount: number;
  totalRevenue: number;
  ltv30d: number;
  ltv60d: number;
  ltv90d: number;
  ltv180d?: number;
  avgOrderValue: number;
  repeatPurchaseRate: number;
}

// Extended daily metric with new fields (per C.1.4)
export interface DailyMetricExtended extends DailyMetric {
  creativeId?: string;
  campaignId?: string;
  frequency: number;
  cvr: number; // Conversion rate
  cpa: number;
  impressions: number;
  clicks: number;
  conversions: number;
}

// Creative daily metrics for fatigue detection (per B.4.2.1)
export interface CreativeDailyMetric {
  id: string;
  creativeId: string;
  date: string;
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  ctr: number;
  cvr: number;
  cpa: number;
  frequency: number;
}

// Enhanced Memory Output (per B.3.4.1)
export interface MemoryOutputV3 {
  timestamp: string;
  totals: {
    totalSpend: number;
    totalRevenue: number;
    ltvAdjustedRevenue: number;
    blendedRoas: number;
    ltvRoas: number;
    mer: number; // Marketing Efficiency Ratio
  };
  channels: {
    id: string;
    name: string;
    platform: string;
    spend: number;
    revenue: number;
    roas: number;
    status: 'winner' | 'loser' | 'neutral';
    contribution: number;
    trend: 'up' | 'down' | 'stable';
  }[];
  ltvFactor: number;
  baselineCohortMonth: string;
  recentCohortMonth: string;
}

// Enhanced Oracle Output (per B.4.4.1)
export interface OracleOutputV3 {
  timestamp: string;
  globalRiskLevel: 'green' | 'yellow' | 'red';
  globalRiskScore: number;
  creativeFatigue: {
    creativeId: string;
    creativeName: string;
    channelId: string;
    fatigueProbability7d: number;
    fatigueProbability14d: number;
    predictedPerformanceDrop: number;
    recentCvr: number;
    baselineCvr: number;
    recentCpa: number;
    baselineCpa: number;
    frequency: number;
    recommendedAction: string;
  }[];
  roiDecay: {
    channelId: string;
    channelName: string;
    recentRoas: number;
    baselineRoas: number;
    decayPercentage: number;
    decaySeverity: 'high' | 'medium' | 'low';
    recommendedAction: string;
  }[];
  ltvDrift: {
    recentCohortMonth: string;
    baselineCohortMonth: string;
    recentLtv90d: number;
    baselineLtv90d: number;
    driftPercentage: number;
    driftSeverity: 'high' | 'medium' | 'low';
    trend: 'accelerating' | 'stabilizing' | 'improving';
    recommendedAction: string;
  } | null;
  risks: RiskFactor[]; // Legacy compatibility
}

// Enhanced Curiosity Output (per B.5.4.1)
export interface CuriosityOutputV3 {
  timestamp: string;
  topActions: ActionRecommendationV3[];
  totalOpportunityUsd: number;
  totalOpportunityFormatted: string;
}

// Enhanced Action Recommendation (per B.5.2.1-4)
export interface ActionRecommendationV3 {
  id: string;
  type: 'shift_budget' | 'pause_creative' | 'increase_budget' | 'focus_retention';
  title: string;
  description: string;
  estimatedImpactUsd: number;
  impactFormatted: string;
  confidence: 'high' | 'medium' | 'low';
  confidenceScore: number; // 0-100
  urgency: 'high' | 'medium' | 'low';
  urgencyScore: number; // 0-100
  score: number; // Weighted composite score
  entities: string[];
  rationale: string;
  // Persona-specific microcopy
  microcopy: {
    sarah: string; // CMO view
    jason: string; // VP Growth view
    emily: string; // Director view
  };
}

// Persona types
export type PersonaType = 'sarah' | 'jason' | 'emily';

// Brain State V3
export interface BrainStateV3 {
  timestamp: string;
  organizationId: string;
  memory: MemoryOutputV3;
  oracle: OracleOutputV3;
  curiosity: CuriosityOutputV3;
}
