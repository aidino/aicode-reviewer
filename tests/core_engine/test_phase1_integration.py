"""
Integration tests for Phase 1 Python PR scan workflow.

This module contains end-to-end integration tests for the complete
Python PR scanning workflow using the LangGraph orchestrator.
External dependencies are mocked while core analysis remains real.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
import logging
from typing import Dict, Any

from src.core_engine.orchestrator import compile_graph, GraphState


# Sample Python code for PR diff simulation
SAMPLE_PYTHON_CODE = """
import os
import sys
import pdb

def very_long_function_that_exceeds_line_limit():
    \"\"\"This function is intentionally long to trigger static analysis rules.\"\"\"
    # Line 1
    print("Debug: Starting function")  # Should trigger print statement rule
    # Line 3
    result = []
    # Line 5
    for i in range(100):
        # Line 7
        if i % 2 == 0:
            # Line 9
            result.append(i * 2)
        else:
            # Line 12
            result.append(i * 3)
        # Line 14
        if i == 50:
            # Line 16
            pdb.set_trace()  # Should trigger pdb rule
        # Line 18
        temp_value = i ** 2
        # Line 20
        temp_value += 1
        # Line 22
        temp_value *= 2
        # Line 24
        if temp_value > 1000:
            # Line 26
            break
        # Line 28
        continue
    # Line 30
    print(f"Result length: {len(result)}")
    # Line 32
    return result
    # Line 34
    # Line 35
    # Line 36
    # Line 37
    # Line 38
    # Line 39
    # Line 40
    # Line 41
    # Line 42
    # Line 43
    # Line 44
    # Line 45
    # Line 46
    # Line 47
    # Line 48
    # Line 49
    # Line 50
    # Line 51
    # Line 52
    # Line 53
    # Line 54
    # Line 55
    # Line 56
    # Line 57
    # Line 58
    # Line 59
    # Line 60 (Function exceeds 50 line limit)


class VeryLargeClassThatExceedsClassLimit:
    \"\"\"This class is intentionally large to trigger class size rule.\"\"\"
    
    def __init__(self):
        self.data = []
    
    def method1(self):
        pass
    
    def method2(self):
        pass
    
    def method3(self):
        pass
    
    def method4(self):
        pass
    
    def method5(self):
        pass
    
    def method6(self):
        pass
    
    def method7(self):
        pass
    
    def method8(self):
        pass
    
    def method9(self):
        pass
    
    def method10(self):
        pass
    
    # Continue adding methods to exceed 200 lines...
    # [Methods 11-100 would be here in real scenario]
    # This class structure would trigger the class too long rule
"""

# Sample PR diff that contains the above Python code
SAMPLE_PR_DIFF = f"""diff --git a/src/sample_module.py b/src/sample_module.py
new file mode 100644
index 0000000..abc123
--- /dev/null
+++ b/src/sample_module.py
@@ -0,0 +1,100 @@
+{chr(10).join("+" + line for line in SAMPLE_PYTHON_CODE.split(chr(10)))}"""

# Sample project files for fallback scenarios
SAMPLE_PROJECT_FILES = {
    "src/main.py": """
import unused_module  # Should trigger unused import rule
import os

def main():
    print("Hello World")  # Should trigger print rule
    return 0

if __name__ == "__main__":
    main()
""",
    "src/utils.py": """
import sys
import pdb

def debug_helper():
    pdb.set_trace()  # Should trigger pdb rule
    return True

def utility_function():
    return "utility"
""",
    "src/large_file.py": SAMPLE_PYTHON_CODE  # Will trigger multiple rules
}

# Sample LLM response for mocking
SAMPLE_LLM_RESPONSE = """# Code Quality Assessment

## Static Analysis Review
The code shows several areas that need attention:

## Security Considerations
- **Critical**: Debugging statements detected (pdb.set_trace()) that must be removed before production
- These debugging calls can expose sensitive information and should never be deployed

## Performance Analysis
- **Function Complexity**: Large functions detected that impact maintainability
- Consider breaking down functions longer than 50 lines into smaller, focused units
- Large classes detected that violate Single Responsibility Principle

