/**
 * MEMORY Module V3 - Requirements V3 Compliant
 * 
 * Implements:
 * - B.3.2.1: LTV Factor calculation from cohorts table
 * - B.3.3.1: Winner/Loser thresholds relative to blended ROAS
 * - B.3.4.1: Output schema with totals wrapper
 * 
 * Key Changes from V1:
 * 1. LTV Factor calculated from real cohort data (not hardcoded 1.25)
 * 2. Winner/Loser based on blended ROAS comparison (not fixed thresholds)
 * 3. Output wrapped in totals object with timestamp
 */

import { 
  BrainModule, 
  DailyMetricExtended, 
  ChannelData, 
  CohortData,
  MemoryOutputV3 
} from '../types';

export interface MemoryInputV3 {
  dailyMetrics: DailyMetricExtended[];
  channels: ChannelData[];
  cohorts: CohortData[];
  organizationId: string;
}

// Thresholds per Requirements V3
const WINNER_THRESHOLD = 1.15; // > blended * 1.15
const LOSER_THRESHOLD = 0.85;  // < blended * 0.85

export class MemoryModuleV3 implements BrainModule<MemoryInputV3, MemoryOutputV3> {
  name = 'MEMORY_V3';

  async process(input: MemoryInputV3): Promise<MemoryOutputV3> {
    const { dailyMetrics, channels, cohorts } = input;

    // 1. Calculate Totals
    const totalSpend = dailyMetrics.reduce((sum, m) => sum + m.spend, 0);
    const totalRevenue = dailyMetrics.reduce((sum, m) => sum + m.revenue, 0);
    const blendedRoas = totalSpend > 0 ? totalRevenue / totalSpend : 0;

    // 2. Calculate LTV Factor from Cohorts (per B.3.2.1)
    const { ltvFactor, baselineCohortMonth, recentCohortMonth } = this.calculateLtvFactor(cohorts);
    
    // 3. Calculate LTV-adjusted metrics
    const ltvAdjustedRevenue = totalRevenue * ltvFactor;
    const ltvRoas = totalSpend > 0 ? ltvAdjustedRevenue / totalSpend : 0;
    
    // 4. Calculate MER (Marketing Efficiency Ratio)
    // MER = Total Revenue / Total Marketing Spend (including non-paid)
    const mer = totalSpend > 0 ? totalRevenue / totalSpend : 0;

    // 5. Analyze Channels with relative thresholds (per B.3.3.1)
    const channelPerformance = this.analyzeChannels(dailyMetrics, channels, blendedRoas);

    return {
      timestamp: new Date().toISOString(),
      totals: {
        totalSpend: this.round(totalSpend, 2),
        totalRevenue: this.round(totalRevenue, 2),
        ltvAdjustedRevenue: this.round(ltvAdjustedRevenue, 2),
        blendedRoas: this.round(blendedRoas, 2),
        ltvRoas: this.round(ltvRoas, 2),
        mer: this.round(mer, 2),
      },
      channels: channelPerformance,
      ltvFactor: this.round(ltvFactor, 4),
      baselineCohortMonth,
      recentCohortMonth,
    };
  }

  /**
   * Calculate LTV Factor from cohorts table
   * Formula: ltv_factor = recent_cohort_ltv_90d / baseline_cohort_ltv_90d
   * 
   * Per B.3.2.1:
   * - Recent cohort: Last 2-3 months
   * - Baseline cohort: Historical baseline (6+ months ago)
   */
  private calculateLtvFactor(cohorts: CohortData[]): {
    ltvFactor: number;
    baselineCohortMonth: string;
    recentCohortMonth: string;
  } {
    if (!cohorts || cohorts.length === 0) {
      // Fallback to default if no cohort data
      return {
        ltvFactor: 1.0,
        baselineCohortMonth: 'N/A',
        recentCohortMonth: 'N/A',
      };
    }

    // Sort cohorts by month (descending)
    const sortedCohorts = [...cohorts]
      .filter(c => c.acquisitionChannel === 'All' || !c.acquisitionChannel)
      .sort((a, b) => b.cohortMonth.localeCompare(a.cohortMonth));

    if (sortedCohorts.length < 2) {
      // Not enough data for comparison
      return {
        ltvFactor: 1.0,
        baselineCohortMonth: sortedCohorts[0]?.cohortMonth || 'N/A',
        recentCohortMonth: sortedCohorts[0]?.cohortMonth || 'N/A',
      };
    }

    // Recent cohort: Most recent with valid LTV data
    const recentCohort = sortedCohorts.find(c => c.ltv90d && c.ltv90d > 0);
    
    // Baseline cohort: 6+ months ago with valid LTV data
    const sixMonthsAgo = this.getMonthOffset(-6);
    const baselineCohort = sortedCohorts.find(
      c => c.cohortMonth <= sixMonthsAgo && c.ltv90d && c.ltv90d > 0
    ) || sortedCohorts[sortedCohorts.length - 1]; // Fallback to oldest

    if (!recentCohort || !baselineCohort || !baselineCohort.ltv90d) {
      return {
        ltvFactor: 1.0,
        baselineCohortMonth: baselineCohort?.cohortMonth || 'N/A',
        recentCohortMonth: recentCohort?.cohortMonth || 'N/A',
      };
    }

    const ltvFactor = recentCohort.ltv90d / baselineCohort.ltv90d;

    return {
      ltvFactor: Math.max(0.5, Math.min(2.0, ltvFactor)), // Clamp to reasonable range
      baselineCohortMonth: baselineCohort.cohortMonth,
      recentCohortMonth: recentCohort.cohortMonth,
    };
  }

