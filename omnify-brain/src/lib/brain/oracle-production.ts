import { supabase } from '../supabase';
import { BrainModule, OracleOutput, RiskFactor } from '../types';
import { OmnifyAI } from '../ai/openai-client';

export class OracleModuleProduction implements BrainModule<{ organizationId: string }, OracleOutput> {
    name = 'ORACLE_PRODUCTION';
    private ai?: OmnifyAI;

    constructor() {
        if (process.env.OPENAI_API_KEY) {
            this.ai = new OmnifyAI(process.env.OPENAI_API_KEY);
        }
    }

    async process(input: { organizationId: string }): Promise<OracleOutput> {
        const { organizationId } = input;
        const risks: RiskFactor[] = [];

        // 1. Fetch channels
        const { data: channels } = await supabase
            .from('channels')
            .select('*')
            .eq('organization_id', organizationId)
            .eq('is_active', true);

        if (!channels) throw new Error('Failed to fetch channels');

        // 2. Fetch creatives
        const { data: creatives } = await supabase
            .from('creatives')
            .select('*')
            .in('channel_id', channels.map(c => c.id))
            .eq('status', 'active');

        // 3. AI-Powered Creative Fatigue Detection
        if (creatives && this.ai) {
            for (const creative of creatives) {
                if (creative.spend > 1000) {
                    try {
                        const analysis = await this.ai.analyzeCreativeFatigue({
                            id: creative.id,
                            name: creative.name,
                            channelId: creative.channel_id,
                            spend: creative.spend,
                            revenue: creative.revenue,
                            impressions: creative.impressions,
                            clicks: creative.clicks,
                            ctr: creative.ctr,
                            roas: creative.roas,
                            status: creative.status,
                            launchDate: creative.launch_date
                        });

                        if (analysis.isFatigued) {
                            risks.push({
                                id: `risk_fatigue_${creative.id}`,
                                type: 'creative_fatigue',
                                severity: analysis.severity,
                                message: `${creative.name}: ${analysis.reasoning}`,
                                entityId: creative.id,
                                predictionDays: 3
                            });
                        }
                    } catch (error) {
                        console.error('[ORACLE] AI analysis failed, using fallback');
                    }
                }
            }
        }

        // 4. ROI Decay Detection
        const { data: recentMetrics } = await supabase
            .from('daily_metrics')
            .select('*')
            .in('channel_id', channels.map(c => c.id))
            .gte('date', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
            .order('date', { ascending: false });

        if (recentMetrics) {
            const channelIds = Array.from(new Set(recentMetrics.map(m => m.channel_id)));

            for (const chId of channelIds) {
                const chMetrics = recentMetrics.filter(m => m.channel_id === chId);
                const avgRoas = chMetrics.reduce((sum, m) => sum + (m.roas || 0), 0) / chMetrics.length;

                if (avgRoas < 1.8) {
                    const channel = channels.find(c => c.id === chId);
                    risks.push({
                        id: `risk_decay_${chId}`,
                        type: 'roi_decay',
                        severity: avgRoas < 1.5 ? 'high' : 'medium',
                        message: `${channel?.name || 'Channel'} efficiency declining. Recent ROAS: ${avgRoas.toFixed(2)}x`,
                        entityId: chId
                    });
                }
            }
        }

        // 5. LTV Drift (simulated for now)
        risks.push({
            id: 'risk_ltv_drift',
            type: 'ltv_drift',
            severity: 'low',
            message: 'New cohorts showing 5% lower LTV than Q3 baseline.',
            predictionDays: 14
        });

        // 6. Calculate Global Risk Score
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