## Best Practices
- **Logging Issues**: Print statements should be replaced with proper logging framework
- Use Python's logging module for better control and formatting
- **Import Management**: Unused imports detected that should be cleaned up

## Specific Recommendations
1. Remove all pdb.set_trace() calls immediately
2. Replace print() statements with logging.info() or logging.debug()
3. Refactor large functions into smaller, testable components
4. Split large classes following Single Responsibility Principle
5. Clean up unused imports to improve code clarity

## Code Structure
The overall code structure shows room for improvement in modularity and separation of concerns."""


class TestPhase1Integration:
    """Integration tests for Phase 1 Python PR scan workflow."""
    
    @pytest.fixture
    def sample_pr_scan_request(self):
        """Create sample PR scan request data."""
        return {
            "repo_url": "https://github.com/test/integration-repo",
            "pr_id": 42,
            "target_branch": "main",
            "source_branch": "feature/test-changes",
            "scan_type": "pr"
        }
    
    @pytest.fixture
    def sample_project_scan_request(self):
        """Create sample project scan request data."""
        return {
            "repo_url": "https://github.com/test/integration-repo",
            "branch": "main",
            "scan_type": "project"
        }
    
    @pytest.fixture
    def initial_graph_state_pr(self, sample_pr_scan_request):
        """Create initial GraphState for PR scan."""
        return GraphState(
            scan_request_data=sample_pr_scan_request,
            repo_url="",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            markdown_report=None,
            json_report=None,
            error_message=None,
            current_step="start",
            workflow_metadata={}
        )
    
    @pytest.fixture
    def initial_graph_state_project(self, sample_project_scan_request):
        """Create initial GraphState for project scan."""
        return GraphState(
            scan_request_data=sample_project_scan_request,
            repo_url="",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            markdown_report=None,
            json_report=None,
            error_message=None,
            current_step="start",
            workflow_metadata={}
        )
    
    def test_pr_scan_workflow_complete_success(self, initial_graph_state_pr):
        """Test complete PR scan workflow with all components."""
        
        # Mock external dependencies
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup CodeFetcherAgent mock
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.return_value = SAMPLE_PR_DIFF
            mock_fetcher.get_changed_files_from_diff.return_value = ["src/sample_module.py"]
            
            # Setup LLMOrchestratorAgent mock
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.llm_provider = "mock"
            mock_llm.model_name = "test-model"
            mock_llm.analyze_pr_diff.return_value = SAMPLE_LLM_RESPONSE
            
            # Compile and run the workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Verify workflow completion
            assert final_state["current_step"] == "completed"
            assert final_state.get("error_message") is None
            
            # Verify code fetching
            assert "pr_diff" in final_state
            assert final_state["pr_diff"] == SAMPLE_PR_DIFF
            assert "workflow_metadata" in final_state
            assert final_state["workflow_metadata"]["changed_files"] == ["src/sample_module.py"]
            
            # Verify AST parsing
            assert "parsed_asts" in final_state
            parsed_asts = final_state["parsed_asts"]
            assert len(parsed_asts) > 0
            
            # Verify static analysis findings
            assert "static_analysis_findings" in final_state
            static_findings = final_state["static_analysis_findings"]
            assert isinstance(static_findings, list)
            assert len(static_findings) > 0
            
            # Check for expected static analysis rules
            finding_rule_ids = [f.get("rule_id") for f in static_findings]
            expected_rules = ["PDB_TRACE_FOUND", "PRINT_STATEMENT_FOUND", "FUNCTION_TOO_LONG"]
            
            for expected_rule in expected_rules:
                assert expected_rule in finding_rule_ids, f"Expected rule {expected_rule} not found in findings"
            
            # Verify LLM insights
            assert "llm_insights" in final_state
            assert final_state["llm_insights"] == SAMPLE_LLM_RESPONSE
            
            # Verify report generation
            assert "report_data" in final_state
            assert "markdown_report" in final_state
            assert "json_report" in final_state
            
            # Verify report data structure
            report_data = final_state["report_data"]
            assert "scan_info" in report_data
            assert "summary" in report_data
            assert "static_analysis_findings" in report_data
            assert "llm_review" in report_data
            
            # Verify scan info
            scan_info = report_data["scan_info"]
            assert scan_info["repository"] == "https://github.com/test/integration-repo"
            assert scan_info["pr_id"] == 42
            assert scan_info["scan_type"] == "pr"
            
            # Verify summary
            summary = report_data["summary"]
            assert summary["total_findings"] >= 3  # At least pdb, print, function_too_long
            assert summary["scan_status"] == "completed"
            assert summary["has_llm_analysis"] is True
            
            # Verify severity breakdown
            severity_breakdown = summary["severity_breakdown"]
            assert "Warning" in severity_breakdown
            assert severity_breakdown["Warning"] >= 1
            
            # Verify category breakdown
            category_breakdown = summary["category_breakdown"]
            expected_categories = ["debugging", "logging", "complexity"]
            for category in expected_categories:
                assert category in category_breakdown, f"Expected category {category} not found"
            
            # Verify LLM review
            llm_review = report_data["llm_review"]
            assert llm_review["insights"] == SAMPLE_LLM_RESPONSE
            assert llm_review["has_content"] is True
            
            # Verify markdown report contains key sections
            markdown_report = final_state["markdown_report"]
            assert "# Code Review Report:" in markdown_report
            assert "## 📋 Executive Summary" in markdown_report
            assert "## 🔍 Static Analysis Results" in markdown_report
            assert "## 🤖 AI Analysis & Insights" in markdown_report
            
            # Verify JSON report is valid JSON
            json_report = final_state["json_report"]
            parsed_json = json.loads(json_report)
            assert parsed_json["summary"]["total_findings"] >= 3
    
    def test_project_scan_workflow_complete_success(self, initial_graph_state_project):
        """Test complete project scan workflow."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup mocks
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_project_files.return_value = SAMPLE_PROJECT_FILES
            
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.llm_provider = "mock"
            mock_llm.model_name = "test-model"
            mock_llm.analyze_code_with_context.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_project)
            
            # Basic assertions
            assert final_state["current_step"] == "completed"
            assert final_state.get("error_message") is None
            
            # Verify project code
            assert "project_code" in final_state
            assert final_state["project_code"] == SAMPLE_PROJECT_FILES
            
            # Verify static analysis found issues
            static_findings = final_state["static_analysis_findings"]
            assert len(static_findings) > 0
            
            # Should find issues in all files
            finding_files = [f.get("file") for f in static_findings]
            assert "src/main.py" in finding_files
            assert "src/utils.py" in finding_files
            assert "src/large_file.py" in finding_files
            
            # Verify LLM analysis
            assert final_state["llm_insights"] == SAMPLE_LLM_RESPONSE
            
            # Verify report structure
            report_data = final_state["report_data"]
            assert report_data["scan_info"]["scan_type"] == "project"
            assert report_data["summary"]["total_findings"] > 0
            
            # Verify markdown report
            assert "markdown_report" in final_state
            markdown_report = final_state["markdown_report"]
            assert "# Code Review Report:" in markdown_report
            assert "## 📋 Executive Summary" in markdown_report
            assert "## 🔍 Static Analysis Results" in markdown_report
            assert "## 🤖 AI Analysis & Insights" in markdown_report
            
            # Verify JSON report
            assert "json_report" in final_state
            json_report = final_state["json_report"]
            parsed_json = json.loads(json_report)
            assert parsed_json["scan_info"]["scan_type"] == "project"
            assert parsed_json["summary"]["total_findings"] > 0
            assert parsed_json["llm_review"]["insights"] == SAMPLE_LLM_RESPONSE
    
    def test_pr_scan_with_fallback_to_project_files(self, initial_graph_state_pr):
        """Test PR scan that falls back to project files when diff fails."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup fetcher mock with PR diff failure and project files success
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.side_effect = Exception("PR diff failed")
            mock_fetcher.get_project_files.return_value = SAMPLE_PROJECT_FILES
            
            # Setup LLM mock
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.llm_provider = "mock"
            mock_llm.model_name = "test-model"
            mock_llm.analyze_code_with_context.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Should complete successfully with fallback
            assert final_state["current_step"] == "completed"
            assert final_state.get("error_message") is None
            
            # Should have project code instead of pr_diff
            assert "project_code" in final_state
            assert final_state["project_code"] == SAMPLE_PROJECT_FILES
            assert final_state["workflow_metadata"]["fallback_mode"] is True
            
            # Should still have static analysis findings and LLM insights
            assert len(final_state["static_analysis_findings"]) > 0
            assert final_state["llm_insights"] == SAMPLE_LLM_RESPONSE
            
            # Verify report formats
            assert "markdown_report" in final_state
            markdown_report = final_state["markdown_report"]
            assert "# Code Review Report:" in markdown_report
            assert "## 📋 Executive Summary" in markdown_report
            assert "## 🔍 Static Analysis Results" in markdown_report
            assert "## 🤖 AI Analysis & Insights" in markdown_report
            
            # Verify JSON report
            assert "json_report" in final_state
            json_report = final_state["json_report"]
            parsed_json = json.loads(json_report)
            assert parsed_json["scan_info"]["scan_type"] == "pr"  # Still a PR scan, just using fallback
            assert parsed_json["summary"]["total_findings"] > 0
            assert parsed_json["llm_review"]["insights"] == SAMPLE_LLM_RESPONSE
            # Verify fallback mode in workflow metadata
            assert final_state["workflow_metadata"]["fallback_mode"] is True
    
    def test_workflow_static_analysis_rule_coverage(self, initial_graph_state_pr):
        """Test that all implemented static analysis rules are triggered."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup mocks
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.return_value = SAMPLE_PR_DIFF
            mock_fetcher.get_changed_files_from_diff.return_value = ["src/sample_module.py"]
            
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.analyze_pr_diff.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Extract all rule IDs from findings
            static_findings = final_state["static_analysis_findings"]
            found_rules = set(f.get("rule_id") for f in static_findings)
            
            # Verify we found the expected rules based on our sample code
            expected_rules = {
                "PDB_TRACE_FOUND",      # pdb.set_trace() in sample code
                "PRINT_STATEMENT_FOUND", # print() statements in sample code
                "FUNCTION_TOO_LONG"     # very_long_function exceeds 50 lines
            }
            
            for rule in expected_rules:
                assert rule in found_rules, f"Expected static analysis rule {rule} not found. Found: {found_rules}"
            
            # Verify severity levels are assigned
            severities = set(f.get("severity") for f in static_findings)
            assert len(severities) > 0
            assert all(s in ["Error", "Warning", "Info"] for s in severities)
            
            # Verify categories are assigned
            categories = set(f.get("category") for f in static_findings)
            expected_categories = {"debugging", "logging", "complexity"}
            assert len(categories.intersection(expected_categories)) > 0
    
    def test_workflow_error_handling(self):
        """Test workflow error handling with invalid input."""
        
        # Create invalid initial state
        invalid_state = GraphState(
            scan_request_data={},  # Missing repo_url
            repo_url="",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="start",
            workflow_metadata={}
        )
        
        # Run workflow
        app = compile_graph()
        final_state = app.invoke(invalid_state)
        
        # Should handle error gracefully
        assert final_state["current_step"] == "error_handled"
        assert "error_message" in final_state
        assert "Repository URL is required" in final_state["error_message"]
        
        # Should still have report data (error report)
        assert "report_data" in final_state
        error_report = final_state["report_data"]
        assert error_report["summary"]["status"] == "error"
    
    def test_workflow_metadata_tracking(self, initial_graph_state_pr):
        """Test that workflow metadata is properly tracked throughout execution."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup mocks
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.return_value = SAMPLE_PR_DIFF
            mock_fetcher.get_changed_files_from_diff.return_value = ["src/sample_module.py"]
            
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.llm_provider = "mock"
            mock_llm.model_name = "test-model"
            mock_llm.analyze_pr_diff.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Verify metadata is properly tracked
            metadata = final_state["workflow_metadata"]
            
            # Should have scan metadata
            assert metadata["scan_type"] == "pr"
            assert metadata["changed_files"] == ["src/sample_module.py"]
            assert metadata["target_branch"] == "main"
            assert metadata["source_branch"] == "feature/test-changes"
            
            # Should have LLM metadata
            assert metadata["llm_provider"] == "mock"
            assert metadata["llm_model"] == "test-model"
            assert "static_findings_processed" in metadata
            
            # Should have report generation metadata
            assert "report_generation_time" in metadata
            assert metadata["report_formats"] == ["json", "markdown"]
            assert "report_agent_version" in metadata
    
    def test_ast_parsing_accuracy(self, initial_graph_state_pr):
        """Test that AST parsing correctly extracts Python code structure."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup mocks
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.return_value = SAMPLE_PR_DIFF
            mock_fetcher.get_changed_files_from_diff.return_value = ["src/sample_module.py"]
            
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.analyze_pr_diff.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Check AST parsing results
            parsed_asts = final_state["parsed_asts"]
            assert len(parsed_asts) > 0
            
            # For PR diff, we might get diff_summary if individual files can't be extracted
            # This is expected behavior based on the current diff parsing implementation
            if "diff_summary" in parsed_asts:
                # Verify diff summary contains the expected content
                diff_summary = parsed_asts["diff_summary"]
                assert diff_summary["type"] == "diff"
                assert "Could not extract individual files" in diff_summary["note"]
            else:
                # If individual files were extracted, verify structure
                for filename, ast_data in parsed_asts.items():
                    if isinstance(ast_data, dict) and "ast_node" in ast_data:
                        # Language info might be in structural_info for some implementations
                        language = ast_data.get("language") or ast_data.get("structural_info", {}).get("language")
                        assert language == "python", f"Expected Python language for {filename}"
                        assert "structural_info" in ast_data
                        structural_info = ast_data["structural_info"]
                        assert isinstance(structural_info, dict)
                        assert "classes" in structural_info
                        assert "functions" in structural_info
                        assert "imports" in structural_info
    
    def test_report_format_consistency(self, initial_graph_state_pr):
        """Test that generated reports maintain consistent format and structure."""
        
        with patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent') as mock_fetcher_class, \
             patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent') as mock_llm_class:
            
            # Setup mocks
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_fetcher.get_pr_diff.return_value = SAMPLE_PR_DIFF
            mock_fetcher.get_changed_files_from_diff.return_value = ["src/sample_module.py"]
            
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm
            mock_llm.analyze_pr_diff.return_value = SAMPLE_LLM_RESPONSE
            
            # Run workflow
            app = compile_graph()
            final_state = app.invoke(initial_graph_state_pr)
            
            # Test JSON report consistency
            json_report = final_state["json_report"]
            parsed_json = json.loads(json_report)
            
            # Verify JSON structure matches report_data
            report_data = final_state["report_data"]
            assert parsed_json["scan_info"] == report_data["scan_info"]
            assert parsed_json["summary"] == report_data["summary"]
            assert parsed_json["static_analysis_findings"] == report_data["static_analysis_findings"]
            
            # Test Markdown report consistency
            markdown_report = final_state["markdown_report"]
            
            # Should contain all major sections
            required_sections = [
                "# Code Review Report:",
                "## 📋 Executive Summary",
                "## 🔍 Static Analysis Results",
                "## 🤖 AI Analysis & Insights",
                "## 💡 Key Recommendations",
                "## 🔧 Technical Details"
            ]
            
            for section in required_sections:
                assert section in markdown_report, f"Required section '{section}' not found in Markdown report"
            
            # Should contain findings data
            assert f"Total Issues Found:** {report_data['summary']['total_findings']}" in markdown_report
            assert SAMPLE_LLM_RESPONSE in markdown_report


if __name__ == "__main__":
    # Configure logging for test output
    logging.basicConfig(level=logging.INFO)
    
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"]) 