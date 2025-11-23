import fs from 'fs';
import path from 'path';
import { BrainState } from '@/lib/types';
import { TopBar } from '@/components/dashboard/TopBar';
import { MemoryCard } from '@/components/dashboard/MemoryCard';
import { OracleCard } from '@/components/dashboard/OracleCard';
import { CuriosityCard } from '@/components/dashboard/CuriosityCard';

// Force dynamic to ensure we read the latest JSON on refresh
export const dynamic = 'force-dynamic';

async function getBrainState(): Promise<BrainState> {
  const filePath = path.join(process.cwd(), 'src', 'data', 'outputs', 'brain-state.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents);
}

export default async function DashboardPage() {
  const brainState = await getBrainState();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <TopBar state={brainState} />

      <main className="flex-1 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-140px)]">
          {/* Column 1: MEMORY */}
          <div className="h-full">
            <MemoryCard data={brainState.memory} />
          </div>

          {/* Column 2: ORACLE */}
          <div className="h-full">
            <OracleCard data={brainState.oracle} />
          </div>

          {/* Column 3: CURIOSITY */}
          <div className="h-full">
            <CuriosityCard data={brainState.curiosity} />
          </div>
        </div>
      </main>
    </div>
  );
}
