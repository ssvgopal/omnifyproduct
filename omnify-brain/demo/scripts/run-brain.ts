import fs from 'fs';
import path from 'path';
import { MemoryModule } from '../src/lib/brain/memory';
import { OracleModule } from '../src/lib/brain/oracle';
import { CuriosityModule } from '../src/lib/brain/curiosity';
import { BrainState, ChannelData, DailyMetric, CreativeData } from '../src/lib/types';

// Paths
const SEED_DIR = path.join(process.cwd(), 'src', 'data', 'seeds');
const OUTPUT_DIR = path.join(process.cwd(), 'src', 'data', 'outputs');

// Ensure output dir exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function runBrain() {
    console.log('🧠 Starting Omnify Brain Cycle...');

    // 1. Load Data
    const channels: ChannelData[] = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'channels.json'), 'utf-8'));
    const dailyMetrics: DailyMetric[] = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'daily_metrics.json'), 'utf-8'));
    const creatives: CreativeData[] = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'creatives.json'), 'utf-8'));

    // 2. Initialize Modules
    const memory = new MemoryModule();
    const oracle = new OracleModule();
    const curiosity = new CuriosityModule();

    // 3. Execute Pipeline
    console.log('Running MEMORY...');
    const memoryOutput = await memory.process({ dailyMetrics, channels });

    console.log('Running ORACLE...');
    const oracleOutput = await oracle.process({ dailyMetrics, creatives });

    console.log('Running CURIOSITY...');
    const curiosityOutput = await curiosity.process({ memory: memoryOutput, oracle: oracleOutput });

    // 4. Save State
    const state: BrainState = {
        timestamp: new Date().toISOString(),
        memory: memoryOutput,
        oracle: oracleOutput,
        curiosity: curiosityOutput
    };

    fs.writeFileSync(path.join(OUTPUT_DIR, 'brain-state.json'), JSON.stringify(state, null, 2));
    console.log('✅ Brain Cycle Complete. State saved to src/data/outputs/brain-state.json');
}

runBrain().catch(console.error);
