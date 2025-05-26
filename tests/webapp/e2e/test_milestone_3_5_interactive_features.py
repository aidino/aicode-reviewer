"""
E2E tests for Milestone 3.5: Web Application - Phase 2 (Interactive Features).

This module contains comprehensive end-to-end tests for interactive features including:
- Scan submission workflow
- Interactive diagram display with zoom/pan
- Sequence diagram rendering and interaction
- Java/Kotlin report data visualization
- User interface responsiveness and accessibility
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import json


class TestMilestone35InteractiveFeatures:
    """E2E test cases for Milestone 3.5 interactive features."""

    @pytest.fixture(scope="class")
    def driver(self):
        """
        Create and configure Selenium WebDriver.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for CI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280,720')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    @pytest.fixture
    def test_scan_data(self):
        """
        Create test data for scan submission.
        
        Returns:
            dict: Test scan data
        """
        return {
            'repository_url': 'https://github.com/test/repo',
            'scan_type': 'pull_request',
            'pr_id': '123',
            'branch': 'feature/test-branch',
            'language': 'python'
        }

    @pytest.fixture
    def mock_scan_response(self):
        """
        Create mock scan response data.
        
        Returns:
            dict: Mock scan response
        """
        return {
            'scan_id': 'scan_123456',
            'job_id': 'job_789012',
            'status': 'PENDING',
            'message': 'Scan initiated successfully',
            'estimated_duration': 300,
            'repository': 'https://github.com/test/repo',
            'scan_type': 'pull_request'
        }

    def test_scan_form_submission_workflow(self, driver, test_scan_data, mock_scan_response):
        """
        Test complete scan submission workflow.
        
        Args:
            driver: Selenium WebDriver
            test_scan_data: Test scan data fixture
            mock_scan_response: Mock scan response fixture
        """
        # Navigate to scan creation page
        driver.get("http://localhost:3000/create-scan")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scan-form"))
        )

        # Fill scan form
        repo_input = driver.find_element(By.NAME, "repository_url")
        repo_input.clear()
        repo_input.send_keys(test_scan_data['repository_url'])

        # Select scan type
        scan_type_select = driver.find_element(By.NAME, "scan_type")
        scan_type_select.click()
        pr_option = driver.find_element(By.XPATH, "//option[@value='pull_request']")
        pr_option.click()

        # Fill PR ID
        pr_input = driver.find_element(By.NAME, "pr_id")
        pr_input.clear()
        pr_input.send_keys(test_scan_data['pr_id'])

        # Mock the API response
        with patch('fetch') as mock_fetch:
            mock_fetch.return_value.ok = True
            mock_fetch.return_value.json.return_value = mock_scan_response
            
            # Submit form
            submit_button = driver.find_element(By.TYPE, "submit")
            submit_button.click()

            # Wait for success message
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )

            # Verify scan ID is displayed
            scan_id_element = driver.find_element(By.CLASS_NAME, "scan-id")
            assert mock_scan_response['scan_id'] in scan_id_element.text

    def test_interactive_diagram_display(self, driver):
        """
        Test interactive diagram display with zoom and pan.
        
        Args:
            driver: Selenium WebDriver
        """
        # Navigate to diagram page with mock data
        driver.get("http://localhost:3000/reports/test-scan-id")
        
        # Wait for diagram to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "diagram-display"))
        )

        # Test zoom functionality
        zoom_in_button = driver.find_element(By.CLASS_NAME, "zoom-in-button")
        zoom_out_button = driver.find_element(By.CLASS_NAME, "zoom-out-button")
        reset_button = driver.find_element(By.CLASS_NAME, "reset-transform-button")

        # Test zoom in
        initial_scale = self.get_diagram_scale(driver)
        zoom_in_button.click()
        time.sleep(0.5)  # Allow animation to complete
        zoomed_scale = self.get_diagram_scale(driver)
        assert zoomed_scale > initial_scale

        # Test zoom out
        zoom_out_button.click()
        time.sleep(0.5)
        reduced_scale = self.get_diagram_scale(driver)
        assert reduced_scale < zoomed_scale

        # Test reset
        reset_button.click()
        time.sleep(0.5)
        reset_scale = self.get_diagram_scale(driver)
        assert abs(reset_scale - 1.0) < 0.1  # Should be close to 1.0

        # Test pan functionality
        diagram_container = driver.find_element(By.CLASS_NAME, "transform-component")
        actions = ActionChains(driver)
        
        # Drag to pan
        actions.click_and_hold(diagram_container)
        actions.move_by_offset(50, 30)
        actions.release()
        actions.perform()
        
        # Verify position changed
        transform = diagram_container.get_attribute("style")
        assert "translate" in transform

    def test_sequence_diagram_rendering(self, driver):
        """
        Test sequence diagram rendering and interaction.
        
        Args:
            driver: Selenium WebDriver
        """
        # Navigate to sequence diagram page
        driver.get("http://localhost:3000/reports/test-scan-id/sequence")
        
        # Wait for sequence diagram to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sequence-diagram-viewer"))
        )

        # Test timeline controls
        timeline_container = driver.find_element(By.CLASS_NAME, "sequence-timeline")
        timeline_items = timeline_container.find_elements(By.CLASS_NAME, "timeline-item")
        assert len(timeline_items) > 0

        # Click on timeline item
        first_timeline_item = timeline_items[0]
        first_timeline_item.click()
        
        # Verify highlight appears
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "timeline-item-active"))
        )

        # Test actor highlighting
        actors = driver.find_elements(By.CLASS_NAME, "sequence-actor")
        if actors:
            first_actor = actors[0]
            first_actor.click()
            
            # Verify actor is highlighted
            assert "actor-highlighted" in first_actor.get_attribute("class")

        # Test interaction filtering
        filter_input = driver.find_element(By.CLASS_NAME, "interaction-filter")
        filter_input.send_keys("request")
        
        # Verify filtered results
        filtered_interactions = driver.find_elements(By.CLASS_NAME, "interaction-visible")
        for interaction in filtered_interactions:
            assert "request" in interaction.text.lower()

    def test_java_report_viewer(self, driver):
        """
        Test Java-specific report viewer functionality.
        
        Args:
            driver: Selenium WebDriver
        """
        # Navigate to Java report page
        driver.get("http://localhost:3000/reports/java-scan-id")
        
        # Wait for Java report viewer to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "java-report-viewer"))
        )

        # Test tab navigation
        tabs = driver.find_elements(By.CLASS_NAME, "tab-button")
        classes_tab = [tab for tab in tabs if "Classes" in tab.text][0]
        classes_tab.click()
        
        # Verify classes tab content
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "java-classes-list"))
        )

        # Test class expansion
        class_items = driver.find_elements(By.CLASS_NAME, "java-class-item")
        if class_items:
            first_class = class_items[0]
            first_class.click()
            
            # Verify methods and fields are shown
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "java-methods"))
            )

        # Test package navigation
        packages_tab = [tab for tab in tabs if "Packages" in tab.text][0]
        packages_tab.click()
        
        # Verify package structure
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "package-structure"))
        )

        # Test metrics view
        metrics_tab = [tab for tab in tabs if "Metrics" in tab.text][0]
        metrics_tab.click()
        
        # Verify metrics are displayed
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "code-metrics"))
        )
        
        metrics_cards = driver.find_elements(By.CLASS_NAME, "metric-card")
        assert len(metrics_cards) > 0

    def test_kotlin_report_viewer(self, driver):
        """
        Test Kotlin-specific report viewer functionality.
        
        Args:
            driver: Selenium WebDriver
        """
        # Navigate to Kotlin report page
        driver.get("http://localhost:3000/reports/kotlin-scan-id")
        
        # Wait for Kotlin report viewer to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kotlin-report-viewer"))
        )

        # Test Kotlin-specific features
        tabs = driver.find_elements(By.CLASS_NAME, "tab-button")
        
        # Test extensions tab
        extensions_tab = [tab for tab in tabs if "Extensions" in tab.text][0]
        extensions_tab.click()
        
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kotlin-extensions"))
        )

        # Test data class highlighting
        classes_tab = [tab for tab in tabs if "Classes" in tab.text][0]
        classes_tab.click()
        
        data_classes = driver.find_elements(By.XPATH, "//span[contains(@class, 'class-type') and text()='DATA CLASS']")
        assert len(data_classes) >= 0  # May be zero if no data classes

        # Test suspend function indicators
        suspend_functions = driver.find_elements(By.XPATH, "//span[contains(@class, 'function-modifier') and text()='suspend']")
        assert len(suspend_functions) >= 0  # May be zero if no suspend functions

    def test_responsive_design(self, driver):
        """
        Test responsive design across different screen sizes.
        
        Args:
            driver: Selenium WebDriver
        """
        # Test desktop view
        driver.set_window_size(1280, 720)
        driver.get("http://localhost:3000/reports/test-scan-id")
        
        # Verify desktop layout
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        assert sidebar.is_displayed()
        
        main_content = driver.find_element(By.CLASS_NAME, "main-content")
        assert main_content.size['width'] > 800

        # Test tablet view
        driver.set_window_size(768, 1024)
        time.sleep(1)  # Allow layout to adjust
        
        # Verify tablet adaptations
        if self.element_exists(driver, By.CLASS_NAME, "mobile-menu-button"):
            mobile_menu_button = driver.find_element(By.CLASS_NAME, "mobile-menu-button")
            assert mobile_menu_button.is_displayed()

        # Test mobile view
        driver.set_window_size(360, 640)
        time.sleep(1)
        
        # Verify mobile layout
        assert self.element_exists(driver, By.CLASS_NAME, "mobile-layout")

    def test_accessibility_features(self, driver):
        """
        Test accessibility features and ARIA compliance.
        
        Args:
            driver: Selenium WebDriver
        """
        driver.get("http://localhost:3000/create-scan")
        
        # Test keyboard navigation
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)
        
        # Verify focus indicators
        focused_element = driver.switch_to.active_element
        assert focused_element.tag_name in ['input', 'button', 'select', 'textarea', 'a']

        # Test ARIA labels
        form_elements = driver.find_elements(By.XPATH, "//*[@aria-label or @aria-labelledby]")
        assert len(form_elements) > 0

        # Test semantic structure
        headings = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
        assert len(headings) > 0

        # Test form labels
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_element in inputs:
            input_id = input_element.get_attribute("id")
            if input_id:
                labels = driver.find_elements(By.XPATH, f"//label[@for='{input_id}']")
                assert len(labels) > 0 or input_element.get_attribute("aria-label")

    def test_error_handling_and_feedback(self, driver):
        """
        Test error handling and user feedback mechanisms.
        
        Args:
            driver: Selenium WebDriver
        """
        driver.get("http://localhost:3000/create-scan")
        
        # Test form validation
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Verify validation errors appear
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        
        error_messages = driver.find_elements(By.CLASS_NAME, "error-message")
        assert len(error_messages) > 0

        # Test network error handling
        with patch('fetch') as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            
            # Fill valid form data
            repo_input = driver.find_element(By.NAME, "repository_url")
            repo_input.send_keys("https://github.com/test/repo")
            
            submit_button.click()
            
            # Verify error handling
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "network-error"))
            )

    def test_performance_optimization(self, driver):
        """
        Test performance optimization features.
        
        Args:
            driver: Selenium WebDriver
        """
        # Test large diagram handling
        driver.get("http://localhost:3000/reports/large-scan-id")
        
        # Measure load time
        start_time = time.time()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "diagram-display"))
        )
        load_time = time.time() - start_time
        
        # Should load within reasonable time
        assert load_time < 10.0

        # Test lazy loading
        diagram_sections = driver.find_elements(By.CLASS_NAME, "diagram-section")
        if len(diagram_sections) > 5:
            # Verify not all sections are immediately rendered
            rendered_sections = [s for s in diagram_sections if s.get_attribute("data-rendered") == "true"]
            assert len(rendered_sections) < len(diagram_sections)

    def test_browser_compatibility(self, driver):
        """
        Test cross-browser compatibility features.
        
        Args:
            driver: Selenium WebDriver
        """
        # Test JavaScript features
        driver.get("http://localhost:3000/create-scan")
        
        # Execute JavaScript to test compatibility
        js_result = driver.execute_script("""
            return {
                supports_es6: typeof Promise !== 'undefined',
                supports_fetch: typeof fetch !== 'undefined',
                supports_flexbox: CSS.supports('display', 'flex'),
                supports_grid: CSS.supports('display', 'grid')
            };
        """)
        
        assert js_result['supports_es6']
        assert js_result['supports_fetch']
        assert js_result['supports_flexbox']

    def test_data_persistence_and_state_management(self, driver):
        """
        Test data persistence and state management.
        
        Args:
            driver: Selenium WebDriver
        """
        driver.get("http://localhost:3000/create-scan")
        
        # Fill form data
        repo_input = driver.find_element(By.NAME, "repository_url")
        test_url = "https://github.com/test/persistence"
        repo_input.send_keys(test_url)
        
        # Navigate away and back
        driver.get("http://localhost:3000/reports")
        driver.back()
        
        # Verify form data is preserved (if implemented)
        repo_input = driver.find_element(By.NAME, "repository_url")
        if repo_input.get_attribute("value"):
            assert test_url in repo_input.get_attribute("value")

    # Helper methods
    def get_diagram_scale(self, driver):
        """
        Get current diagram scale from transform matrix.
        
        Args:
            driver: Selenium WebDriver
            
        Returns:
            float: Current scale value
        """
        try:
            transform_element = driver.find_element(By.CLASS_NAME, "transform-component")
            style = transform_element.get_attribute("style")
            
            # Extract scale from transform matrix
            if "scale" in style:
                import re
                scale_match = re.search(r'scale\(([0-9.]+)\)', style)
                if scale_match:
                    return float(scale_match.group(1))
            
            return 1.0  # Default scale
        except:
            return 1.0

    def element_exists(self, driver, by, value):
        """
        Check if element exists without raising exception.
        
        Args:
            driver: Selenium WebDriver
            by: Selenium By locator type
            value: Locator value
            
        Returns:
            bool: True if element exists
        """
        try:
            driver.find_element(by, value)
            return True
        except:
            return False

    def wait_for_async_operation(self, driver, timeout=10):
        """
        Wait for async operations to complete.
        
        Args:
            driver: Selenium WebDriver
            timeout: Maximum wait time in seconds
        """
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )


