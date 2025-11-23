import { BrainModule, MemoryOutput, OracleOutput, CuriosityOutput, ActionRecommendation } from '../types';

export class CuriosityModule implements BrainModule<{ memory: MemoryOutput, oracle: OracleOutput }, CuriosityOutput> {
    name = 'CURIOSITY';

    async process(input: { memory: MemoryOutput, oracle: OracleOutput }): Promise<CuriosityOutput> {
        const { memory, oracle } = input;
        const actions: ActionRecommendation[] = [];

        // 1. React to Risks (Oracle)
        oracle.risks.forEach(risk => {
            if (risk.type === 'creative_fatigue') {
                actions.push({
                    id: `act_pause_${risk.entityId}`,
                    type: 'pause_creative',
                    title: `Pause Creative ${risk.entityId}`,
                    description: `Creative is fatigued (ROAS < 2.0). Pause to save budget.`,
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
                    title: `Shift Budget from ${risk.entityId.replace('ch_', '')}`,
                    description: `Channel efficiency is decaying. Shift spend to top performers.`,
                    impact: '+$1,200/week',
                    confidence: 'medium',
                    urgency: 'medium',
                    entities: [risk.entityId]
                });
            }
        });

        // 2. React to Opportunities (Memory)
        const winners = memory.channels.filter(c => c.status === 'winner');
        const losers = memory.channels.filter(c => c.status === 'loser');

        if (winners.length > 0 && losers.length > 0) {
            const winner = winners[0];
            const loser = losers[0];

            // Avoid duplicate "Shift" actions if already covered by ROI Decay
            const existingShift = actions.find(a => a.type === 'shift_budget' && a.entities.includes(loser.id));

            if (!existingShift) {
                actions.push({
                    id: `act_optimize_${loser.id}_to_${winner.id}`,
                    type: 'shift_budget',
                    title: `Shift Budget: ${loser.name} -> ${winner.name}`,
                    description: `Move budget from low ROAS (${loser.roas}) to high ROAS (${winner.roas}) channel.`,
                    impact: '+$2,100/mo',
                    confidence: 'high',
                    urgency: 'medium',
                    entities: [loser.id, winner.id]
                });
            }
        }

        if (winners.length > 0) {
            const winner = winners[0];
            actions.push({
                id: `act_scale_${winner.id}`,
                type: 'increase_budget',
                title: `Scale Up ${winner.name}`,
                description: `Channel is performing exceptionally well (ROAS ${winner.roas}). Increase daily spend by 20%.`,
                impact: '+$3,500 revenue/week',
                confidence: 'high',
                urgency: 'low',
                entities: [winner.id]
            });
        }

        // 3. Rank Actions
        // Priority: High Urgency > High Confidence
        const rankedActions = actions.sort((a, b) => {
            const urgencyScore = { high: 3, medium: 2, low: 1 };
            const confidenceScore = { high: 3, medium: 2, low: 1 };

            const scoreA = urgencyScore[a.urgency] * 10 + confidenceScore[a.confidence];
            const scoreB = urgencyScore[b.urgency] * 10 + confidenceScore[b.confidence];

            return scoreB - scoreA;
        });

        return {
            topActions: rankedActions.slice(0, 3), // Top 3 only
            totalOpportunity: '+$12,450/mo' // Simulated total
        };
    }
}
