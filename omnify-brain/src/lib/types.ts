export interface BrainModule<TInput, TOutput> {
  name: string;
  process(input: TInput): Promise<TOutput>;
}

export interface ChannelData {
  id: string;
  name: string;
  platform: 'Meta' | 'Google' | 'TikTok' | 'LinkedIn' | 'Email';
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
