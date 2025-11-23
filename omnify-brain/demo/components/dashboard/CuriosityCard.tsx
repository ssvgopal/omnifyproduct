'use client';

import { CuriosityOutput } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { usePersona } from '@/lib/persona-context';
import { Lightbulb, ArrowRight, DollarSign } from 'lucide-react';

interface CuriosityCardProps {
    data: CuriosityOutput;
}

export function CuriosityCard({ data }: CuriosityCardProps) {
    const { persona } = usePersona();

    const titles = {
        sarah: "Strategic Moves",
        jason: "Growth Opportunities",
        emily: "Recommended Actions"
    };

    const descriptions = {
        sarah: "High-impact decisions to optimize profitability.",
        jason: "Tactical budget shifts to maximize efficiency.",
        emily: "Execute these changes to fix issues."
    };

    return (
        <Card className="h-full border-l-4 border-l-purple-500">
            <CardHeader>
                <div className="flex items-center gap-2 text-purple-600 mb-2">
                    <Lightbulb className="h-5 w-5" />
                    <span className="text-sm font-bold tracking-wider uppercase">Curiosity</span>
                </div>
                <CardTitle>{titles[persona]}</CardTitle>
                <CardDescription>{descriptions[persona]}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-100">
                        <div>
                            <p className="text-sm font-medium text-purple-800">Total Opportunity</p>
                            <p className="text-xs text-purple-600">Weekly Impact</p>
                        </div>
                        <div className="text-2xl font-bold text-purple-600">{data.totalOpportunity}</div>
                    </div>

                    <div className="space-y-4">
                        {data.topActions.map((action, index) => (
                            <div key={action.id} className="relative p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                                <div className="absolute -top-3 -left-3 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                                    {index + 1}
                                </div>

                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-semibold text-sm">{action.title}</h4>
                                    <Badge variant="secondary" className="bg-green-100 text-green-800 hover:bg-green-100">
                                        {action.impact}
                                    </Badge>
                                </div>

                                <p className="text-sm text-muted-foreground mb-3">{action.description}</p>

                                <div className="flex items-center justify-between">
                                    <div className="flex gap-2">
                                        <Badge variant="outline" className="text-[10px]">
                                            {action.confidence.toUpperCase()} Confidence
                                        </Badge>
                                        <Badge variant="outline" className="text-[10px]">
                                            {action.urgency.toUpperCase()} Urgency
                                        </Badge>
                                    </div>
                                    <Button size="sm" variant="ghost" className="h-8 text-purple-600 hover:text-purple-700 hover:bg-purple-50 p-0">
                                        Apply <ArrowRight className="ml-1 h-3 w-3" />
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
