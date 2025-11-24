import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { MemoryModuleProduction } from '@/lib/brain/memory-production';
import { OracleModuleProduction } from '@/lib/brain/oracle-production';
import { CuriosityModuleProduction } from '@/lib/brain/curiosity-production';

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser();
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Step 1: Run MEMORY
    const memoryModule = new MemoryModuleProduction();
    const memoryOutput = await memoryModule.process({ organizationId: user.organizationId });

    // Step 2: Run ORACLE
    const oracleModule = new OracleModuleProduction();
    const oracleOutput = await oracleModule.process({ organizationId: user.organizationId });

    // Step 3: Run CURIOSITY
    const curiosityModule = new CuriosityModuleProduction();
    const curiosityOutput = await curiosityModule.process({
      memory: memoryOutput,
      oracle: oracleOutput,
    });

    // Step 4: Store brain state
    const { error: stateError } = await supabaseAdmin
      .from('brain_states')
      .insert({
        organization_id: user.organizationId,
        memory_output: memoryOutput,
        oracle_output: oracleOutput,
        curiosity_output: curiosityOutput,
        computed_at: new Date().toISOString(),
      });

    if (stateError) {
      console.error('[BRAIN CYCLE] Error storing brain state:', stateError);
      // Continue even if storage fails
    }

    return NextResponse.json({
      success: true,
      memory: memoryOutput,
      oracle: oracleOutput,
      curiosity: curiosityOutput,
    });
  } catch (error: any) {
    console.error('[BRAIN CYCLE] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Brain cycle failed' },
      { status: 500 }
    );
  }
}
