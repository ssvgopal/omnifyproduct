'use client';

import React, { createContext, useContext, useState } from 'react';

export type PersonaType = 'sarah' | 'jason' | 'emily';

interface PersonaContextType {
    persona: PersonaType;
    setPersona: (p: PersonaType) => void;
}

const PersonaContext = createContext<PersonaContextType | undefined>(undefined);

export function PersonaProvider({ children }: { children: React.ReactNode }) {
    const [persona, setPersona] = useState<PersonaType>('sarah');

    return (
        <PersonaContext.Provider value={{ persona, setPersona }}>
            {children}
        </PersonaContext.Provider>
    );
}

export function usePersona() {
    const context = useContext(PersonaContext);
    if (context === undefined) {
        throw new Error('usePersona must be used within a PersonaProvider');
    }
    return context;
}
