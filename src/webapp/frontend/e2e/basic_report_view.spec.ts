/**
 * E2E test for basic report view functionality.
 * 
 * Tests the complete user journey from scan list to report details,
 * including navigation, API mocking, and content validation.
 */

import { test, expect } from '@playwright/test';

test.describe('Basic Report View E2E', () => {
  // API mocking is handled by global mock server setup
  // No need to mock in individual tests

  test('complete report view flow - navigate from scan list to report details', async ({ page }) => {
    // Step 1: Navigate to the root page (/)
    await page.goto('/');

    // Step 2: Assert the scan list is displayed
    await expect(page.locator('h1')).toContainText('Code Review Scans');
    
    // Wait for scans to load and verify scan list content
    await expect(page.locator('[data-testid="scan-list-item"]').first()).toBeVisible();
    
    // Verify that scan data is displayed
    await expect(page.locator('text=demo_scan_001')).toBeVisible();
    await expect(page.locator('text=user/test-repo')).toBeVisible();
    await expect(page.locator('text=COMPLETED')).toBeVisible();
    await expect(page.locator('text=PR')).toBeVisible();
    
    // Verify scan statistics
    await expect(page.locator('text=5')).toBeVisible(); // total findings
    
    // Step 3: Click on a scan link
    await page.locator('text=demo_scan_001').click();

    // Step 4: Assert the report details page is loaded
    await expect(page.locator('h1')).toContainText('Scan Report: demo_scan_001');
    
    // Verify basic report information
    await expect(page.locator('text=user/test-repo')).toBeVisible();
    await expect(page.locator('text=Back to Scans')).toBeVisible();
    
    // Verify tabs are present
    await expect(page.locator('text=Overview')).toBeVisible();
    await expect(page.locator('text=Findings (2)')).toBeVisible();
    await expect(page.locator('text=LLM Insights (2)')).toBeVisible();
    await expect(page.locator('text=Diagrams (1)')).toBeVisible();

    // Step 5: Assert that findings are rendered
    // Click on Findings tab
    await page.locator('text=Findings (2)').click();
    
    // Verify findings content
    await expect(page.locator('text=Hardcoded API key detected')).toBeVisible();
    await expect(page.locator('text=Inefficient nested loop detected')).toBeVisible();
    
    // Verify severity levels
    await expect(page.locator('text=CRITICAL')).toBeVisible();
    await expect(page.locator('text=HIGH')).toBeVisible();
    
    // Verify code snippets are displayed
    await expect(page.locator('text=API_KEY = "sk-1234567890abcdef"')).toBeVisible();
    
    // Verify suggestions are displayed
    await expect(page.locator('text=Store sensitive data in environment variables')).toBeVisible();

    // Step 6: Assert that LLM insights are rendered
    // Click on LLM Insights tab
    await page.locator('text=LLM Insights (2)').click();
    
    // Verify LLM analysis content
    await expect(page.locator('text=Security Analysis')).toBeVisible();
    await expect(page.locator('text=Code Quality')).toBeVisible();
    
    // Verify confidence scores and model information
    await expect(page.locator('text=Confidence: 85%')).toBeVisible();
    await expect(page.locator('text=Model: gpt-4')).toBeVisible();
    
    // Verify LLM recommendations
    await expect(page.locator('text=Use environment variables for sensitive data')).toBeVisible();

    // Step 7: Assert that diagrams are rendered (or placeholder)
    // Click on Diagrams tab
    await page.locator('text=Diagrams (1)').click();
    
    // Verify diagram is displayed
    await expect(page.locator('text=Class Diagram')).toBeVisible();
    
    // Verify diagram component or placeholder is present
    // The actual diagram rendering might be async, so we check for the container
    await expect(page.locator('[data-testid="diagram-display"]')).toBeVisible();
  });

  test('scan list displays correct information and navigation works', async ({ page }) => {
    await page.goto('/');

    // Verify page title and header
    await expect(page.locator('h1')).toContainText('Code Review Scans');
    
    // Verify New Scan button is present
    await expect(page.locator('text=New Scan')).toBeVisible();
    
    // Verify scan list table headers
    await expect(page.locator('text=Scan ID')).toBeVisible();
    await expect(page.locator('text=Repository')).toBeVisible();
    await expect(page.locator('text=Type')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Findings')).toBeVisible();
    await expect(page.locator('text=Created')).toBeVisible();
    await expect(page.locator('text=Actions')).toBeVisible();
    
    // Verify multiple scans are displayed
    await expect(page.locator('text=demo_scan_001')).toBeVisible();
    await expect(page.locator('text=project_scan_002')).toBeVisible();
    await expect(page.locator('text=pr_scan_003')).toBeVisible();
    
    // Verify different scan types
    await expect(page.locator('text=PR')).toBeVisible();
    await expect(page.locator('text=PROJECT')).toBeVisible();
    
    // Verify different statuses
    await expect(page.locator('text=COMPLETED')).toBeVisible();
    await expect(page.locator('text=RUNNING')).toBeVisible();
    await expect(page.locator('text=FAILED')).toBeVisible();
    
    // Verify action buttons
    await expect(page.locator('text=View').first()).toBeVisible();
    await expect(page.locator('text=Delete').first()).toBeVisible();
  });

  test('report tabs functionality works correctly', async ({ page }) => {
    // Navigate directly to a report
    await page.goto('/reports/demo_scan_001');
    
    // Wait for report to load
    await expect(page.locator('h1')).toContainText('Scan Report: demo_scan_001');
    
    // Test Overview tab (default)
    await expect(page.locator('text=Scan Summary')).toBeVisible();
    await expect(page.locator('text=Scan Information')).toBeVisible();
    
    // Test switching to Findings tab
    await page.locator('text=Findings (2)').click();
    await expect(page.locator('text=Filter by severity:')).toBeVisible();
    
    // Test switching to LLM Insights tab
    await page.locator('text=LLM Insights (2)').click();
    await expect(page.locator('text=Security Analysis')).toBeVisible();
    
    // Test switching to Diagrams tab
    await page.locator('text=Diagrams (1)').click();
    await expect(page.locator('text=Class Diagram')).toBeVisible();
    
    // Test switching back to Overview tab
    await page.locator('text=Overview').click();
    await expect(page.locator('text=Scan Summary')).toBeVisible();
  });

  test('error handling works for non-existent scan', async ({ page }) => {
    // Mock error response for non-existent scan
    await page.route('**/scans/nonexistent/report', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Scan not found' }),
      });
    });
    
    // Navigate to non-existent scan
    await page.goto('/reports/nonexistent');
    
    // Verify error message is displayed
    await expect(page.locator('text=Error loading report:')).toBeVisible();
    await expect(page.locator('text=Scan not found')).toBeVisible();
    
    // Verify retry and back buttons are present
    await expect(page.locator('text=Retry')).toBeVisible();
    await expect(page.locator('text=Back to Scans')).toBeVisible();
  });
}); 