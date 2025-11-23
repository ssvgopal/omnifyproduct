import { MemoryModuleProduction } from '../brain/memory-production';
import { OracleModuleProduction } from '../brain/oracle-production';
import { CuriosityModuleProduction } from '../brain/curiosity-production';
import { supabaseAdmin } from '../db/supabase';
import { getLatestBrainState } from '../db/queries';
import { BrainState } from '../types';

export class BrainService {
  /**
   * Compute brain state for an organization
   */
  async computeBrainState(organizationId: string): Promise<BrainState> {
    console.log(`[BRAIN] Computing state for org: ${organizationId}`);

    try {
      // Initialize modules
      const memory = new MemoryModuleProduction();
      const oracle = new OracleModuleProduction();
      const curiosity = new CuriosityModuleProduction();

      // Run brain cycle
      const memoryOutput = await memory.process({ organizationId });
      const oracleOutput = await oracle.process({ organizationId });
      const curiosityOutput = await curiosity.process({
        memory: memoryOutput,
        oracle: oracleOutput,
      });

      const brainState: BrainState = {
        timestamp: new Date().toISOString(),
        memory: memoryOutput,
        oracle: oracleOutput,
        curiosity: curiosityOutput,
      };

      // Cache result in database
      const { error } = await supabaseAdmin.from('brain_states').insert({
        organization_id: organizationId,
        memory_output: memoryOutput,
        oracle_output: oracleOutput,
        curiosity_output: curiosityOutput,
        computed_at: brainState.timestamp,
      });

      if (error) {
        console.error('[BRAIN] Error caching state:', error);
        // Don't throw - we still have the computed state
      }

      console.log(`[BRAIN] State computed successfully`);
      return brainState;
    } catch (error: any) {
      console.error('[BRAIN] Error computing state:', error);
      throw new Error(`Brain computation failed: ${error.message}`);
    }
  }

  /**
   * Get latest brain state (cached or compute new)
   */
  async getBrainState(organizationId: string, maxAgeMinutes = 60): Promise<BrainState> {
    // Try to get cached state
    const cached = await getLatestBrainState(organizationId);

    if (cached) {
      const age = Date.now() - new Date(cached.computed_at).getTime();
      const maxAge = maxAgeMinutes * 60 * 1000;

      if (age < maxAge) {
        console.log(`[BRAIN] Using cached state (${Math.round(age / 60000)} minutes old)`);
        return {
          timestamp: cached.computed_at,
          memory: cached.memory_output,
          oracle: cached.oracle_output,
          curiosity: cached.curiosity_output,
        };
      }
    }

    // Compute new state
    console.log('[BRAIN] Cache miss or stale - computing new state');
    return this.computeBrainState(organizationId);
  }
}
