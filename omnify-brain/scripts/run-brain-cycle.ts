/**
 * Brain Cycle Runner V3 - End-to-End Data Flow
 * 
 * Implements the complete data flow per Requirements V3:
 * Supabase/Seeds → MEMORY → ORACLE → CURIOSITY → FACE (brain_states)
 * 
 * Usage:
 *   npx ts-node scripts/run-brain-cycle.ts
 *   npx ts-node scripts/run-brain-cycle.ts --use-seeds  (use local seed files)
 *   npx ts-node scripts/run-brain-cycle.ts --org-id=<id>  (specific org)
 */

import fs from 'fs';
import path from 'path';
import { MemoryModuleV3 } from '../src/lib/brain/memory-v3';
import { OracleModuleV3 } from '../src/lib/brain/oracle-v3';
import { CuriosityModuleV3 } from '../src/lib/brain/curiosity-v3';
import { 
  ChannelData, 
  CreativeData, 
  DailyMetricExtended,
  CohortData,
  CreativeDailyMetric,
  BrainStateV3,
  MemoryOutputV3,
  OracleOutputV3,
  CuriosityOutputV3
} from '../src/lib/types';

// Configuration
const SEED_DIR = path.join(process.cwd(), 'src', 'data', 'seeds');
const OUTPUT_DIR = path.join(process.cwd(), 'src', 'data', 'outputs');
const DEFAULT_ORG_ID = 'org_demo_beauty_65m';

// Parse command line arguments
const args = process.argv.slice(2);
const useSeeds = args.includes('--use-seeds') || !process.env.SUPABASE_URL;
const orgIdArg = args.find(a => a.startsWith('--org-id='));
const organizationId = orgIdArg ? orgIdArg.split('=')[1] : DEFAULT_ORG_ID;

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Load data from local seed files
 */
async function loadDataFromSeeds(): Promise<{
  channels: ChannelData[];
  creatives: CreativeData[];
  dailyMetrics: DailyMetricExtended[];
  cohorts: CohortData[];
  creativeDailyMetrics: CreativeDailyMetric[];
}> {
  console.log('📂 Loading data from seed files...');

  const channels: ChannelData[] = JSON.parse(
    fs.readFileSync(path.join(SEED_DIR, 'channels.json'), 'utf-8')
  );
  const creatives: CreativeData[] = JSON.parse(
    fs.readFileSync(path.join(SEED_DIR, 'creatives.json'), 'utf-8')
  );
  const dailyMetrics: DailyMetricExtended[] = JSON.parse(
    fs.readFileSync(path.join(SEED_DIR, 'daily_metrics.json'), 'utf-8')
  );
  const cohorts: CohortData[] = JSON.parse(
    fs.readFileSync(path.join(SEED_DIR, 'cohorts.json'), 'utf-8')
  );
  const creativeDailyMetrics: CreativeDailyMetric[] = JSON.parse(
    fs.readFileSync(path.join(SEED_DIR, 'creative_daily_metrics.json'), 'utf-8')
  );

  console.log(`   ✓ Loaded ${channels.length} channels`);
  console.log(`   ✓ Loaded ${creatives.length} creatives`);
  console.log(`   ✓ Loaded ${dailyMetrics.length} daily metrics`);
  console.log(`   ✓ Loaded ${cohorts.length} cohorts`);
  console.log(`   ✓ Loaded ${creativeDailyMetrics.length} creative daily metrics`);

  return { channels, creatives, dailyMetrics, cohorts, creativeDailyMetrics };
}

/**
 * Load data from Supabase
 * TODO: Implement when Supabase is configured
 */
async function loadDataFromSupabase(orgId: string): Promise<{
  channels: ChannelData[];
  creatives: CreativeData[];
  dailyMetrics: DailyMetricExtended[];
  cohorts: CohortData[];
  creativeDailyMetrics: CreativeDailyMetric[];
}> {
  console.log(`📡 Loading data from Supabase for org: ${orgId}...`);
  
  // TODO: Implement Supabase data loading
  // const { data: channels } = await supabase
  //   .from('channels')
  //   .select('*')
  //   .eq('organization_id', orgId);
  
  throw new Error('Supabase loading not yet implemented. Use --use-seeds flag.');
}

