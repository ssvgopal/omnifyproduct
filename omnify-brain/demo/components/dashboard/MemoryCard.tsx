'use client';

import { MemoryOutput } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { usePersona } from '@/lib/persona-context';
import { Brain } from 'lucide-react';

interface MemoryCardProps {
    data: MemoryOutput;
}

export function MemoryCard({ data }: MemoryCardProps) {
    const { persona } = usePersona();

    const titles = {
        sarah: "Attribution Truth",
        jason: "Channel Performance",
        emily: "Daily ROAS Tracker"
    };

    const descriptions = {
        sarah: "Unified view of spend efficiency across all platforms.",
        jason: "Real-time ROAS vs Targets analysis.",
        emily: "Monitor channel health and budget pacing."
    };

    return (
        <Card className="h-full border-l-4 border-l-blue-500">
            <CardHeader>
                <div className="flex items-center gap-2 text-blue-600 mb-2">
                    <Brain className="h-5 w-5" />
                    <span className="text-sm font-bold tracking-wider uppercase">Memory</span>
                </div>
                <CardTitle>{titles[persona]}</CardTitle>
                <CardDescription>{descriptions[persona]}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    <div className="flex justify-between items-end">
                        <div>
                            <p className="text-sm text-muted-foreground">Total Spend (30d)</p>
                            <p className="text-2xl font-bold">${data.totalSpend.toLocaleString()}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-muted-foreground">Blended ROAS</p>
                            <p className="text-2xl font-bold text-blue-600">{data.blendedRoas.toFixed(2)}x</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {data.channels.map(channel => (
                            <div key={channel.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${channel.status === 'winner' ? 'bg-green-500' :
                                            channel.status === 'loser' ? 'bg-red-500' : 'bg-yellow-500'
                                        }`} />
                                    <div>
                                        <p className="font-medium">{channel.name}</p>
                                        <p className="text-xs text-muted-foreground">{channel.contribution.toFixed(0)}% Contrib.</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-bold">{channel.roas.toFixed(2)}x</p>
                                    <Badge variant={channel.status === 'winner' ? 'default' : channel.status === 'loser' ? 'destructive' : 'secondary'} className="text-[10px] h-5">
                                        {channel.status.toUpperCase()}
                                    </Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