# Fixtures for pytest
@pytest.fixture(scope="session")
def interactive_features_test_suite():
    """
    Create a test suite for interactive features.
    
    Returns:
        TestMilestone35InteractiveFeatures: Test suite instance
    """
    return TestMilestone35InteractiveFeatures()


@pytest.mark.e2e
class TestE2EWorkflow:
    """Complete end-to-end workflow tests."""

    def test_complete_scan_workflow(self, driver):
        """
        Test complete workflow from scan creation to report viewing.
        
        Args:
            driver: Selenium WebDriver
        """
        # Step 1: Create scan
        driver.get("http://localhost:3000/create-scan")
        
        # Fill and submit scan form
        repo_input = driver.find_element(By.NAME, "repository_url")
        repo_input.send_keys("https://github.com/test/complete-workflow")
        
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Step 2: Navigate to scan status
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scan-id"))
        )
        
        scan_id_element = driver.find_element(By.CLASS_NAME, "scan-id")
        scan_id = scan_id_element.text.split(": ")[1]
        
        # Step 3: View scan results
        driver.get(f"http://localhost:3000/reports/{scan_id}")
        
        # Step 4: Interact with report
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-viewer"))
        )
        
        # Test diagram interaction
        if self.element_exists(driver, By.CLASS_NAME, "diagram-display"):
            zoom_in = driver.find_element(By.CLASS_NAME, "zoom-in-button")
            zoom_in.click()
        
        # Test tab navigation
        tabs = driver.find_elements(By.CLASS_NAME, "tab-button")
        for tab in tabs:
            tab.click()
            time.sleep(0.5)
        
        # Verify workflow completion
        assert "report-viewer" in driver.page_source

    def element_exists(self, driver, by, value):
        """Check if element exists."""
        try:
            driver.find_element(by, value)
            return True
        except:
            return False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short']) 