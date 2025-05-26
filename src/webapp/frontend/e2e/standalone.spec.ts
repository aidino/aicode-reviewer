/**
 * Standalone E2E test that sets up its own mocking.
 */

import { test, expect } from '@playwright/test';

test.describe('Standalone Report View Test', () => {
  test('basic functionality without global setup', async ({ page }) => {
    // Mock API endpoints directly in the test
    await page.route('**/scans*', async (route) => {
      const mockScans = [
        {
          scan_id: 'demo_scan_001',
          scan_type: 'pr',
          repository: 'user/test-repo',
          status: 'completed',
          created_at: '2025-01-28T10:00:00Z',
          total_findings: 5,
          pr_id: 123,
        },
      ];
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockScans),
      });
    });

    await page.route('**/scans/demo_scan_001/report', async (route) => {
      const mockReport = {
        scan_info: {
          scan_id: 'demo_scan_001',
          scan_type: 'pr',
          repository: 'user/test-repo',
          created_at: '2025-01-28T10:00:00Z',
        },
        summary: {
          total_findings: 5,
          critical_count: 1,
          high_count: 2,
          medium_count: 1,
          low_count: 1,
        },
        static_analysis_findings: [
          {
            id: 'finding_1',
            rule_id: 'security.hardcoded_secret',
            severity: 'critical',
            category: 'Security',
            message: 'Hardcoded API key detected',
            file_path: 'src/config.py',
            line_number: 15,
          },
        ],
        llm_analysis: [
          {
            section: 'Security Analysis',
            content: 'Security issues found',
            confidence_score: 0.85,
            model_used: 'gpt-4',
          },
        ],
        diagrams: [
          {
            diagram_type: 'Class Diagram',
            diagram_content: '@startuml\nclass User\n@enduml',
            format: 'plantuml',
          },
        ],
        metadata: {
          total_files_analyzed: 25,
          languages_detected: ['Python'],
          analysis_duration_seconds: 300,
        },
      };
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockReport),
      });
    });

    // Try to navigate to the root page
    try {
      await page.goto('/');
      
      // Wait a bit for the page to load
      await page.waitForTimeout(3000);
      
      // Log what we can see
      const bodyText = await page.locator('body').textContent();
      console.log('Page body text:', bodyText?.substring(0, 200));
      
      // Take a screenshot for debugging
      await page.screenshot({ path: 'test-results/standalone-homepage.png', fullPage: true });
      
      // Look for any text that might be there
      const hasText = await page.locator('text=Code Review').isVisible({ timeout: 1000 }).catch(() => false);
      console.log('Found "Code Review" text:', hasText);
      
    } catch (error) {
      console.log('Error navigating to page:', error);
      throw error;
    }
  });
}); 