  /**
   * Analyze channel performance with relative thresholds
   * 
   * Per B.3.3.1:
   * - Winner: chRoas > blendedRoas * 1.15
   * - Loser: chRoas < blendedRoas * 0.85
   * - Neutral: everything else
   */
  private analyzeChannels(
    dailyMetrics: DailyMetricExtended[],
    channels: ChannelData[],
    blendedRoas: number
  ): MemoryOutputV3['channels'] {
    const winnerThreshold = blendedRoas * WINNER_THRESHOLD;
    const loserThreshold = blendedRoas * LOSER_THRESHOLD;

    const totalRevenue = dailyMetrics.reduce((sum, m) => sum + m.revenue, 0);

    return channels.map(channel => {
      const channelMetrics = dailyMetrics.filter(m => m.channelId === channel.id);
      const chSpend = channelMetrics.reduce((sum, m) => sum + m.spend, 0);
      const chRevenue = channelMetrics.reduce((sum, m) => sum + m.revenue, 0);
      const chRoas = chSpend > 0 ? chRevenue / chSpend : 0;

      // Determine status using relative thresholds
      let status: 'winner' | 'loser' | 'neutral' = 'neutral';
      if (chRoas > winnerThreshold) {
        status = 'winner';
      } else if (chRoas < loserThreshold) {
        status = 'loser';
      }

      // Calculate trend (compare last 7 days vs prior 7 days)
      const trend = this.calculateTrend(channelMetrics);

      return {
        id: channel.id,
        name: channel.name,
        platform: channel.platform,
        spend: this.round(chSpend, 2),
        revenue: this.round(chRevenue, 2),
        roas: this.round(chRoas, 2),
        status,
        contribution: totalRevenue > 0 ? this.round((chRevenue / totalRevenue) * 100, 1) : 0,
        trend,
      };
    });
  }

  /**
   * Calculate performance trend
   * Compares last 7 days vs prior 7 days
   */
  private calculateTrend(metrics: DailyMetricExtended[]): 'up' | 'down' | 'stable' {
    if (metrics.length < 14) return 'stable';

    const sorted = [...metrics].sort((a, b) => 
      new Date(b.date).getTime() - new Date(a.date).getTime()
    );

    const recent7 = sorted.slice(0, 7);
    const prior7 = sorted.slice(7, 14);

    const recentAvgRoas = recent7.reduce((sum, m) => sum + m.roas, 0) / recent7.length;
    const priorAvgRoas = prior7.reduce((sum, m) => sum + m.roas, 0) / prior7.length;

    const change = priorAvgRoas > 0 ? (recentAvgRoas - priorAvgRoas) / priorAvgRoas : 0;

    if (change > 0.05) return 'up';
    if (change < -0.05) return 'down';
    return 'stable';
  }

  /**
   * Get month string offset from current month
   */
  private getMonthOffset(months: number): string {
    const date = new Date();
    date.setMonth(date.getMonth() + months);
    return date.toISOString().slice(0, 7); // 'YYYY-MM'
  }

  /**
   * Round number to specified decimal places
   */
  private round(value: number, decimals: number): number {
    return Number(value.toFixed(decimals));
  }
}

// Export singleton instance
export const memoryModuleV3 = new MemoryModuleV3();
