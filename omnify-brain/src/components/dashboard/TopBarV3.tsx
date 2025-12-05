'use client';

/**
 * TopBar V3 - Requirements V3 Compliant
 * 
 * Implements B.6.2.1:
 * - MER (Marketing Efficiency Ratio)
 * - Blended ROAS
 * - LTV-ROAS
 * - Global Risk Level (green/yellow/red indicator)
 * - "Here's what changed this week" narrative
 */

import { BrainStateV3, PersonaType } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { PersonaToggle } from '@/components/shared/PersonaToggle';
import { usePersona } from '@/lib/persona-context';
import { AlertCircle, TrendingUp, TrendingDown, Minus, Brain } from 'lucide-react';

interface TopBarV3Props {
  state: BrainStateV3;
}

export function TopBarV3({ state }: TopBarV3Props) {
  const { persona } = usePersona();
  const { memory, oracle, curiosity } = state;

  // Risk level styling
  const riskStyles = {
    green: { bg: 'bg-green-500', text: 'text-green-700', label: 'LOW RISK' },
    yellow: { bg: 'bg-yellow-500', text: 'text-yellow-700', label: 'MODERATE RISK' },
    red: { bg: 'bg-red-500', text: 'text-red-700', label: 'HIGH RISK' },
  };

  const riskStyle = riskStyles[oracle.globalRiskLevel];

  // Generate "What changed this week" narrative based on persona
  const narrative = generateNarrative(state, persona);

  return (
    <div className="border-b bg-background">
      {/* Main metrics bar - responsive */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between p-4 border-b gap-4">
        {/* Logo and title */}
        <div className="flex items-center justify-between lg:justify-start gap-4">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-purple-600" />
            <h1 className="text-lg lg:text-xl font-bold tracking-tight">Omnify Brain</h1>
          </div>
          <Badge variant="outline" className="text-xs">V3 MVP</Badge>
        </div>

        {/* Metrics - scrollable on mobile */}
        <div className="flex items-center gap-4 lg:gap-6 overflow-x-auto pb-2 lg:pb-0 -mx-4 px-4 lg:mx-0 lg:px-0">
          {/* Blended ROAS */}
          <MetricDisplay
            label="Blended ROAS"
            value={`${memory.totals.blendedRoas.toFixed(2)}x`}
            trend={getTrend(memory.channels)}
          />

          {/* LTV-ROAS */}
          <MetricDisplay
            label="LTV:ROAS"
            value={`${memory.totals.ltvRoas.toFixed(2)}x`}
            highlight
            tooltip={`LTV Factor: ${memory.ltvFactor.toFixed(2)}`}
          />

          {/* CAC - Customer Acquisition Cost */}
          <MetricDisplay
            label="CAC"
            value={formatCurrency(calculateCAC(memory))}
            tooltip="Customer Acquisition Cost"
          />

          {/* 90d CLV - Customer Lifetime Value */}
          <MetricDisplay
            label="90d CLV"
            value={formatCurrency(calculateCLV90d(memory))}
            tooltip="90-day Customer Lifetime Value"
          />

          {/* Global Risk Level */}
          <div className="flex flex-col items-center shrink-0">
            <span className="text-muted-foreground text-xs mb-1">Risk Level</span>
            <Badge className={`${riskStyle.bg} hover:${riskStyle.bg} text-white px-3`}>
              <AlertCircle className="h-3 w-3 mr-1" />
              {riskStyle.label}
            </Badge>
          </div>

          {/* Persona Toggle - hidden on small screens, shown on medium+ */}
          <div className="hidden md:block shrink-0">
            <PersonaToggle />
          </div>
        </div>

        {/* Persona Toggle - shown only on small screens */}
        <div className="md:hidden">
          <PersonaToggle />
        </div>
      </div>

      {/* Narrative bar - "Here's what changed this week" */}
      <div className="px-4 py-3 bg-muted/30">
        <div className="flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-2">
          <span className="text-sm font-medium text-muted-foreground shrink-0">
            {persona === 'sarah' ? "Here's the truth:" : 
             persona === 'jason' ? "This week:" : 
             "Action needed:"}
          </span>
          <p className="text-sm text-foreground">{narrative}</p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// Helper Components
// ============================================

interface MetricDisplayProps {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'stable';
  highlight?: boolean;
  tooltip?: string;
}

function MetricDisplay({ label, value, trend, highlight, tooltip }: MetricDisplayProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400';

  return (
    <div className="flex flex-col items-center" title={tooltip}>
      <span className="text-muted-foreground text-xs mb-1">{label}</span>
      <div className="flex items-center gap-1">
        <span className={`font-bold text-lg ${highlight ? 'text-blue-600' : ''}`}>
          {value}
        </span>
        {trend && <TrendIcon className={`h-4 w-4 ${trendColor}`} />}
      </div>
    </div>
  );
}

// ============================================
// Narrative Generation
// ============================================

function generateNarrative(state: BrainStateV3, persona: PersonaType): string {
  const { memory, oracle, curiosity } = state;

  // Gather key insights
  const winners = memory.channels.filter(c => c.status === 'winner');
  const losers = memory.channels.filter(c => c.status === 'loser');
  const fatigueCount = oracle.creativeFatigue.length;
  const decayCount = oracle.roiDecay.length;
  const hasLtvDrift = oracle.ltvDrift !== null;
  const topAction = curiosity.topActions[0];

  // Generate persona-specific narrative
  switch (persona) {
    case 'sarah': // CMO - Executive summary
      return generateSarahNarrative(winners, losers, fatigueCount, hasLtvDrift, topAction, memory, curiosity);
    
    case 'jason': // VP Growth - Technical details
      return generateJasonNarrative(winners, losers, oracle, topAction, memory);
    
    case 'emily': // Director - Action-focused
      return generateEmilyNarrative(fatigueCount, decayCount, topAction, curiosity);
    
    default:
      return 'No significant changes detected.';
  }
}

function generateSarahNarrative(
  winners: any[], 
  losers: any[], 
  fatigueCount: number,
  hasLtvDrift: boolean,
  topAction: any,
  memory: any,
  curiosity: any
): string {
  const parts: string[] = [];

  // Performance summary
  if (winners.length > 0) {
    parts.push(`${winners[0].name} is your hero at ${winners[0].roas}x ROAS.`);
  }

  // Risk summary
  if (losers.length > 0 || fatigueCount > 0) {
    const issues = [];
    if (losers.length > 0) issues.push(`${losers[0].name} underperforming`);
    if (fatigueCount > 0) issues.push(`${fatigueCount} creative${fatigueCount > 1 ? 's' : ''} fatiguing`);
    parts.push(`Watch out: ${issues.join(', ')}.`);
  }

  // LTV drift
  if (hasLtvDrift) {
    parts.push('Customer quality is declining—this will compound.');
  }

  // Opportunity
  if (topAction) {
    parts.push(`Top move: ${topAction.title} for ${topAction.impactFormatted}.`);
  }

  return parts.join(' ') || 'Performance is stable. No immediate action required.';
}

function generateJasonNarrative(
  winners: any[],
  losers: any[],
  oracle: any,
  topAction: any,
  memory: any
): string {
  const parts: string[] = [];

  // Channel performance
  const channelSummary = memory.channels
    .map((c: any) => `${c.name}: ${c.roas}x (${c.trend})`)
    .join(', ');
  parts.push(`Channels: ${channelSummary}.`);

  // Fatigue alerts
  if (oracle.creativeFatigue.length > 0) {
    const topFatigue = oracle.creativeFatigue[0];
    parts.push(`${topFatigue.creativeName} at ${(topFatigue.fatigueProbability7d * 100).toFixed(0)}% fatigue risk.`);
  }

  // Decay alerts
  if (oracle.roiDecay.length > 0) {
    const topDecay = oracle.roiDecay[0];
    parts.push(`${topDecay.channelName} ROAS dropped ${topDecay.decayPercentage}%.`);
  }

  // LTV drift
  if (oracle.ltvDrift) {
    parts.push(`LTV drift: ${oracle.ltvDrift.driftPercentage}% (${oracle.ltvDrift.trend}).`);
  }

  return parts.join(' ') || 'All metrics within normal ranges.';
}

function generateEmilyNarrative(
  fatigueCount: number,
  decayCount: number,
  topAction: any,
  curiosity: any
): string {
  const parts: string[] = [];

  // Urgent issues
  const urgentCount = fatigueCount + decayCount;
  if (urgentCount > 0) {
    parts.push(`${urgentCount} issue${urgentCount > 1 ? 's' : ''} need attention.`);
  }

  // Top action
  if (topAction) {
    // Use Emily's microcopy if available
    const actionText = topAction.microcopy?.emily || topAction.title;
    parts.push(actionText);
  }

  // Total opportunity
  parts.push(`Total opportunity: ${curiosity.totalOpportunityFormatted}.`);

  return parts.join(' ') || 'No urgent actions. Monitor performance.';
}

// ============================================
// Helper Functions
// ============================================

function getTrend(channels: any[]): 'up' | 'down' | 'stable' {
  const upCount = channels.filter(c => c.trend === 'up').length;
  const downCount = channels.filter(c => c.trend === 'down').length;
  
  if (upCount > downCount) return 'up';
  if (downCount > upCount) return 'down';
  return 'stable';
}

/**
 * Calculate CAC (Customer Acquisition Cost)
 * CAC = Total Spend / Total Conversions
 */
function calculateCAC(memory: any): number {
  const totalSpend = memory.totals.totalSpend || 0;
  // Estimate conversions from revenue and average order value
  // Assuming AOV of ~$75 for beauty/skincare (per research brief)
  const estimatedAOV = 75;
  const estimatedConversions = memory.totals.totalRevenue / estimatedAOV;
  
  if (estimatedConversions <= 0) return 0;
  return totalSpend / estimatedConversions;
}

/**
 * Calculate 90-day CLV (Customer Lifetime Value)
 * Uses LTV factor from cohort data
 */
function calculateCLV90d(memory: any): number {
  // Base CLV from average order value * repeat purchase rate
  // Per research brief: $50M-$350M beauty brands with subscriptions
  const baseAOV = 75;
  const repeatPurchaseMultiplier = memory.ltvFactor || 1.0;
  
  // 90-day CLV = AOV * LTV factor * estimated purchases in 90 days
  // Assuming 1.5 purchases in 90 days for subscription brands
  return baseAOV * repeatPurchaseMultiplier * 1.5;
}

/**
 * Format currency for display
 */
function formatCurrency(amount: number): string {
  if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(1)}K`;
  }
  return `$${amount.toFixed(0)}`;
}
