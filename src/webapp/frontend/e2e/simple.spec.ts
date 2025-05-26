/**
 * Simple E2E test for debugging setup.
 */

import { test, expect } from '@playwright/test';

test.describe('Simple Setup Test', () => {
  test('can load the homepage', async ({ page }) => {
    // Navigate to the homepage
    await page.goto('/');
    
    // Wait for any content to load
    await page.waitForTimeout(2000);
    
    // Check if we can find basic HTML elements
    const html = await page.locator('html').isVisible();
    expect(html).toBe(true);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-results/homepage.png' });
    
    console.log('Page title:', await page.title());
    console.log('Page URL:', page.url());
  });

  test('mock server is working', async ({ page }) => {
    // Test if we can access the mock API directly
    const response = await page.request.get('http://localhost:8000/health');
    expect(response.ok()).toBe(true);
    
    const health = await response.json();
    expect(health).toHaveProperty('status');
    console.log('Health response:', health);
  });
}); 