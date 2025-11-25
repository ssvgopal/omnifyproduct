/**
 * ORACLE Module V3 - Requirements V3 Compliant
 * 
 * Implements:
 * - B.4.2.1: Creative Fatigue Detection (CVR drop > 20%, CPA increase > 25%, frequency > 3.5)
 * - B.4.2.2: ROI Decay Detection (ROAS drop > 15%, baseline comparison)
 * - B.4.2.3: LTV Drift Detection (cohort comparison, 10% threshold)
 * - B.4.4.1: Output schema with structured risk data
 * 
 * Key Changes from V1:
 * 1. Time-series analysis for fatigue (not simple threshold)
 * 2. Baseline comparison for decay (not fixed ROAS threshold)
 * 3. Real cohort data for LTV drift (not hardcoded simulation)
 */

import { 
  BrainModule, 
  DailyMetricExtended,
  CreativeData,
  CreativeDailyMetric,
  CohortData,
  ChannelData,
  OracleOutputV3,
  RiskFactor,
  MemoryOutputV3
} from '../types';

export interface OracleInputV3 {
  dailyMetrics: DailyMetricExtended[];
  creatives: CreativeData[];
  creativeDailyMetrics: CreativeDailyMetric[];
  cohorts: CohortData[];
  channels: ChannelData[];
  memory: MemoryOutputV3;
}

// Thresholds per Requirements V3
const FATIGUE_CVR_DROP_THRESHOLD = 0.20;      // 20% CVR drop
const FATIGUE_CPA_INCREASE_THRESHOLD = 0.25;  // 25% CPA increase
const FATIGUE_FREQUENCY_THRESHOLD = 3.5;      // Frequency > 3.5
const DECAY_ROAS_DROP_THRESHOLD = 0.15;       // 15% ROAS drop
const LTV_DRIFT_THRESHOLD = 0.10;             // 10% LTV drift

export class OracleModuleV3 implements BrainModule<OracleInputV3, OracleOutputV3> {
  name = 'ORACLE_V3';

  async process(input: OracleInputV3): Promise<OracleOutputV3> {
    const { dailyMetrics, creatives, creativeDailyMetrics, cohorts, channels, memory } = input;

    // 1. Detect Creative Fatigue (per B.4.2.1)
    const creativeFatigue = this.detectCreativeFatigue(creatives, creativeDailyMetrics);

    // 2. Detect ROI Decay (per B.4.2.2)
    const roiDecay = this.detectRoiDecay(dailyMetrics, channels);

    // 3. Detect LTV Drift (per B.4.2.3)
    const ltvDrift = this.detectLtvDrift(cohorts);

    // 4. Calculate Global Risk Level (per B.4.3.1)
    const { globalRiskLevel, globalRiskScore } = this.calculateGlobalRisk(
      creativeFatigue,
      roiDecay,
      ltvDrift
    );

    // 5. Generate legacy risks array for backward compatibility
    const risks = this.generateLegacyRisks(creativeFatigue, roiDecay, ltvDrift);

    return {
      timestamp: new Date().toISOString(),
      globalRiskLevel,
      globalRiskScore,
      creativeFatigue,
      roiDecay,
      ltvDrift,
      risks,
    };
  }

