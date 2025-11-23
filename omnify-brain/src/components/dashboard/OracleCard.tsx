'use client';

import { OracleOutput } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { usePersona } from '@/lib/persona-context';
import { AlertTriangle, TrendingDown, Zap } from 'lucide-react';

interface OracleCardProps {
    data: OracleOutput;
}

export function OracleCard({ data }: OracleCardProps) {
    const { persona } = usePersona();

    const titles = {
        sarah: "Risk Forecast",
        jason: "Predictive Alerts",
        emily: "Fatigue & Decay Warnings"
    };

    const descriptions = {
        sarah: "Forward-looking risks impacting next month's P&L.",
        jason: "7-14 day early warning system for performance drift.",
        emily: "Urgent issues requiring immediate attention."
    };

    return (
        <Card className="h-full border-l-4 border-l-orange-500">
            <CardHeader>
                <div className="flex items-center gap-2 text-orange-600 mb-2">
                    <Zap className="h-5 w-5" />
                    <span className="text-sm font-bold tracking-wider uppercase">Oracle</span>
                </div>
                <CardTitle>{titles[persona]}</CardTitle>
                <CardDescription>{descriptions[persona]}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-100">
                        <div>
                            <p className="text-sm font-medium text-orange-800">Global Risk Score</p>
                            <p className="text-xs text-orange-600">Lower is better</p>
                        </div>
                        <div className="text-3xl font-bold text-orange-600">{100 - data.globalRiskScore}</div>
                    </div>

                    <div className="space-y-3">
                        {data.risks.map(risk => (
                            <div key={risk.id} className="flex gap-3 p-3 border rounded-lg bg-white shadow-sm">
                                <div className="mt-1">
                                    {risk.type === 'creative_fatigue' ? <TrendingDown className="h-5 w-5 text-red-500" /> :
                                        risk.type === 'roi_decay' ? <AlertTriangle className="h-5 w-5 text-orange-500" /> :
                                            <AlertTriangle className="h-5 w-5 text-yellow-500" />}
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-semibold text-sm">
                                            {risk.type === 'creative_fatigue' ? 'Creative Fatigue' :
                                                risk.type === 'roi_decay' ? 'ROI Decay' : 'LTV Drift'}
                                        </span>
                                        <Badge variant="outline" className="text-[10px] h-5">
                                            {risk.predictionDays ? `In ${risk.predictionDays} days` : 'Now'}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground leading-tight">{risk.message}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
