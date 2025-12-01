/**
 * E2E Test Script - Omnify Brain
 * 
 * Tests the complete user journey:
 * 1. Health check
 * 2. Auth endpoints
 * 3. Brain cycle
 * 4. Dashboard data
 * 5. Integrations
 * 
 * Usage: npx tsx scripts/e2e-test.ts
 */

const BASE_URL = process.env.NEXTAUTH_URL || 'http://localhost:3000';

interface TestResult {
  name: string;
  passed: boolean;
  duration: number;
  error?: string;
}

const results: TestResult[] = [];

async function runTest(name: string, testFn: () => Promise<void>) {
  const start = Date.now();
  try {
    await testFn();
    results.push({ name, passed: true, duration: Date.now() - start });
    console.log(`  ✅ ${name} (${Date.now() - start}ms)`);
  } catch (error: any) {
    results.push({ name, passed: false, duration: Date.now() - start, error: error.message });
    console.log(`  ❌ ${name}: ${error.message}`);
  }
}

async function main() {
  console.log('');
  console.log('🧪 ═══════════════════════════════════════════════════════');
  console.log('   OMNIFY BRAIN E2E TEST SUITE');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`   Base URL: ${BASE_URL}`);
  console.log('');

  // 1. Health Check
  console.log('📋 1. HEALTH CHECKS');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Server is running', async () => {
    const response = await fetch(`${BASE_URL}/`);
    if (!response.ok && response.status !== 307) {
      throw new Error(`Server returned ${response.status}`);
    }
  });

  await runTest('API routes accessible', async () => {
    const response = await fetch(`${BASE_URL}/api/brain-state`);
    // Should return 200 or 401 (auth required)
    if (response.status !== 200 && response.status !== 401) {
      throw new Error(`API returned ${response.status}`);
    }
  });

  // 2. Auth Endpoints
  console.log('');
  console.log('🔐 2. AUTH ENDPOINTS');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Login page loads', async () => {
    const response = await fetch(`${BASE_URL}/login`);
    if (!response.ok) {
      throw new Error(`Login page returned ${response.status}`);
    }
  });

  await runTest('Signup page loads', async () => {
    const response = await fetch(`${BASE_URL}/signup`);
    if (!response.ok) {
      throw new Error(`Signup page returned ${response.status}`);
    }
  });

  await runTest('NextAuth endpoint exists', async () => {
    const response = await fetch(`${BASE_URL}/api/auth/providers`);
    if (!response.ok) {
      throw new Error(`Auth providers returned ${response.status}`);
    }
    const data = await response.json();
    if (!data.credentials) {
      throw new Error('Credentials provider not configured');
    }
  });

  // 3. Brain Cycle (with demo data)
  console.log('');
  console.log('🧠 3. BRAIN CYCLE');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Brain state endpoint returns data', async () => {
    const response = await fetch(`${BASE_URL}/api/brain-state`);
    if (response.status === 401) {
      console.log('    (Auth required - skipping data validation)');
      return;
    }
    if (!response.ok) {
      throw new Error(`Brain state returned ${response.status}`);
    }
    const data = await response.json();
    if (!data.memory && !data.oracle && !data.curiosity) {
      throw new Error('Brain state missing required fields');
    }
  });

  // 4. Dashboard
  console.log('');
  console.log('📊 4. DASHBOARD');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Dashboard V3 page loads', async () => {
    const response = await fetch(`${BASE_URL}/dashboard-v3`);
    // May redirect to login, which is fine
    if (response.status !== 200 && response.status !== 307) {
      throw new Error(`Dashboard returned ${response.status}`);
    }
  });

  await runTest('Onboarding page loads', async () => {
    const response = await fetch(`${BASE_URL}/onboarding`);
    if (response.status !== 200 && response.status !== 307) {
      throw new Error(`Onboarding returned ${response.status}`);
    }
  });

  // 5. Integrations
  console.log('');
  console.log('🔌 5. INTEGRATIONS');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Integrations settings page loads', async () => {
    const response = await fetch(`${BASE_URL}/settings/integrations`);
    if (response.status !== 200 && response.status !== 307) {
      throw new Error(`Settings returned ${response.status}`);
    }
  });

  await runTest('Meta connector auth endpoint exists', async () => {
    const response = await fetch(`${BASE_URL}/api/connectors/meta/auth`);
    // Should return 401 (auth required) or redirect
    if (response.status !== 401 && response.status !== 200) {
      throw new Error(`Meta auth returned ${response.status}`);
    }
  });

  await runTest('Google connector auth endpoint exists', async () => {
    const response = await fetch(`${BASE_URL}/api/connectors/google/auth`);
    if (response.status !== 401 && response.status !== 200) {
      throw new Error(`Google auth returned ${response.status}`);
    }
  });

  // 6. API Endpoints
  console.log('');
  console.log('🔗 6. API ENDPOINTS');
  console.log('─────────────────────────────────────────────────────────');

  await runTest('Integrations API exists', async () => {
    const response = await fetch(`${BASE_URL}/api/integrations`);
    if (response.status !== 401 && response.status !== 200) {
      throw new Error(`Integrations API returned ${response.status}`);
    }
  });

  await runTest('Actions execute API exists', async () => {
    const response = await fetch(`${BASE_URL}/api/actions/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    // Should return 400 (missing fields) or 401 (auth required)
    if (response.status !== 400 && response.status !== 401 && response.status !== 403) {
      throw new Error(`Actions API returned ${response.status}`);
    }
  });

  // Summary
  console.log('');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('   TEST SUMMARY');
  console.log('═══════════════════════════════════════════════════════════');

  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);

  console.log(`   Total: ${results.length} tests`);
  console.log(`   ✅ Passed: ${passed}`);
  console.log(`   ❌ Failed: ${failed}`);
  console.log(`   ⏱️  Duration: ${totalDuration}ms`);
  console.log('');

  if (failed > 0) {
    console.log('   FAILED TESTS:');
    results.filter(r => !r.passed).forEach(r => {
      console.log(`   - ${r.name}: ${r.error}`);
    });
    console.log('');
    process.exit(1);
  } else {
    console.log('   🎉 All tests passed!');
    console.log('');
  }
}

main().catch(console.error);