  /**
   * Detect Creative Fatigue (per B.4.2.1)
   * 
   * Algorithm:
   * 1. Calculate recent_performance (last 7 days): CVR, CPA
   * 2. Calculate baseline_performance (prior 14-21 days): CVR, CPA
   * 3. Detect: CVR drop > 20% OR CPA increase > 25% OR frequency > 3.5
   * 4. Calculate fatigue_probability_7d and fatigue_probability_14d
   * 5. Estimate predicted_performance_drop percentage
   */
  private detectCreativeFatigue(
    creatives: CreativeData[],
    creativeDailyMetrics: CreativeDailyMetric[]
  ): OracleOutputV3['creativeFatigue'] {
    const fatigueResults: OracleOutputV3['creativeFatigue'] = [];

    for (const creative of creatives) {
      if (creative.status !== 'active') continue;

      const metrics = creativeDailyMetrics
        .filter(m => m.creativeId === creative.id)
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

      if (metrics.length < 14) continue; // Need at least 14 days of data

      // Recent performance (last 7 days)
      const recent7 = metrics.slice(0, 7);
      const recentCvr = this.avgMetric(recent7, 'cvr');
      const recentCpa = this.avgMetric(recent7, 'cpa');
      const recentFrequency = this.avgMetric(recent7, 'frequency');

      // Baseline performance (days 8-21)
      const baseline14 = metrics.slice(7, 21);
      const baselineCvr = this.avgMetric(baseline14, 'cvr');
      const baselineCpa = this.avgMetric(baseline14, 'cpa');

      // Skip if no valid baseline
      if (baselineCvr === 0 || baselineCpa === 0) continue;

      // Calculate changes
      const cvrDrop = (baselineCvr - recentCvr) / baselineCvr;
      const cpaIncrease = (recentCpa - baselineCpa) / baselineCpa;

      // Check fatigue conditions
      const isCvrFatigued = cvrDrop > FATIGUE_CVR_DROP_THRESHOLD;
      const isCpaFatigued = cpaIncrease > FATIGUE_CPA_INCREASE_THRESHOLD;
      const isFrequencyHigh = recentFrequency > FATIGUE_FREQUENCY_THRESHOLD;

      if (isCvrFatigued || isCpaFatigued || isFrequencyHigh) {
        // Calculate fatigue probability
        const fatigueProbability7d = this.calculateFatigueProbability(
          cvrDrop, cpaIncrease, recentFrequency, 7
        );
        const fatigueProbability14d = this.calculateFatigueProbability(
          cvrDrop, cpaIncrease, recentFrequency, 14
        );

        // Estimate performance drop
        const predictedPerformanceDrop = Math.min(
          Math.max(cvrDrop, cpaIncrease) * 1.5,
          0.5 // Cap at 50%
        );

        fatigueResults.push({
          creativeId: creative.id,
          creativeName: creative.name,
          channelId: creative.channelId,
          fatigueProbability7d: this.round(fatigueProbability7d, 2),
          fatigueProbability14d: this.round(fatigueProbability14d, 2),
          predictedPerformanceDrop: this.round(predictedPerformanceDrop, 2),
          recentCvr: this.round(recentCvr, 4),
          baselineCvr: this.round(baselineCvr, 4),
          recentCpa: this.round(recentCpa, 2),
          baselineCpa: this.round(baselineCpa, 2),
          frequency: this.round(recentFrequency, 2),
          recommendedAction: this.generateFatigueAction(creative, fatigueProbability7d),
        });
      }
    }

    return fatigueResults;
  }

  /**
   * Detect ROI Decay (per B.4.2.2)
   * 
   * Algorithm:
   * 1. Calculate recent_ROAS (last 7 days)
   * 2. Calculate baseline_ROAS (prior 14-21 days)
   * 3. Detect: ROAS drop > 15% OR spend increasing but ROAS flat/declining
   * 4. Calculate decay_severity (high/medium/low)
   */
  private detectRoiDecay(
    dailyMetrics: DailyMetricExtended[],
    channels: ChannelData[]
  ): OracleOutputV3['roiDecay'] {
    const decayResults: OracleOutputV3['roiDecay'] = [];

    for (const channel of channels) {
      const metrics = dailyMetrics
        .filter(m => m.channelId === channel.id)
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

      if (metrics.length < 14) continue;

      // Recent ROAS (last 7 days)
      const recent7 = metrics.slice(0, 7);
      const recentRoas = this.calculateRoas(recent7);
      const recentSpend = recent7.reduce((sum, m) => sum + m.spend, 0);

      // Baseline ROAS (days 8-21)
      const baseline14 = metrics.slice(7, 21);
      const baselineRoas = this.calculateRoas(baseline14);
      const baselineSpend = baseline14.reduce((sum, m) => sum + m.spend, 0);

      if (baselineRoas === 0) continue;

      // Calculate decay
      const roasDrop = (baselineRoas - recentRoas) / baselineRoas;
      const spendIncrease = baselineSpend > 0 
        ? (recentSpend - baselineSpend) / baselineSpend 
        : 0;

      // Check decay conditions
      const isRoasDecaying = roasDrop > DECAY_ROAS_DROP_THRESHOLD;
      const isSpendIncreasingWithFlatRoas = spendIncrease > 0.1 && roasDrop > 0;

      if (isRoasDecaying || isSpendIncreasingWithFlatRoas) {
        const decaySeverity = this.calculateDecaySeverity(roasDrop, spendIncrease);

        decayResults.push({
          channelId: channel.id,
          channelName: channel.name,
          recentRoas: this.round(recentRoas, 2),
          baselineRoas: this.round(baselineRoas, 2),
          decayPercentage: this.round(roasDrop * 100, 1),
          decaySeverity,
          recommendedAction: this.generateDecayAction(channel, decaySeverity, roasDrop),
        });
      }
    }

    return decayResults;
  }

