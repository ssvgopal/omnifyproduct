'use client';

import { usePersona, PersonaType } from '@/lib/persona-context';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function PersonaToggle() {
    const { persona, setPersona } = usePersona();

    return (
        <Tabs value={persona} onValueChange={(v) => setPersona(v as PersonaType)} className="w-[400px]">
            <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="sarah">Sarah (CMO)</TabsTrigger>
                <TabsTrigger value="jason">Jason (VP)</TabsTrigger>
                <TabsTrigger value="emily">Emily (Dir)</TabsTrigger>
            </TabsList>
        </Tabs>
    );
}
