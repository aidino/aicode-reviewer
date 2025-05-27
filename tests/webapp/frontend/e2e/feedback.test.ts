/**
 * End-to-end tests for user feedback functionality.
 * 
 * Tests the complete feedback workflow from UI interaction to API submission
 * for scan findings, LLM insights, and diagrams.
 */

import { test, expect } from '@playwright/test';

test.describe('Feedback Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a report page with mock data
    await page.goto('/reports/demo_report_001');
    
    // Wait for the page to load
    await expect(page.locator('h1')).toContainText('Scan Report');
  });

  test.describe('Quick Feedback', () => {
    test('should show feedback buttons for findings', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Wait for findings to load
      await expect(page.locator('.feedback-button')).toHaveCount(5, { timeout: 5000 });
      
      // Check that feedback buttons exist for each finding
      const feedbackButtons = page.locator('.feedback-button');
      await expect(feedbackButtons.first()).toBeVisible();
      
      // Verify feedback button text
      await expect(feedbackButtons.first().locator('text=Was this helpful?')).toBeVisible();
      await expect(feedbackButtons.first().locator('button:has-text("👍 Helpful")')).toBeVisible();
      await expect(feedbackButtons.first().locator('button:has-text("👎 Not Helpful")')).toBeVisible();
    });

    test('should submit positive feedback for finding', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Mock the feedback API response
      await page.route('/api/feedback/', (route) => {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Click helpful button on first finding
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await firstFeedbackButton.locator('button:has-text("👍 Helpful")').click();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });

    test('should submit negative feedback for finding', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Mock the feedback API response
      await page.route('/api/feedback/', (route) => {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_456',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Click not helpful button on first finding
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await firstFeedbackButton.locator('button:has-text("👎 Not Helpful")').click();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });

    test('should handle feedback API error gracefully', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Mock API error response
      await page.route('/api/feedback/', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Internal server error'
          })
        });
      });
      
      // Click helpful button on first finding
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await firstFeedbackButton.locator('button:has-text("👍 Helpful")').click();
      
      // Verify error message appears
      await expect(firstFeedbackButton.locator('text=Error submitting feedback')).toBeVisible();
    });
  });

  test.describe('Detailed Feedback Form', () => {
    test('should open and close detailed feedback form', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      const firstFeedbackButton = page.locator('.feedback-button').first();
      
      // Click detailed feedback button
      await firstFeedbackButton.locator('button:has-text("📝 Detailed feedback")').click();
      
      // Verify form is visible
      await expect(firstFeedbackButton.locator('text=Provide Detailed Feedback')).toBeVisible();
      await expect(firstFeedbackButton.locator('select')).toBeVisible();
      await expect(firstFeedbackButton.locator('textarea')).toBeVisible();
      
      // Close form
      await firstFeedbackButton.locator('button:has-text("Cancel")').click();
      
      // Verify form is hidden
      await expect(firstFeedbackButton.locator('text=Provide Detailed Feedback')).not.toBeVisible();
    });

    test('should submit detailed feedback with rating and comment', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Mock the feedback API response
      await page.route('/api/feedback/', (route) => {
        const requestBody = route.request().postDataJSON();
        
        // Verify request contains detailed feedback data
        expect(requestBody.rating).toBe('very_helpful');
        expect(requestBody.comment).toBe('This finding helped me identify a real issue');
        expect(requestBody.is_helpful).toBe(true);
        
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_detailed_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      const firstFeedbackButton = page.locator('.feedback-button').first();
      
      // Open detailed feedback form
      await firstFeedbackButton.locator('button:has-text("📝 Detailed feedback")').click();
      
      // Fill out the form
      await firstFeedbackButton.locator('select').selectOption('very_helpful');
      await firstFeedbackButton.locator('textarea').fill('This finding helped me identify a real issue');
      
      // Submit the form
      await firstFeedbackButton.locator('button:has-text("Submit Feedback")').click();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
      
      // Verify form is closed
      await expect(firstFeedbackButton.locator('text=Provide Detailed Feedback')).not.toBeVisible();
    });

    test('should show loading state during submission', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Mock slow API response
      await page.route('/api/feedback/', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_slow_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      const firstFeedbackButton = page.locator('.feedback-button').first();
      
      // Open detailed feedback form
      await firstFeedbackButton.locator('button:has-text("📝 Detailed feedback")').click();
      
      // Fill out the form
      await firstFeedbackButton.locator('textarea').fill('Test comment');
      
      // Submit the form
      await firstFeedbackButton.locator('button:has-text("Submit Feedback")').click();
      
      // Verify loading state
      await expect(firstFeedbackButton.locator('button:has-text("Submitting...")')).toBeVisible();
      
      // Wait for completion
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });
  });

  test.describe('LLM Insights Feedback', () => {
    test('should show feedback buttons for LLM insights', async ({ page }) => {
      // Navigate to insights tab
      await page.click('button:has-text("LLM Insights")');
      
      // Wait for insights to load
      await expect(page.locator('.feedback-button')).toHaveCount(4, { timeout: 5000 });
      
      // Verify feedback buttons exist for insights
      const feedbackButtons = page.locator('.feedback-button');
      await expect(feedbackButtons.first()).toBeVisible();
    });

    test('should submit feedback for LLM insight', async ({ page }) => {
      // Navigate to insights tab
      await page.click('button:has-text("LLM Insights")');
      
      // Mock the feedback API response
      await page.route('/api/feedback/', (route) => {
        const requestBody = route.request().postDataJSON();
        
        // Verify request data for LLM insight
        expect(requestBody.feedback_type).toBe('llm_insight');
        expect(requestBody.is_helpful).toBe(true);
        
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_insight_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Click helpful button on first insight
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await firstFeedbackButton.locator('button:has-text("👍 Helpful")').click();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });
  });

  test.describe('Diagram Feedback', () => {
    test('should show feedback buttons for diagrams', async ({ page }) => {
      // Navigate to diagrams tab
      await page.click('button:has-text("Diagrams")');
      
      // Wait for diagrams to load
      await expect(page.locator('.feedback-button')).toHaveCount(2, { timeout: 5000 });
      
      // Verify feedback buttons exist for diagrams
      const feedbackButtons = page.locator('.feedback-button');
      await expect(feedbackButtons.first()).toBeVisible();
    });

    test('should submit feedback for diagram', async ({ page }) => {
      // Navigate to diagrams tab
      await page.click('button:has-text("Diagrams")');
      
      // Mock the feedback API response
      await page.route('/api/feedback/', (route) => {
        const requestBody = route.request().postDataJSON();
        
        // Verify request data for diagram
        expect(requestBody.feedback_type).toBe('diagram');
        expect(requestBody.is_helpful).toBe(false);
        
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_diagram_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Click not helpful button on first diagram
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await firstFeedbackButton.locator('button:has-text("👎 Not Helpful")').click();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('feedback buttons should be keyboard accessible', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      const firstFeedbackButton = page.locator('.feedback-button').first();
      
      // Focus on helpful button and press Enter
      await firstFeedbackButton.locator('button:has-text("👍 Helpful")').focus();
      
      // Mock API response
      await page.route('/api/feedback/', (route) => {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_keyboard_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Press Enter to submit
      await page.keyboard.press('Enter');
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });

    test('detailed feedback form should be keyboard navigable', async ({ page }) => {
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      const firstFeedbackButton = page.locator('.feedback-button').first();
      
      // Open detailed feedback form
      await firstFeedbackButton.locator('button:has-text("📝 Detailed feedback")').click();
      
      // Navigate through form elements with Tab
      await page.keyboard.press('Tab'); // Radio button
      await page.keyboard.press('Tab'); // Rating select
      await page.keyboard.press('Tab'); // Textarea
      await page.keyboard.press('Tab'); // Cancel button
      await page.keyboard.press('Tab'); // Submit button
      
      // Verify focus is on submit button
      await expect(firstFeedbackButton.locator('button:has-text("Submit Feedback")')).toBeFocused();
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('feedback buttons should work on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Navigate to findings tab
      await page.click('button:has-text("Findings")');
      
      // Verify feedback buttons are visible and clickable on mobile
      const firstFeedbackButton = page.locator('.feedback-button').first();
      await expect(firstFeedbackButton).toBeVisible();
      
      // Mock API response
      await page.route('/api/feedback/', (route) => {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            feedback_id: 'feedback_mobile_123',
            message: 'Feedback submitted successfully',
            timestamp: new Date().toISOString()
          })
        });
      });
      
      // Tap helpful button (mobile touch)
      await firstFeedbackButton.locator('button:has-text("👍 Helpful")').tap();
      
      // Verify success message appears
      await expect(firstFeedbackButton.locator('text=Thank you for your feedback!')).toBeVisible();
    });
  });
}); 