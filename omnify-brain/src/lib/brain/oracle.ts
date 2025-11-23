import { BrainModule, DailyMetric, CreativeData, OracleOutput, RiskFactor } from '../types';

export class OracleModule implements BrainModule<{ dailyMetrics: DailyMetric[], creatives: CreativeData[] }, OracleOutput> {
    name = 'ORACLE';

    async process(input: { dailyMetrics: DailyMetric[], creatives: CreativeData[] }): Promise<OracleOutput> {
        const { dailyMetrics, creatives } = input;
        const risks: RiskFactor[] = [];

        // 1. Creative Fatigue Detection
        // Rule: Active creative with Spend > $1000 AND ROAS < 2.0
        creatives.forEach(cr => {
            if (cr.status === 'active' && cr.spend > 1000 && cr.roas < 2.0) {
                risks.push({
                    id: `risk_fatigue_${cr.id}`,
                    type: 'creative_fatigue',
                    severity: 'high',
                    message: `Creative ${cr.name} is showing signs of fatigue. ROAS dropped to ${cr.roas}.`,
                    entityId: cr.id,
                    predictionDays: 3 // "Will die in 3 days"
                });
            }
        });

        // 2. ROI Decay Detection (Channel Level)
        // Rule: Check last 3 days vs previous 7 days (Simplified: Check if channel is 'loser' in recent metrics)
        // We'll group metrics by channel first
        const channelIds = Array.from(new Set(dailyMetrics.map(m => m.channelId)));

        channelIds.forEach(chId => {
            const chMetrics = dailyMetrics.filter(m => m.channelId === chId).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

            // Take last 3 days
            const recent = chMetrics.slice(0, 3);
            const recentRoas = recent.reduce((sum, m) => sum + m.roas, 0) / (recent.length || 1);

            if (recentRoas < 1.8) {
                risks.push({
                    id: `risk_decay_${chId}`,
                    type: 'roi_decay',
                    severity: 'medium',
                    message: `Channel ${chId.replace('ch_', '')} efficiency is decaying. Recent ROAS: ${recentRoas.toFixed(2)}.`,
                    entityId: chId
                });
            }
        });

        // 3. LTV Drift (Simulated)
        // Randomly trigger a low-risk drift for demo
        risks.push({
            id: 'risk_ltv_drift',
            type: 'ltv_drift',
            severity: 'low',
            message: 'New cohorts showing 5% lower LTV than Q3 baseline.',
            predictionDays: 14
        });

        // 4. Calculate Global Risk Score
        // Base 100 (Safe). Subtract for risks.
        let score = 100;
        risks.forEach(r => {
            if (r.severity === 'high') score -= 20;
            if (r.severity === 'medium') score -= 10;
            if (r.severity === 'low') score -= 5;
        });
        score = Math.max(0, score);

        let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
        if (score < 50) riskLevel = 'critical';
        else if (score < 70) riskLevel = 'high';
        else if (score < 85) riskLevel = 'medium';

        return {
            globalRiskScore: score,
            riskLevel,
            risks
        };
    }
}
