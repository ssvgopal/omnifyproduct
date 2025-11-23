# Omnify AI Marketing Brain - MVP Demo

> **🎯 Self-Contained Demo Implementation**  
> This is a **no-dependency demo** showcasing the Omnify Brain architecture without requiring API keys, databases, or external services.

## What This Is

A **fully functional prototype** of the Omnify AI Marketing Brain that demonstrates:
- **MEMORY Module**: Attribution & ROI analysis
- **ORACLE Module**: Predictive risk detection (Creative Fatigue, ROI Decay, LTV Drift)
- **CURIOSITY Module**: Prescriptive action recommendations
- **FACE Dashboard**: Single intelligence surface with persona-specific views

## Key Features

✅ **Zero External Dependencies**  
✅ **No API Keys Required**  
✅ **No Database Setup**  
✅ **Static JSON Data Simulation**  
✅ **TypeScript Brain Modules**  
✅ **Persona Toggle** (CMO / VP Growth / Director)  
✅ **Production-Ready UI** (Next.js 15 + shadcn/ui)

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Generate demo data (simulates a Beauty Brand scenario)
npx tsx scripts/seed-demo.ts

# 3. Run the Brain Cycle (processes data through modules)
npx tsx scripts/run-brain.ts

# 4. Start the dashboard
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Demo Scenario

The seed data simulates a **Beauty & Skincare DTC brand** with:
- **Meta Ads**: High performer (WINNER - Green)
- **TikTok Ads**: Declining efficiency (LOSER - Red)
- **Creative C12**: Showing fatigue signs
- **30 days** of performance data

## Architecture

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with PersonaProvider
│   └── page.tsx           # Main Dashboard
├── components/
│   ├── ui/                # shadcn/ui primitives
│   ├── dashboard/         # Feature components
│   │   ├── TopBar.tsx
│   │   ├── MemoryCard.tsx
│   │   ├── OracleCard.tsx
│   │   └── CuriosityCard.tsx
│   └── PersonaToggle.tsx
├── lib/
│   ├── brain/             # Brain Logic Modules
│   │   ├── memory.ts      # Attribution logic
│   │   ├── oracle.ts      # Prediction logic
│   │   └── curiosity.ts   # Recommendation logic
│   ├── types.ts           # TypeScript interfaces
│   └── persona-context.tsx
└── data/
    ├── seeds/             # Generated demo data
    └── outputs/           # Brain state JSON
```

## What's Next?

This MVP demonstrates the **concept and architecture**. For production:
- **Real API Integrations**: Meta, Google, TikTok, Shopify
- **Database**: Supabase for persistent storage
- **AI/ML**: OpenAI/Anthropic for advanced insights
- **Authentication**: User management
- **Webhooks**: Real-time data ingestion

See `PRODUCTION_ROADMAP.md` for the full implementation plan.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (Strict)
- **UI**: TailwindCSS + shadcn/ui
- **Icons**: Lucide React
- **Build**: Turbopack

## License

Proprietary - Omnify AI