  /**
   * Detect LTV Drift (per B.4.2.3)
   * 
   * Algorithm:
   * 1. Read from cohorts table
   * 2. Compare recent cohorts (last 2-3 months) vs historical baseline
   * 3. Flag if new cohort LTV < historical average by > 10%
   * 4. Identify if drift is accelerating or stabilizing
   */
  private detectLtvDrift(cohorts: CohortData[]): OracleOutputV3['ltvDrift'] {
    if (!cohorts || cohorts.length < 4) return null;

    // Filter to 'All' channel cohorts and sort by month
    const sortedCohorts = cohorts
      .filter(c => c.acquisitionChannel === 'All' || !c.acquisitionChannel)
      .filter(c => c.ltv90d && c.ltv90d > 0)
      .sort((a, b) => b.cohortMonth.localeCompare(a.cohortMonth));

    if (sortedCohorts.length < 4) return null;

    // Recent cohorts (last 2-3 months)
    const recentCohorts = sortedCohorts.slice(0, 3);
    const recentAvgLtv = recentCohorts.reduce((sum, c) => sum + c.ltv90d, 0) / recentCohorts.length;

    // Baseline cohorts (6+ months ago)
    const baselineCohorts = sortedCohorts.filter(c => {
      const cohortDate = new Date(c.cohortMonth + '-01');
      const sixMonthsAgo = new Date();
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
      return cohortDate < sixMonthsAgo;
    });

    if (baselineCohorts.length === 0) return null;

    const baselineAvgLtv = baselineCohorts.reduce((sum, c) => sum + c.ltv90d, 0) / baselineCohorts.length;

    if (baselineAvgLtv === 0) return null;

    // Calculate drift
    const driftPercentage = (baselineAvgLtv - recentAvgLtv) / baselineAvgLtv;

    // Only flag if drift exceeds threshold
    if (Math.abs(driftPercentage) < LTV_DRIFT_THRESHOLD) return null;

    // Determine trend (accelerating, stabilizing, improving)
    const trend = this.calculateLtvTrend(recentCohorts);

    // Determine severity
    const driftSeverity: 'high' | 'medium' | 'low' = 
      driftPercentage > 0.20 ? 'high' :
      driftPercentage > 0.15 ? 'medium' : 'low';

    return {
      recentCohortMonth: recentCohorts[0].cohortMonth,
      baselineCohortMonth: baselineCohorts[0].cohortMonth,
      recentLtv90d: this.round(recentAvgLtv, 2),
      baselineLtv90d: this.round(baselineAvgLtv, 2),
      driftPercentage: this.round(driftPercentage * 100, 1),
      driftSeverity,
      trend,
      recommendedAction: this.generateLtvDriftAction(driftSeverity, driftPercentage),
    };
  }

