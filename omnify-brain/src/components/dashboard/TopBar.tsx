import { BrainState } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { PersonaToggle } from '@/components/shared/PersonaToggle';

interface TopBarProps {
    state: BrainState;
}

export function TopBar({ state }: TopBarProps) {
    const { memory, oracle } = state;

    const riskColor =
        oracle.riskLevel === 'critical' ? 'bg-red-500' :
            oracle.riskLevel === 'high' ? 'bg-orange-500' :
                oracle.riskLevel === 'medium' ? 'bg-yellow-500' : 'bg-green-500';

    return (
        <div className="flex items-center justify-between p-6 border-b bg-background">
            <div className="flex items-center gap-4">
                <h1 className="text-2xl font-bold tracking-tight">Omnify Brain</h1>
                <Badge variant="outline" className="text-xs">MVP Demo</Badge>
            </div>

            <div className="flex items-center gap-8">
                <div className="flex gap-6 text-sm">
                    <div className="flex flex-col items-center">
                        <span className="text-muted-foreground text-xs">Blended ROAS</span>
                        <span className="font-bold text-lg">{memory.blendedRoas.toFixed(2)}x</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-muted-foreground text-xs">LTV:ROAS</span>
                        <span className="font-bold text-lg text-blue-600">{memory.ltvRoas.toFixed(2)}x</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-muted-foreground text-xs">Risk Level</span>
                        <Badge className={`${riskColor} hover:${riskColor} text-white`}>
                            {oracle.riskLevel.toUpperCase()} ({oracle.globalRiskScore})
                        </Badge>
                    </div>
                </div>

                <PersonaToggle />
            </div>
        </div>
    );
}
