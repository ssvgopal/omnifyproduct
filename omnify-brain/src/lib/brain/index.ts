/**
 * Brain Modules Index
 * 
 * Exports both legacy (V1) and new (V3) brain modules.
 * V3 modules are Requirements V3 compliant.
 */

// Legacy modules (V1)
export { MemoryModule } from './memory';
export { OracleModule } from './oracle';
export { CuriosityModule } from './curiosity';

// Production modules (existing)
export * from './memory-production';
export * from './oracle-production';
export * from './curiosity-production';

// V3 modules (Requirements V3 compliant)
export { MemoryModuleV3, memoryModuleV3 } from './memory-v3';
export { OracleModuleV3, oracleModuleV3 } from './oracle-v3';
export { CuriosityModuleV3, curiosityModuleV3 } from './curiosity-v3';

// Re-export input types
export type { MemoryInputV3 } from './memory-v3';
export type { OracleInputV3 } from './oracle-v3';
export type { CuriosityInputV3 } from './curiosity-v3';