  /**
   * Calculate Global Risk Level (per B.4.3.1)
   * 
   * Logic:
   * - ≥3 high-severity issues → RED
   * - 1-2 moderate issues → YELLOW
   * - 0-1 low issues → GREEN
   */
  private calculateGlobalRisk(
    creativeFatigue: OracleOutputV3['creativeFatigue'],
    roiDecay: OracleOutputV3['roiDecay'],
    ltvDrift: OracleOutputV3['ltvDrift']
  ): { globalRiskLevel: 'green' | 'yellow' | 'red'; globalRiskScore: number } {
    let highSeverityCount = 0;
    let mediumSeverityCount = 0;
    let lowSeverityCount = 0;

    // Count creative fatigue severity
    for (const fatigue of creativeFatigue) {
      if (fatigue.fatigueProbability7d > 0.8) highSeverityCount++;
      else if (fatigue.fatigueProbability7d > 0.6) mediumSeverityCount++;
      else lowSeverityCount++;
    }

    // Count ROI decay severity
    for (const decay of roiDecay) {
      if (decay.decaySeverity === 'high') highSeverityCount++;
      else if (decay.decaySeverity === 'medium') mediumSeverityCount++;
      else lowSeverityCount++;
    }

    // Count LTV drift severity
    if (ltvDrift) {
      if (ltvDrift.driftSeverity === 'high') highSeverityCount++;
      else if (ltvDrift.driftSeverity === 'medium') mediumSeverityCount++;
      else lowSeverityCount++;
    }

    // Determine global risk level
    let globalRiskLevel: 'green' | 'yellow' | 'red';
    if (highSeverityCount >= 3) {
      globalRiskLevel = 'red';
    } else if (highSeverityCount >= 1 || mediumSeverityCount >= 2) {
      globalRiskLevel = 'yellow';
    } else {
      globalRiskLevel = 'green';
    }

    // Calculate risk score (0-100, higher = more risk)
    const globalRiskScore = Math.min(100, 
      highSeverityCount * 30 + mediumSeverityCount * 15 + lowSeverityCount * 5
    );

    return { globalRiskLevel, globalRiskScore };
  }

  /**
   * Generate legacy risks array for backward compatibility
   */
  private generateLegacyRisks(
    creativeFatigue: OracleOutputV3['creativeFatigue'],
    roiDecay: OracleOutputV3['roiDecay'],
    ltvDrift: OracleOutputV3['ltvDrift']
  ): RiskFactor[] {
    const risks: RiskFactor[] = [];

    for (const fatigue of creativeFatigue) {
      risks.push({
        id: `risk_fatigue_${fatigue.creativeId}`,
        type: 'creative_fatigue',
        severity: fatigue.fatigueProbability7d > 0.8 ? 'high' : 
                  fatigue.fatigueProbability7d > 0.6 ? 'medium' : 'low',
        message: `${fatigue.creativeName} showing fatigue. CVR dropped ${this.round((fatigue.baselineCvr - fatigue.recentCvr) / fatigue.baselineCvr * 100, 0)}%.`,
        entityId: fatigue.creativeId,
        predictionDays: fatigue.fatigueProbability7d > 0.8 ? 3 : 7,
      });
    }

    for (const decay of roiDecay) {
      risks.push({
        id: `risk_decay_${decay.channelId}`,
        type: 'roi_decay',
        severity: decay.decaySeverity,
        message: `${decay.channelName} ROAS dropped ${decay.decayPercentage}% from baseline.`,
        entityId: decay.channelId,
      });
    }

    if (ltvDrift) {
      risks.push({
        id: 'risk_ltv_drift',
        type: 'ltv_drift',
        severity: ltvDrift.driftSeverity,
        message: `New cohorts showing ${ltvDrift.driftPercentage}% lower LTV than baseline.`,
        predictionDays: 14,
      });
    }

    return risks;
  }

  // ============================================
  // Helper Methods
  // ============================================

  private avgMetric(metrics: CreativeDailyMetric[], field: keyof CreativeDailyMetric): number {
    if (metrics.length === 0) return 0;
    const sum = metrics.reduce((acc, m) => acc + (Number(m[field]) || 0), 0);
    return sum / metrics.length;
  }

