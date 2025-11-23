import OpenAI from 'openai';
import { CreativeData, RiskFactor } from '../types';

export class OmnifyAI {
    private openai: OpenAI;

    constructor(apiKey: string) {
        this.openai = new OpenAI({ apiKey });
    }

    /**
     * Analyze creative fatigue using AI
     */
    async analyzeCreativeFatigue(creative: CreativeData): Promise<{
        isFatigued: boolean;
        severity: 'low' | 'medium' | 'high';
        reasoning: string;
        recommendations: string[];
    }> {
        const prompt = `Analyze this ad creative performance data and determine if it's showing signs of fatigue:

Creative: ${creative.name}
Launch Date: ${creative.launchDate}
Current ROAS: ${creative.roas}x
Spend: $${creative.spend}
CTR: ${creative.ctr}%
Status: ${creative.status}

Provide analysis in JSON format with:
- isFatigued: boolean
- severity: "low" | "medium" | "high"
- reasoning: string (brief explanation)
- recommendations: string[] (2-3 actionable suggestions)`;

        try {
            const response = await this.openai.chat.completions.create({
                model: 'gpt-4',
                messages: [
                    {
                        role: 'system',
                        content: 'You are an expert marketing analyst specializing in ad creative performance. Analyze data and provide actionable insights in JSON format.'
                    },
                    { role: 'user', content: prompt }
                ],
                response_format: { type: 'json_object' },
                temperature: 0.3
            });

            const result = JSON.parse(response.choices[0].message.content || '{}');
            return result;
        } catch (error: any) {
            console.error('[OPENAI] Error analyzing creative:', error.message);
            // Fallback to rule-based
            return {
                isFatigued: creative.roas < 2.0 && creative.spend > 1000,
                severity: creative.roas < 1.5 ? 'high' : creative.roas < 2.0 ? 'medium' : 'low',
                reasoning: 'AI analysis unavailable, using rule-based detection',
                recommendations: ['Pause creative', 'Test new variations', 'Reduce budget']
            };
        }
    }

    /**
     * Generate executive summary
     */
    async generateExecutiveSummary(data: {
        totalSpend: number;
        totalRevenue: number;
        blendedRoas: number;
        risks: RiskFactor[];
    }): Promise<string> {
        const prompt = `Generate a concise executive summary (2-3 sentences) for this marketing performance:

Total Spend: $${data.totalSpend.toLocaleString()}
Total Revenue: $${data.totalRevenue.toLocaleString()}
Blended ROAS: ${data.blendedRoas}x
Active Risks: ${data.risks.length}

Focus on key insights and actionable takeaways for a CMO.`;

        try {
            const response = await this.openai.chat.completions.create({
                model: 'gpt-4',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a marketing analytics expert. Provide concise, executive-level summaries.'
                    },
                    { role: 'user', content: prompt }
                ],
                max_tokens: 150,
                temperature: 0.5
            });

            return response.choices[0].message.content || 'Summary unavailable';
        } catch (error: any) {
            console.error('[OPENAI] Error generating summary:', error.message);
            return `Spent $${data.totalSpend.toLocaleString()} generating $${data.totalRevenue.toLocaleString()} in revenue (${data.blendedRoas}x ROAS). ${data.risks.length} active risks require attention.`;
        }
    }

    /**
     * Detect anomalies in metrics
     */
    async detectAnomalies(metrics: Array<{ date: string; value: number }>, metricName: string): Promise<{
        hasAnomaly: boolean;
        anomalyDates: string[];
        explanation: string;
    }> {
        const prompt = `Analyze this time-series data for ${metricName} and detect anomalies:

${metrics.map(m => `${m.date}: ${m.value}`).join('\n')}

Identify any unusual spikes or drops. Return JSON with:
- hasAnomaly: boolean
- anomalyDates: string[] (dates with anomalies)
- explanation: string`;

        try {
            const response = await this.openai.chat.completions.create({
                model: 'gpt-4',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a data analyst specializing in anomaly detection. Analyze time-series data and identify unusual patterns.'
                    },
                    { role: 'user', content: prompt }
                ],
                response_format: { type: 'json_object' },
                temperature: 0.2
            });

            return JSON.parse(response.choices[0].message.content || '{}');
        } catch (error: any) {
            console.error('[OPENAI] Error detecting anomalies:', error.message);
            return {
                hasAnomaly: false,
                anomalyDates: [],
                explanation: 'Anomaly detection unavailable'
            };
        }
    }
}
