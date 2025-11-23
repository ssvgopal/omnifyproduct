import Anthropic from '@anthropic-ai/sdk';
import { BrainState, ActionRecommendation } from '../types';

export class ClaudeAnalyzer {
    private anthropic: Anthropic;

    constructor(apiKey: string) {
        this.anthropic = new Anthropic({ apiKey });
    }

    /**
     * Generate strategic budget recommendations
     */
    async generateBudgetRecommendations(data: {
        channels: Array<{ name: string; roas: number; spend: number; status: string }>;
        totalBudget: number;
    }): Promise<ActionRecommendation[]> {
        const prompt = `You are a marketing strategist. Analyze this channel performance data and generate 3 specific budget reallocation recommendations:

Total Budget: $${data.totalBudget}

Channels:
${data.channels.map(c => `- ${c.name}: $${c.spend} spend, ${c.roas}x ROAS, Status: ${c.status}`).join('\n')}

For each recommendation, provide:
1. type: "shift_budget" | "increase_budget" | "pause_creative"
2. title: Brief action title
3. description: Detailed explanation
4. impact: Estimated dollar impact (e.g., "+$1,200/week")
5. confidence: "high" | "medium" | "low"
6. urgency: "high" | "medium" | "low"
7. entities: Array of channel names involved

Return as JSON array.`;

        try {
            const response = await this.anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 1500,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ]
            });

            const content = response.content[0];
            if (content.type === 'text') {
                // Extract JSON from response
                const jsonMatch = content.text.match(/\[[\s\S]*\]/);
                if (jsonMatch) {
                    const recommendations = JSON.parse(jsonMatch[0]);
                    return recommendations.map((r: any, i: number) => ({
                        id: `claude_rec_${i}`,
                        ...r
                    }));
                }
            }

            return [];
        } catch (error: any) {
            console.error('[CLAUDE] Error generating recommendations:', error.message);
            return [];
        }
    }

    /**
     * Generate deep-dive analysis report
     */
    async generateAnalysisReport(brainState: BrainState): Promise<string> {
        const prompt = `Generate a comprehensive marketing performance analysis report based on this data:

MEMORY (Attribution):
- Total Spend: $${brainState.memory.totalSpend}
- Total Revenue: $${brainState.memory.totalRevenue}
- Blended ROAS: ${brainState.memory.blendedRoas}x
- Channels: ${JSON.stringify(brainState.memory.channels)}

ORACLE (Risks):
- Risk Level: ${brainState.oracle.riskLevel}
- Active Risks: ${brainState.oracle.risks.length}
- Risks: ${JSON.stringify(brainState.oracle.risks)}

CURIOSITY (Actions):
- Top Actions: ${JSON.stringify(brainState.curiosity.topActions)}

Provide:
1. Executive Summary (2-3 paragraphs)
2. Key Insights (3-5 bullet points)
3. Risk Analysis (detailed breakdown)
4. Strategic Recommendations (prioritized list)
5. Next Steps (actionable timeline)

Format as markdown.`;

        try {
            const response = await this.anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 3000,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ]
            });

            const content = response.content[0];
            return content.type === 'text' ? content.text : 'Report generation failed';
        } catch (error: any) {
            console.error('[CLAUDE] Error generating report:', error.message);
            return '# Analysis Report\n\nReport generation unavailable. Please check API credentials.';
        }
    }

    /**
     * Multi-step reasoning for complex optimization
     */
    async optimizeBudgetAllocation(data: {
        channels: Array<{ name: string; roas: number; spend: number }>;
        totalBudget: number;
        constraints: string[];
    }): Promise<{
        allocation: Record<string, number>;
        reasoning: string;
        expectedROAS: number;
    }> {
        const prompt = `You are an expert in marketing budget optimization. Use multi-step reasoning to determine the optimal budget allocation:

Current State:
${data.channels.map(c => `- ${c.name}: $${c.spend} (${c.roas}x ROAS)`).join('\n')}

Total Budget: $${data.totalBudget}
Constraints: ${data.constraints.join(', ')}

Think step-by-step:
1. Analyze current efficiency of each channel
2. Identify reallocation opportunities
3. Calculate expected outcomes
4. Propose optimal allocation

Return JSON with:
- allocation: { channelName: newBudget }
- reasoning: step-by-step explanation
- expectedROAS: predicted blended ROAS`;

        try {
            const response = await this.anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 2000,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ]
            });

            const content = response.content[0];
            if (content.type === 'text') {
                const jsonMatch = content.text.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    return JSON.parse(jsonMatch[0]);
                }
            }

            return {
                allocation: {},
                reasoning: 'Optimization failed',
                expectedROAS: 0
            };
        } catch (error: any) {
            console.error('[CLAUDE] Error optimizing budget:', error.message);
            return {
                allocation: {},
                reasoning: 'Optimization unavailable',
                expectedROAS: 0
            };
        }
    }
}
