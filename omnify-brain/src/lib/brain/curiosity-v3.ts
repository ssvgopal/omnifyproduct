/**
 * CURIOSITY Module V3 - Requirements V3 Compliant
 * 
 * Implements:
 * - B.5.2.1: Shift Budget Actions
 * - B.5.2.2: Pause Creative Actions
 * - B.5.2.3: Increase Budget Actions
 * - B.5.2.4: Retention/LTV Focus Actions
 * - B.5.3.1: Weighted scoring function
 * - B.5.4.1: Output schema with top 3 actions
 * 
 * Key Changes from V1:
 * 1. Four distinct action generators (not just rule-based)
 * 2. Weighted scoring: (impact * 0.4) + (severity * 0.3) + (confidence * 0.2) + (urgency * 0.1)
 * 3. Persona-specific microcopy for each action
 */

import { 
  BrainModule, 
  MemoryOutputV3,
  OracleOutputV3,
  CuriosityOutputV3,
  ActionRecommendationV3,
  PersonaType
} from '../types';

export interface CuriosityInputV3 {
  memory: MemoryOutputV3;
  oracle: OracleOutputV3;
}

// Scoring weights per B.5.3.1
const WEIGHTS = {
  impact: 0.4,
  severity: 0.3,
  confidence: 0.2,
  urgency: 0.1,
};

// Severity scores for normalization
const SEVERITY_SCORES = {
  high: 100,
  medium: 60,
  low: 30,
};

export class CuriosityModuleV3 implements BrainModule<CuriosityInputV3, CuriosityOutputV3> {
  name = 'CURIOSITY_V3';

  async process(input: CuriosityInputV3): Promise<CuriosityOutputV3> {
    const { memory, oracle } = input;
    const actions: ActionRecommendationV3[] = [];

    // 1. Generate Shift Budget Actions (B.5.2.1)
    const shiftActions = this.generateShiftBudgetActions(memory, oracle);
    actions.push(...shiftActions);

    // 2. Generate Pause Creative Actions (B.5.2.2)
    const pauseActions = this.generatePauseCreativeActions(oracle);
    actions.push(...pauseActions);

    // 3. Generate Increase Budget Actions (B.5.2.3)
    const increaseActions = this.generateIncreaseBudgetActions(memory, oracle);
    actions.push(...increaseActions);

    // 4. Generate Retention/LTV Focus Actions (B.5.2.4)
    const retentionActions = this.generateRetentionActions(oracle);
    actions.push(...retentionActions);

    // 5. Score and rank all actions (B.5.3.1)
    const scoredActions = actions.map(action => ({
      ...action,
      score: this.calculateScore(action),
    }));

    // 6. Sort by score and take top 3
    const rankedActions = scoredActions
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);

    // 7. Calculate total opportunity
    const totalOpportunityUsd = rankedActions.reduce(
      (sum, action) => sum + action.estimatedImpactUsd,
      0
    );