/**
 * Save brain state to local file
 */
async function saveBrainStateLocal(
  organizationId: string,
  state: BrainStateV3
): Promise<void> {
  const filename = `brain-state-${organizationId}.json`;
  const filepath = path.join(OUTPUT_DIR, filename);
  
  fs.writeFileSync(filepath, JSON.stringify(state, null, 2));
  console.log(`💾 Brain state saved to: ${filepath}`);
}

/**
 * Save brain state to Supabase
 * TODO: Implement when Supabase is configured
 */
async function saveBrainStateSupabase(
  organizationId: string,
  state: BrainStateV3
): Promise<void> {
  console.log(`📡 Saving brain state to Supabase for org: ${organizationId}...`);
  
  // TODO: Implement Supabase saving
  // await supabase.from('brain_states').insert({
  //   organization_id: organizationId,
  //   memory_output: state.memory,
  //   oracle_output: state.oracle,
  //   curiosity_output: state.curiosity,
  //   computed_at: state.timestamp,
  // });
  
  throw new Error('Supabase saving not yet implemented.');
}

/**
 * Main brain cycle execution
 */
async function runBrainCycle(orgId: string): Promise<BrainStateV3> {
  console.log('');
  console.log('🧠 ═══════════════════════════════════════════════════════');
  console.log('   OMNIFY BRAIN CYCLE V3');
  console.log('   Requirements V3 Compliant Implementation');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('');

  const startTime = Date.now();

  // 1. Load Data
  console.log('📊 STEP 1: Loading Data');
  console.log('─────────────────────────────────────────────────────────');
  
  const data = useSeeds 
    ? await loadDataFromSeeds()
    : await loadDataFromSupabase(orgId);
  
  console.log('');

  // 2. Initialize Modules
  console.log('⚙️  STEP 2: Initializing Brain Modules');
  console.log('─────────────────────────────────────────────────────────');
  
  const memoryModule = new MemoryModuleV3();
  const oracleModule = new OracleModuleV3();
  const curiosityModule = new CuriosityModuleV3();
  
  console.log('   ✓ MEMORY Module V3 initialized');
  console.log('   ✓ ORACLE Module V3 initialized');
  console.log('   ✓ CURIOSITY Module V3 initialized');
  console.log('');

  // 3. Execute MEMORY
  console.log('🔵 STEP 3: Running MEMORY Module');
  console.log('─────────────────────────────────────────────────────────');
  
  const memoryOutput: MemoryOutputV3 = await memoryModule.process({
    dailyMetrics: data.dailyMetrics,
    channels: data.channels,
    cohorts: data.cohorts,
    organizationId: orgId,
  });
  
  console.log(`   ✓ Total Spend: $${memoryOutput.totals.totalSpend.toLocaleString()}`);
  console.log(`   ✓ Total Revenue: $${memoryOutput.totals.totalRevenue.toLocaleString()}`);
  console.log(`   ✓ Blended ROAS: ${memoryOutput.totals.blendedRoas}x`);
  console.log(`   ✓ LTV-ROAS: ${memoryOutput.totals.ltvRoas}x`);
  console.log(`   ✓ LTV Factor: ${memoryOutput.ltvFactor} (${memoryOutput.baselineCohortMonth} → ${memoryOutput.recentCohortMonth})`);
  console.log(`   ✓ Channels: ${memoryOutput.channels.map(c => `${c.name}(${c.status})`).join(', ')}`);
  console.log('');

  // 4. Execute ORACLE
  console.log('🟠 STEP 4: Running ORACLE Module');
  console.log('─────────────────────────────────────────────────────────');
  
  const oracleOutput: OracleOutputV3 = await oracleModule.process({
    dailyMetrics: data.dailyMetrics,
    creatives: data.creatives,
    creativeDailyMetrics: data.creativeDailyMetrics,
    cohorts: data.cohorts,
    channels: data.channels,
    memory: memoryOutput,
  });
  
  console.log(`   ✓ Global Risk Level: ${oracleOutput.globalRiskLevel.toUpperCase()}`);
  console.log(`   ✓ Global Risk Score: ${oracleOutput.globalRiskScore}/100`);
  console.log(`   ✓ Creative Fatigue Alerts: ${oracleOutput.creativeFatigue.length}`);
  if (oracleOutput.creativeFatigue.length > 0) {
    oracleOutput.creativeFatigue.forEach(f => {
      console.log(`      - ${f.creativeName}: ${(f.fatigueProbability7d * 100).toFixed(0)}% fatigue probability`);
    });
  }
  console.log(`   ✓ ROI Decay Alerts: ${oracleOutput.roiDecay.length}`);
  if (oracleOutput.roiDecay.length > 0) {
    oracleOutput.roiDecay.forEach(d => {
      console.log(`      - ${d.channelName}: ${d.decayPercentage}% decay (${d.decaySeverity})`);
    });
  }
  console.log(`   ✓ LTV Drift: ${oracleOutput.ltvDrift ? `${oracleOutput.ltvDrift.driftPercentage}% (${oracleOutput.ltvDrift.driftSeverity})` : 'None detected'}`);
  console.log('');

  // 5. Execute CURIOSITY
  console.log('🟣 STEP 5: Running CURIOSITY Module');
  console.log('─────────────────────────────────────────────────────────');
  
  const curiosityOutput: CuriosityOutputV3 = await curiosityModule.process({
    memory: memoryOutput,
    oracle: oracleOutput,
  });
  
  console.log(`   ✓ Total Opportunity: ${curiosityOutput.totalOpportunityFormatted}`);
  console.log(`   ✓ Top 3 Actions:`);
  curiosityOutput.topActions.forEach((action, i) => {
    console.log(`      ${i + 1}. [${action.type}] ${action.title}`);
    console.log(`         Impact: ${action.impactFormatted} | Confidence: ${action.confidence} | Urgency: ${action.urgency}`);
    console.log(`         Score: ${action.score.toFixed(2)}`);
  });
  console.log('');

  // 6. Assemble Brain State
  const brainState: BrainStateV3 = {
    timestamp: new Date().toISOString(),
    organizationId: orgId,
    memory: memoryOutput,
    oracle: oracleOutput,
    curiosity: curiosityOutput,
  };

  // 7. Save Brain State
  console.log('💾 STEP 6: Saving Brain State');
  console.log('─────────────────────────────────────────────────────────');
  
  await saveBrainStateLocal(orgId, brainState);
  
  // Also save to Supabase if configured
  if (!useSeeds && process.env.SUPABASE_URL) {
    try {
      await saveBrainStateSupabase(orgId, brainState);
    } catch (error) {
      console.log('   ⚠️  Supabase save skipped (not configured)');
    }
  }
  console.log('');

  // 8. Summary
  const duration = Date.now() - startTime;
  console.log('═══════════════════════════════════════════════════════════');
  console.log('✅ BRAIN CYCLE COMPLETE');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`   Duration: ${duration}ms`);
  console.log(`   Organization: ${orgId}`);
  console.log(`   Data Source: ${useSeeds ? 'Local Seeds' : 'Supabase'}`);
  console.log('');
  console.log('📋 EXECUTIVE SUMMARY:');
  console.log(`   • Blended ROAS: ${memoryOutput.totals.blendedRoas}x`);
  console.log(`   • LTV-ROAS: ${memoryOutput.totals.ltvRoas}x`);
  console.log(`   • Risk Level: ${oracleOutput.globalRiskLevel.toUpperCase()}`);
  console.log(`   • Top Action: ${curiosityOutput.topActions[0]?.title || 'None'}`);
  console.log(`   • Total Opportunity: ${curiosityOutput.totalOpportunityFormatted}`);
  console.log('');

  return brainState;
}

// Execute
runBrainCycle(organizationId)
  .then(() => {
    console.log('🎯 Brain cycle completed successfully!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Brain cycle failed:', error);
    process.exit(1);
  });