  private calculateRoas(metrics: DailyMetricExtended[]): number {
    const totalSpend = metrics.reduce((sum, m) => sum + m.spend, 0);
    const totalRevenue = metrics.reduce((sum, m) => sum + m.revenue, 0);
    return totalSpend > 0 ? totalRevenue / totalSpend : 0;
  }

  private calculateFatigueProbability(
    cvrDrop: number,
    cpaIncrease: number,
    frequency: number,
    days: number
  ): number {
    // Weighted probability based on signals
    let probability = 0;
    
    if (cvrDrop > FATIGUE_CVR_DROP_THRESHOLD) {
      probability += 0.4 * Math.min(cvrDrop / 0.4, 1);
    }
    if (cpaIncrease > FATIGUE_CPA_INCREASE_THRESHOLD) {
      probability += 0.3 * Math.min(cpaIncrease / 0.5, 1);
    }
    if (frequency > FATIGUE_FREQUENCY_THRESHOLD) {
      probability += 0.3 * Math.min((frequency - 3) / 2, 1);
    }

    // Adjust for time horizon
    if (days === 14) {
      probability = Math.min(probability * 1.3, 0.95);
    }

    return Math.min(probability, 0.95);
  }

  private calculateDecaySeverity(roasDrop: number, spendIncrease: number): 'high' | 'medium' | 'low' {
    if (roasDrop > 0.30 || (roasDrop > 0.20 && spendIncrease > 0.2)) {
      return 'high';
    }
    if (roasDrop > 0.20 || (roasDrop > 0.15 && spendIncrease > 0.1)) {
      return 'medium';
    }
    return 'low';
  }

  private calculateLtvTrend(recentCohorts: CohortData[]): 'accelerating' | 'stabilizing' | 'improving' {
    if (recentCohorts.length < 3) return 'stabilizing';

    const ltv0 = recentCohorts[0].ltv90d;
    const ltv1 = recentCohorts[1].ltv90d;
    const ltv2 = recentCohorts[2].ltv90d;

    const change1 = ltv1 > 0 ? (ltv0 - ltv1) / ltv1 : 0;
    const change2 = ltv2 > 0 ? (ltv1 - ltv2) / ltv2 : 0;

    if (change1 < change2 && change1 < -0.02) {
      return 'accelerating'; // Getting worse faster
    }
    if (change1 > 0) {
      return 'improving';
    }
    return 'stabilizing';
  }

  private generateFatigueAction(creative: CreativeData, probability: number): string {
    if (probability > 0.8) {
      return `Pause ${creative.name} immediately and rotate in fresh creative.`;
    }
    if (probability > 0.6) {
      return `Prepare replacement for ${creative.name}. Reduce spend by 30%.`;
    }
    return `Monitor ${creative.name} closely. Consider A/B testing new variants.`;
  }

  private generateDecayAction(
    channel: ChannelData,
    severity: 'high' | 'medium' | 'low',
    roasDrop: number
  ): string {
    if (severity === 'high') {
      return `Shift 20% of ${channel.name} budget to top performers immediately.`;
    }
    if (severity === 'medium') {
      return `Review ${channel.name} targeting and creatives. Consider 10% budget shift.`;
    }
    return `Monitor ${channel.name} performance. No immediate action required.`;
  }

  private generateLtvDriftAction(severity: 'high' | 'medium' | 'low', driftPct: number): string {
    if (severity === 'high') {
      return `Critical: Focus on retention campaigns. Review acquisition quality.`;
    }
    if (severity === 'medium') {
      return `Investigate cohort quality. Consider retention-focused initiatives.`;
    }
    return `Monitor LTV trends. No immediate action required.`;
  }

  private round(value: number, decimals: number): number {
    return Number(value.toFixed(decimals));
  }
}

// Export singleton instance
export const oracleModuleV3 = new OracleModuleV3();
