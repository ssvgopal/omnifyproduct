import { BrainModule, MemoryOutput, OracleOutput, CuriosityOutput, ActionRecommendation } from '../types';
import { ClaudeAnalyzer } from '../ai/anthropic-client';

export class CuriosityModuleProduction implements BrainModule<{ memory: MemoryOutput, oracle: OracleOutput }, CuriosityOutput> {
    name = 'CURIOSITY_PRODUCTION';
    private claude?: ClaudeAnalyzer;

    constructor() {
        if (process.env.ANTHROPIC_API_KEY) {
            this.claude = new ClaudeAnalyzer(process.env.ANTHROPIC_API_KEY);
        }
    }

    async process(input: { memory: MemoryOutput, oracle: OracleOutput }): Promise<CuriosityOutput> {
        const { memory, oracle } = input;
        let actions: ActionRecommendation[] = [];

        // 1. Try AI-powered recommendations first
        if (this.claude) {
            try {
                const aiActions = await this.claude.generateBudgetRecommendations({
                    channels: memory.channels.map(c => ({
                        name: c.name,
                        roas: c.roas,
                        spend: memory.totalSpend * (c.contribution / 100),
                        status: c.status
                    })),
                    totalBudget: memory.totalSpend
                });

                if (aiActions.length > 0) {
                    actions = aiActions;
                }
            } catch (error) {
                console.error('[CURIOSITY] AI recommendations failed, using fallback');
            }
        }

        // 2. Fallback to rule-based recommendations
        if (actions.length === 0) {
            // React to Risks
            oracle.risks.forEach(risk => {
                if (risk.type === 'creative_fatigue') {
                    actions.push({
                        id: `act_pause_${risk.entityId}`,
                        type: 'pause_creative',
                        title: `Pause Creative ${risk.entityId}`,
                        description: `Creative is fatigued. Pause to save budget.`,
                        impact: '+$450/day saved',
                        confidence: 'high',
                        urgency: 'high',
                        entities: [risk.entityId || '']
                    });
                }
                if (risk.type === 'roi_decay' && risk.entityId) {
                    actions.push({
                        id: `act_shift_${risk.entityId}`,
                        type: 'shift_budget',
                        title: `Shift Budget from ${risk.entityId}`,
                        description: `Channel efficiency is decaying. Shift spend to top performers.`,
                        impact: '+$1,200/week',
                        confidence: 'medium',
                        urgency: 'medium',
                        entities: [risk.entityId]
                    });
                }
            });

            // React to Opportunities
            const winners = memory.channels.filter(c => c.status === 'winner');
            const losers = memory.channels.filter(c => c.status === 'loser');

            if (winners.length > 0 && losers.length > 0) {
                const winner = winners[0];
                const loser = losers[0];

                actions.push({
                    id: `act_optimize_${loser.id}_to_${winner.id}`,
                    type: 'shift_budget',
                    title: `Shift Budget: ${loser.name} → ${winner.name}`,
                    description: `Move budget from low ROAS (${loser.roas}) to high ROAS (${winner.roas}) channel.`,
                    impact: '+$2,100/mo',
                    confidence: 'high',
                    urgency: 'medium',
                    entities: [loser.id, winner.id]
                });
            }

            if (winners.length > 0) {
                const winner = winners[0];
                actions.push({
                    id: `act_scale_${winner.id}`,
                    type: 'increase_budget',
                    title: `Scale Up ${winner.name}`,
                    description: `Channel performing exceptionally (ROAS ${winner.roas}). Increase daily spend by 20%.`,
                    impact: '+$3,500 revenue/week',
                    confidence: 'high',
                    urgency: 'low',
                    entities: [winner.id]
                });
            }
        }

        // 3. Rank Actions
        const rankedActions = actions.sort((a, b) => {
            const urgencyScore = { high: 3, medium: 2, low: 1 };
            const confidenceScore = { high: 3, medium: 2, low: 1 };

            const scoreA = urgencyScore[a.urgency] * 10 + confidenceScore[a.confidence];
            const scoreB = urgencyScore[b.urgency] * 10 + confidenceScore[b.confidence];

            return scoreB - scoreA;
        });

        return {
            topActions: rankedActions.slice(0, 3),
            totalOpportunity: '+$12,450/mo'
        };
    }
}