    return {
      timestamp: new Date().toISOString(),
      topActions: rankedActions,
      totalOpportunityUsd: this.round(totalOpportunityUsd, 2),
      totalOpportunityFormatted: this.formatCurrency(totalOpportunityUsd) + '/mo',
    };
  }

  /**
   * Generator 1: Shift Budget Actions (B.5.2.1)
   * 
   * Identifies losers/decaying channels from MEMORY/ORACLE
   * and recommends shifting budget to winners.
   */
  private generateShiftBudgetActions(
    memory: MemoryOutputV3,
    oracle: OracleOutputV3
  ): ActionRecommendationV3[] {
    const actions: ActionRecommendationV3[] = [];

    const winners = memory.channels.filter(c => c.status === 'winner');
    const losers = memory.channels.filter(c => c.status === 'loser');
    const decayingChannels = oracle.roiDecay.map(d => d.channelId);

    // For each loser or decaying channel, recommend shift to winner
    for (const loser of losers) {
      if (winners.length === 0) continue;

      const bestWinner = winners.reduce((best, w) => 
        w.roas > best.roas ? w : best
      );

      // Calculate shift amount (10% of loser's spend)
      const shiftAmount = loser.spend * 0.10;
      
      // Estimate impact: shift_amount * (target_ROAS - source_ROAS)
      const estimatedImpact = shiftAmount * (bestWinner.roas - loser.roas);

      // Determine urgency based on decay status
      const isDecaying = decayingChannels.includes(loser.id);
      const urgency: 'high' | 'medium' | 'low' = isDecaying ? 'high' : 'medium';
      const urgencyScore = isDecaying ? 90 : 60;

      actions.push({
        id: `act_shift_${loser.id}_to_${bestWinner.id}`,
        type: 'shift_budget',
        title: `Shift Budget: ${loser.name} → ${bestWinner.name}`,
        description: `Move ${this.formatCurrency(shiftAmount)} from ${loser.name} (ROAS ${loser.roas}x) to ${bestWinner.name} (ROAS ${bestWinner.roas}x).`,
        estimatedImpactUsd: Math.max(estimatedImpact, 0),
        impactFormatted: `+${this.formatCurrency(Math.max(estimatedImpact, 0))}/mo`,
        confidence: 'high',
        confidenceScore: 85,
        urgency,
        urgencyScore,
        score: 0, // Will be calculated later
        entities: [loser.id, bestWinner.id],
        rationale: `${loser.name} is underperforming (${loser.roas}x vs blended ${memory.totals.blendedRoas}x). ${bestWinner.name} has capacity for additional spend.`,
        microcopy: {
          sarah: `Here's exactly where to move budget: Shift ${this.formatCurrency(shiftAmount)} from ${loser.name} to ${bestWinner.name} for +${this.formatCurrency(estimatedImpact)}/mo impact.`,
          jason: `${loser.name} ROAS (${loser.roas}x) is ${this.round((1 - loser.roas / memory.totals.blendedRoas) * 100, 0)}% below blended. Shift 10% to ${bestWinner.name} (${bestWinner.roas}x).`,
          emily: `Move ${this.formatCurrency(shiftAmount)} from ${loser.name} → ${bestWinner.name}. Execute in platform now.`,
        },
      });
    }

    return actions;
  }

  /**
   * Generator 2: Pause Creative Actions (B.5.2.2)
   * 
   * For each creative with fatigue_probability_7d > 0.6,
   * recommend pausing.
   */
  private generatePauseCreativeActions(
    oracle: OracleOutputV3
  ): ActionRecommendationV3[] {
    const actions: ActionRecommendationV3[] = [];

    for (const fatigue of oracle.creativeFatigue) {
      if (fatigue.fatigueProbability7d < 0.6) continue;

      // Estimate impact: current_daily_spend * predicted_performance_drop * 7 days
      // Assuming average daily spend of $500 per creative (would come from data)
      const estimatedDailySpend = 500; // TODO: Get from actual data
      const estimatedImpact = estimatedDailySpend * fatigue.predictedPerformanceDrop * 7;

      const urgency: 'high' | 'medium' | 'low' = 
        fatigue.fatigueProbability7d > 0.8 ? 'high' : 'medium';
      const urgencyScore = fatigue.fatigueProbability7d > 0.8 ? 95 : 70;

      const daysUntilDead = fatigue.fatigueProbability7d > 0.8 ? 3 : 7;

      actions.push({
        id: `act_pause_${fatigue.creativeId}`,
        type: 'pause_creative',
        title: `Pause ${fatigue.creativeName}`,
        description: `Creative showing ${this.round(fatigue.fatigueProbability7d * 100, 0)}% fatigue probability. CVR dropped ${this.round((fatigue.baselineCvr - fatigue.recentCvr) / fatigue.baselineCvr * 100, 0)}%.`,
        estimatedImpactUsd: estimatedImpact,
        impactFormatted: `+${this.formatCurrency(estimatedImpact)}/week saved`,
        confidence: fatigue.fatigueProbability7d > 0.8 ? 'high' : 'medium',
        confidenceScore: this.round(fatigue.fatigueProbability7d * 100, 0),
        urgency,
        urgencyScore,
        score: 0,
        entities: [fatigue.creativeId],
        rationale: `CVR dropped from ${this.round(fatigue.baselineCvr * 100, 2)}% to ${this.round(fatigue.recentCvr * 100, 2)}%. Frequency at ${fatigue.frequency}x. Predicted ${this.round(fatigue.predictedPerformanceDrop * 100, 0)}% further decline.`,
        microcopy: {
          sarah: `${fatigue.creativeName} will break in ${daysUntilDead} days. Pause now to save ${this.formatCurrency(estimatedImpact)}/week.`,
          jason: `${fatigue.creativeName} fatigue: CVR ${this.round(fatigue.recentCvr * 100, 2)}% (was ${this.round(fatigue.baselineCvr * 100, 2)}%), Freq ${fatigue.frequency}x. ${this.round(fatigue.fatigueProbability7d * 100, 0)}% probability of failure in 7d.`,
          emily: `Pause ${fatigue.creativeName} NOW. Rotate in backup creative.`,
        },
      });
    }

    return actions;
  }

  /**
   * Generator 3: Increase Budget Actions (B.5.2.3)
   * 
   * Identifies channels with ROAS > blended_ROAS * 1.2
   * that are not flagged as decaying.
   */
  private generateIncreaseBudgetActions(
    memory: MemoryOutputV3,
    oracle: OracleOutputV3
  ): ActionRecommendationV3[] {
    const actions: ActionRecommendationV3[] = [];

    const decayingChannelIds = oracle.roiDecay.map(d => d.channelId);
    const highPerformers = memory.channels.filter(
      c => c.roas > memory.totals.blendedRoas * 1.2 && !decayingChannelIds.includes(c.id)
    );

    for (const channel of highPerformers) {
      // Calculate increase amount (10% of current spend)
      const increaseAmount = channel.spend * 0.10;
      
      // Estimate impact: increase_amount * (channel_ROAS - 1)
      // This represents the profit from additional spend
      const estimatedImpact = increaseAmount * (channel.roas - 1);

      actions.push({
        id: `act_scale_${channel.id}`,
        type: 'increase_budget',
        title: `Scale Up ${channel.name}`,
        description: `${channel.name} is outperforming (${channel.roas}x vs ${memory.totals.blendedRoas}x blended). Increase budget by 10%.`,
        estimatedImpactUsd: estimatedImpact,
        impactFormatted: `+${this.formatCurrency(estimatedImpact)}/mo`,
        confidence: 'high',
        confidenceScore: 80,
        urgency: 'low',
        urgencyScore: 40,
        score: 0,
        entities: [channel.id],
        rationale: `${channel.name} ROAS (${channel.roas}x) is ${this.round((channel.roas / memory.totals.blendedRoas - 1) * 100, 0)}% above blended. Trend is ${channel.trend}. Capacity for additional spend.`,
        microcopy: {
          sarah: `${channel.name} is your hero. Increase budget by ${this.formatCurrency(increaseAmount)} for +${this.formatCurrency(estimatedImpact)}/mo.`,
          jason: `${channel.name} at ${channel.roas}x ROAS (${this.round((channel.roas / memory.totals.blendedRoas - 1) * 100, 0)}% above blended). Safe to scale 10%. Trend: ${channel.trend}.`,
          emily: `Add ${this.formatCurrency(increaseAmount)} to ${channel.name} daily budget.`,
        },
      });
    }

    return actions;
  }

  /**
   * Generator 4: Retention/LTV Focus Actions (B.5.2.4)
   * 
   * If LTV drift severity = "high", generate focus_retention action.
   */
  private generateRetentionActions(
    oracle: OracleOutputV3
  ): ActionRecommendationV3[] {
    const actions: ActionRecommendationV3[] = [];

    if (!oracle.ltvDrift) return actions;

    const { ltvDrift } = oracle;

    if (ltvDrift.driftSeverity === 'high' || ltvDrift.driftSeverity === 'medium') {
      // Estimate impact based on drift severity
      // Assuming fixing LTV drift could recover 5-10% of revenue
      const estimatedImpact = ltvDrift.driftSeverity === 'high' ? 5000 : 2500;

      const urgency: 'high' | 'medium' | 'low' = 
        ltvDrift.driftSeverity === 'high' ? 'high' : 'medium';
      const urgencyScore = ltvDrift.driftSeverity === 'high' ? 85 : 60;

      actions.push({
        id: 'act_focus_retention',
        type: 'focus_retention',
        title: 'Focus on Customer Retention',
        description: `New cohort LTV is ${Math.abs(ltvDrift.driftPercentage)}% ${ltvDrift.driftPercentage > 0 ? 'lower' : 'higher'} than baseline. ${ltvDrift.trend === 'accelerating' ? 'Drift is accelerating.' : ''}`,
        estimatedImpactUsd: estimatedImpact,
        impactFormatted: `+${this.formatCurrency(estimatedImpact)}/mo potential`,
        confidence: 'medium',
        confidenceScore: 65,
        urgency,
        urgencyScore,
        score: 0,
        entities: [],
        rationale: `Recent cohorts (${ltvDrift.recentCohortMonth}) showing $${ltvDrift.recentLtv90d} 90-day LTV vs $${ltvDrift.baselineLtv90d} baseline. Trend: ${ltvDrift.trend}.`,
        microcopy: {
          sarah: `Customer quality is declining. LTV dropped ${Math.abs(ltvDrift.driftPercentage)}% - this will compound. Prioritize retention.`,
          jason: `LTV drift alert: ${ltvDrift.recentCohortMonth} cohort at $${ltvDrift.recentLtv90d} vs $${ltvDrift.baselineLtv90d} baseline (${ltvDrift.trend}). Review acquisition channels.`,
          emily: `Launch retention campaign. Review email flows and loyalty program.`,
        },
      });
    }

    return actions;
  }

  /**
   * Calculate weighted score (per B.5.3.1)
   * 
   * score = (estimated_impact_usd * 0.4) + 
   *         (severity_weight * 0.3) + 
   *         (confidence_weight * 0.2) + 
   *         (urgency_weight * 0.1)
   */
  private calculateScore(action: ActionRecommendationV3): number {
    // Normalize impact to 0-100 scale (assuming max impact of $10,000)
    const normalizedImpact = Math.min(action.estimatedImpactUsd / 10000 * 100, 100);

    // Get severity score based on urgency (using urgency as proxy for severity)
    const severityScore = action.urgencyScore;

    // Confidence is already 0-100
    const confidenceScore = action.confidenceScore;

    // Urgency is already 0-100
    const urgencyScore = action.urgencyScore;

    const score = 
      (normalizedImpact * WEIGHTS.impact) +
      (severityScore * WEIGHTS.severity) +
      (confidenceScore * WEIGHTS.confidence) +
      (urgencyScore * WEIGHTS.urgency);

    return this.round(score, 2);
  }

  // ============================================
  // Helper Methods
  // ============================================

  private formatCurrency(amount: number): string {
    if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`;
    }
    return `$${amount.toFixed(0)}`;
  }

  private round(value: number, decimals: number): number {
    return Number(value.toFixed(decimals));
  }
}

// Export singleton instance
export const curiosityModuleV3 = new CuriosityModuleV3();
