/**
 * Global setup for Playwright E2E tests.
 * 
 * This file sets up the mock server before running tests and tears it down afterwards.
 */

import { startMockServer, stopMockServer } from './mock-server';

async function globalSetup() {
  console.log('🚀 Starting global setup for E2E tests...');
  
  // Start the mock server
  startMockServer();
  
  console.log('✅ Global setup completed');
}

async function globalTeardown() {
  console.log('🧹 Starting global teardown for E2E tests...');
  
  // Stop the mock server
  stopMockServer();
  
  console.log('✅ Global teardown completed');
}

export default globalSetup;
export { globalTeardown }; 