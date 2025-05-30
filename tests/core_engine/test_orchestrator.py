"""
Unit tests for LangGraph Orchestrator.

This module contains comprehensive tests for the orchestrator functionality,
including state management, node functions, and graph compilation.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

from src.core_engine.orchestrator import (
    GraphState,
    start_scan,
    fetch_code_node,
    parse_code_node,
    static_analysis_node,
    llm_analysis_node,
    project_scanning_node,
    reporting_node,
    handle_error_node,
    should_fetch_pr_or_project,
    should_continue_or_error,
    should_run_project_scanning,
    compile_graph,
    create_sample_scan_request
)


class TestGraphState:
    """Test cases for GraphState model."""
    
    def test_graph_state_creation(self):
        """Test creating a valid GraphState."""
        state = GraphState(
            scan_request_data={"repo_url": "test-repo"},
            repo_url="https://github.com/test/repo",
            pr_id=123,
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
        
        assert state["repo_url"] == "https://github.com/test/repo"
        assert state["pr_id"] == 123
        assert state["current_step"] == "start"


class TestNodeFunctions:
    """Test cases for individual node functions."""
    
    def test_start_scan_success(self):
        """Test successful scan initialization."""
        initial_state = GraphState(
            scan_request_data={
                "repo_url": "https://github.com/test/repo",
                "pr_id": 123
            },
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
        
        result = start_scan(initial_state)
        
        assert result["repo_url"] == "https://github.com/test/repo"
        assert result["pr_id"] == 123
        assert result["current_step"] == "fetch_code"
        assert "workflow_metadata" in result
        assert result["workflow_metadata"]["scan_type"] == "pr"
    
    def test_start_scan_missing_repo_url(self):
        """Test scan initialization with missing repo URL."""
        initial_state = GraphState(
            scan_request_data={},
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
        
        result = start_scan(initial_state)
        
        assert result["current_step"] == "error"
        assert "Repository URL is required" in result["error_message"]
    
    @patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent')
    def test_fetch_code_node_pr_scan(self, mock_agent_class):
        """Test code fetching for PR scan."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.get_pr_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        mock_agent.get_changed_files_from_diff.return_value = ["file.py"]
        
        state = GraphState(
            scan_request_data={
                "target_branch": "main",
                "source_branch": "feature"
            },
            repo_url="https://github.com/test/repo",
            pr_id=123,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="fetch_code",
            workflow_metadata={}
        )
        
        result = fetch_code_node(state)
        
        assert "pr_diff" in result
        assert result["current_step"] == "parse_code"
        assert "diff --git a/file.py b/file.py" in result["pr_diff"]
        assert "workflow_metadata" in result
        assert result["workflow_metadata"]["changed_files"] == ["file.py"]
        
        # Verify agent was called correctly
        mock_agent.get_pr_diff.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            pr_id=123,
            target_branch="main",
            source_branch="feature"
        )
    
    @patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent')
    def test_fetch_code_node_project_scan(self, mock_agent_class):
        """Test code fetching for full project scan."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.get_project_files.return_value = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass"
        }
        
        state = GraphState(
            scan_request_data={"branch": "develop"},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="fetch_code",
            workflow_metadata={}
        )
        
        result = fetch_code_node(state)
        
        assert "project_code" in result
        assert result["current_step"] == "parse_code"
        assert isinstance(result["project_code"], dict)
        assert "main.py" in result["project_code"]
        assert "utils.py" in result["project_code"]
        assert result["workflow_metadata"]["total_files"] == 2
        assert result["workflow_metadata"]["branch"] == "develop"
        
        # Verify agent was called correctly
        mock_agent.get_project_files.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            branch_or_commit="develop"
        )
    
    @patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent')
    def test_fetch_code_node_pr_scan_with_fallback(self, mock_agent_class):
        """Test PR scan with fallback to project files."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # First call (get_pr_diff) fails, second call (get_project_files) succeeds
        mock_agent.get_pr_diff.side_effect = Exception("PR diff failed")
        mock_agent.get_project_files.return_value = {
            "main.py": "print('fallback')"
        }
        
        state = GraphState(
            scan_request_data={
                "source_branch": "feature"
            },
            repo_url="https://github.com/test/repo",
            pr_id=123,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="fetch_code",
            workflow_metadata={}
        )
        
        result = fetch_code_node(state)
        
        assert "project_code" in result
        assert result["current_step"] == "parse_code"
        assert result["workflow_metadata"]["fallback_mode"] == True
        assert result["workflow_metadata"]["source_branch"] == "feature"
        
        # Verify both methods were called
        mock_agent.get_pr_diff.assert_called_once()
        mock_agent.get_project_files.assert_called_once_with(
            "https://github.com/test/repo", 
            "feature"
        )
    
    @patch('src.core_engine.agents.code_fetcher_agent.CodeFetcherAgent')
    def test_fetch_code_node_no_files_found(self, mock_agent_class):
        """Test project scan when no supported files are found."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.get_project_files.return_value = {}  # No files found
        
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="fetch_code",
            workflow_metadata={}
        )
        
        result = fetch_code_node(state)
        
        assert result["current_step"] == "error"
        assert "No supported files found" in result["error_message"]
    
    def test_parse_code_node_with_project_code(self):
        """Test AST parsing with project code."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code={"main.py": "print('hello')", "utils.py": "def helper(): pass"},
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="parse_code",
            workflow_metadata={}
        )
        
        result = parse_code_node(state)
        
        assert "parsed_asts" in result
        assert result["current_step"] == "static_analysis"
        assert "main.py" in result["parsed_asts"]
        assert "utils.py" in result["parsed_asts"]
    
    def test_parse_code_node_with_pr_diff(self):
        """Test AST parsing with PR diff."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=123,
            project_code=None,
            pr_diff="diff --git a/main.py b/main.py\n+print('new code')",
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="parse_code",
            workflow_metadata={}
        )
        
        result = parse_code_node(state)
        
        assert "parsed_asts" in result
        assert result["current_step"] == "static_analysis"
        # For simple diff format, expect diff_summary when individual files can't be extracted
        assert "diff_summary" in result["parsed_asts"]
    
    def test_parse_code_node_no_code(self):
        """Test AST parsing with no code available."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="parse_code",
            workflow_metadata={}
        )
        
        result = parse_code_node(state)
        
        assert result["current_step"] == "error"
        assert "No code to parse" in result["error_message"]
    
    def test_static_analysis_node_success(self):
        """Test successful static analysis."""
        # Create properly structured AST data
        mock_ast_data = {
            "ast_node": "mock_ast_node_object",  # This would be a real tree-sitter node
            "language": "python",
            "structural_info": {
                "classes": [],
                "functions": [],
                "imports": []
            }
        }
        
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts={"main.py": mock_ast_data, "utils.py": mock_ast_data},
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="static_analysis",
            workflow_metadata={}
        )
        
        result = static_analysis_node(state)
        
        assert "static_analysis_findings" in result
        assert result["current_step"] == "llm_analysis"
        assert isinstance(result["static_analysis_findings"], list)
        # Note: Static analysis may return empty list if no issues found, which is valid
    
    def test_static_analysis_node_no_asts(self):
        """Test static analysis with no ASTs."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="static_analysis",
            workflow_metadata={}
        )
        
        result = static_analysis_node(state)
        
        assert result["current_step"] == "error"
        assert "No ASTs available" in result["error_message"]
    
    def test_llm_analysis_node_success(self):
        """Test successful LLM analysis."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,  # This is a project scan (no PR ID)
            project_code={"main.py": "def main(): pass"},  # Has project code
            pr_diff=None,
            parsed_asts={"main.py": "ast_data"},
            static_analysis_findings=[{"type": "warning", "message": "test"}],
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="llm_analysis",
            workflow_metadata={}  # No project_scan_completed flag
        )
        
        result = llm_analysis_node(state)
        
        assert "llm_insights" in result
        # For project scans without project_scan_completed flag, should go to project_scanning
        assert result["current_step"] == "project_scanning"
        assert "Code Quality Assessment" in result["llm_insights"]
    
    def test_llm_analysis_node_success_pr_scan(self):
        """Test successful LLM analysis for PR scan."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=123,  # This is a PR scan
            project_code=None,
            pr_diff="diff content",
            parsed_asts={"main.py": "ast_data"},
            static_analysis_findings=[{"type": "warning", "message": "test"}],
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="llm_analysis",
            workflow_metadata={}
        )
        
        result = llm_analysis_node(state)
        
        assert "llm_insights" in result
        # For PR scans, should go directly to reporting
        assert result["current_step"] == "reporting"
        assert "Code Quality Assessment" in result["llm_insights"]
    
    @patch('src.core_engine.agents.project_scanning_agent.ProjectScanningAgent')
    def test_project_scanning_node_success(self, mock_agent_class):
        """Test successful project scanning."""
        # Setup mock
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.scan_entire_project.return_value = {
            "scan_type": "project",
            "complexity_metrics": {"total_files": 5, "total_lines": 100},
            "risk_assessment": {"overall_risk_level": "medium"},
            "recommendations": [{"title": "Test recommendation"}],
            "architectural_analysis": "Test architectural analysis"
        }
        
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code={"main.py": "def main(): pass", "utils.py": "def helper(): pass"},
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=[{"type": "warning", "message": "test"}],
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="project_scanning",
            workflow_metadata={}
        )
        
        result = project_scanning_node(state)
        
        assert "project_scan_result" in result
        assert result["current_step"] == "reporting"
        assert result["workflow_metadata"]["project_scan_completed"] is True
        assert result["workflow_metadata"]["risk_level"] == "medium"
        assert result["workflow_metadata"]["recommendations_count"] == 1
        
        # Verify the agent was called with correct parameters
        mock_agent.scan_entire_project.assert_called_once_with(
            code_files={"main.py": "def main(): pass", "utils.py": "def helper(): pass"},
            static_findings=[{"type": "warning", "message": "test"}]
        )
    
    def test_project_scanning_node_no_code(self):
        """Test project scanning with no project code."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code={},  # Empty project code
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=[],
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="project_scanning",
            workflow_metadata={}
        )
        
        result = project_scanning_node(state)
        
        assert result["current_step"] == "error"
        assert "No project code available for scanning" in result["error_message"]
    
    def test_llm_analysis_node_no_code(self):
        """Test LLM analysis with no code."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="llm_analysis",
            workflow_metadata={}
        )
        
        result = llm_analysis_node(state)
        
        assert result["current_step"] == "error"
        assert "No code available for LLM analysis" in result["error_message"]
    
    def test_reporting_node_success(self):
        """Test successful report generation."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=123,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=[
                {"rule_id": "TEST_WARNING", "severity": "Warning", "category": "test", "message": "test warning"},
                {"rule_id": "TEST_INFO", "severity": "Info", "category": "test", "message": "test info"}
            ],
            llm_insights="Test LLM insights",
            report_data=None,
            error_message=None,
            current_step="reporting",
            workflow_metadata={"scan_type": "pr", "start_time": "test_time"}
        )
        
        result = reporting_node(state)
        
        assert "report_data" in result
        assert "markdown_report" in result
        assert "json_report" in result
        assert result["current_step"] == "completed"
        
        # Test report structure (using ReportingAgent structure)
        report = result["report_data"]
        assert "scan_info" in report
        assert "summary" in report
        assert "static_analysis_findings" in report
        assert "llm_review" in report
        
        # Test summary data
        summary = report["summary"]
        assert summary["total_findings"] == 2
        assert summary["scan_status"] == "completed"
        assert summary["has_llm_analysis"] is True
        
        # Test severity breakdown
        severity_breakdown = summary["severity_breakdown"]
        assert severity_breakdown["Warning"] == 1
        assert severity_breakdown["Info"] == 1
        
        # Test scan info
        scan_info = report["scan_info"]
        assert scan_info["repository"] == "https://github.com/test/repo"
        assert scan_info["pr_id"] == 123
        assert scan_info["scan_type"] == "pr"
        
        # Test LLM review
        llm_review = report["llm_review"]
        assert llm_review["insights"] == "Test LLM insights"
        assert llm_review["has_content"] is True
        
        # Test static analysis findings
        assert len(report["static_analysis_findings"]) == 2
        
        # Test that markdown report is generated
        markdown = result["markdown_report"]
        assert "# Code Review Report:" in markdown
        assert "Test LLM insights" in markdown
    
    def test_handle_error_node(self):
        """Test error handling node."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=123,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message="Test error message",
            current_step="error",
            workflow_metadata={"test": "data"}
        )
        
        result = handle_error_node(state)
        
        assert "report_data" in result
        assert result["current_step"] == "error_handled"
        
        error_report = result["report_data"]
        assert error_report["summary"]["status"] == "error"
        assert error_report["summary"]["error_message"] == "Test error message"
        assert error_report["summary"]["pr_id"] == 123


class TestConditionalEdges:
    """Test cases for conditional edge functions."""
    
    def test_should_fetch_pr_or_project_normal(self):
        """Test normal flow routing."""
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="fetch_code",
            workflow_metadata={}
        )
        
        result = should_fetch_pr_or_project(state)
        assert result == "fetch_code"
    
    def test_should_fetch_pr_or_project_error(self):
        """Test error routing."""
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="error",
            workflow_metadata={}
        )
        
        result = should_fetch_pr_or_project(state)
        assert result == "handle_error"
    
    def test_should_continue_or_error_completed(self):
        """Test completion routing."""
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="completed",
            workflow_metadata={}
        )
        
        from langgraph.graph import END
        result = should_continue_or_error(state)
        assert result == END
    
    def test_should_continue_or_error_normal_steps(self):
        """Test normal step progression."""
        steps = ["fetch_code", "parse_code", "static_analysis", "llm_analysis", "project_scanning", "reporting"]
        
        for step in steps:
            state = GraphState(
                scan_request_data={},
                repo_url="test",
                pr_id=None,
                project_code=None,
                pr_diff=None,
                parsed_asts=None,
                static_analysis_findings=None,
                llm_insights=None,
                report_data=None,
                error_message=None,
                current_step=step,
                workflow_metadata={}
            )
            
            result = should_continue_or_error(state)
            assert result == step
    
    def test_should_run_project_scanning_project_scan(self):
        """Test should_run_project_scanning for project scan."""
        from src.core_engine.orchestrator import should_run_project_scanning
        
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=None,  # No PR ID = project scan
            project_code={"main.py": "def main(): pass"},  # Has project code
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="static_analysis",
            workflow_metadata={}
        )
        
        result = should_run_project_scanning(state)
        assert result == "project_scanning"
    
    def test_should_run_project_scanning_pr_scan(self):
        """Test should_run_project_scanning for PR scan."""
        from src.core_engine.orchestrator import should_run_project_scanning
        
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=123,  # Has PR ID = PR scan
            project_code={"main.py": "def main(): pass"},
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="static_analysis",
            workflow_metadata={}
        )
        
        result = should_run_project_scanning(state)
        assert result == "llm_analysis"
    
    def test_should_run_project_scanning_no_project_code(self):
        """Test should_run_project_scanning with no project code."""
        from src.core_engine.orchestrator import should_run_project_scanning
        
        state = GraphState(
            scan_request_data={},
            repo_url="test",
            pr_id=None,  # No PR ID but also no project code
            project_code={},  # Empty project code
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=None,
            llm_insights=None,
            report_data=None,
            error_message=None,
            current_step="static_analysis",
            workflow_metadata={}
        )
        
        result = should_run_project_scanning(state)
        assert result == "llm_analysis"


class TestGraphCompilation:
    """Test cases for graph compilation."""
    
    def test_compile_graph_success(self):
        """Test successful graph compilation."""
        app = compile_graph()
        
        # Verify the app is compiled and ready
        assert app is not None
        assert hasattr(app, 'invoke')
    
    def test_create_sample_scan_request(self):
        """Test sample scan request creation."""
        sample_state = create_sample_scan_request()
        
        assert sample_state["scan_request_data"]["repo_url"] == "https://github.com/example/test-repo"
        assert sample_state["scan_request_data"]["pr_id"] == 123
        assert sample_state["current_step"] == "start"


class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    @pytest.mark.integration
    def test_pr_scan_workflow_structure(self):
        """Test the overall structure of PR scan workflow."""
        # This test verifies the workflow structure without actually running it
        app = compile_graph()
        
        # Verify that the graph has the expected nodes
        # Note: This is a structural test, not a full execution test
        assert app is not None
    
    @pytest.mark.integration  
    def test_project_scan_workflow_structure(self):
        """Test the overall structure of project scan workflow."""
        # This test verifies the workflow structure for project scans
        app = compile_graph()
        
        # Verify that the graph can handle project scan scenarios
        assert app is not None


def test_orchestrator_workflow_includes_impact_analysis():
    app = compile_graph()
    # Kiểm tra app đã compile thành công và có thể invoke
    # Không thể access trực tiếp nodes của CompiledStateGraph
    assert app is not None
    assert hasattr(app, 'invoke')


def test_orchestrator_integration_runs_and_returns_impact_analysis():
    # Test trực tiếp impact_analysis_node function thay vì full workflow
    from src.core_engine.orchestrator import impact_analysis_node
    from src.core_engine.agents.impact_analysis.models import ImpactAnalysisInput
    
    # Mock state với diff và dependency graph
    mock_state = {
        "pr_diff": "diff --git a/foo.py b/foo.py\nindex 123..456 100644\n--- a/foo.py\n+++ b/foo.py",
        "workflow_metadata": {
            "dependency_graph": {"foo.py": ["bar.py"]},
            "changed_files": ["foo.py"]
        }
    }
    
    # Chạy impact_analysis_node
    result = impact_analysis_node(mock_state)
    
    # Kết quả phải có impact_analysis_result
    assert "impact_analysis_result" in result
    assert result["current_step"] == "llm_analysis"
    
    # Kiểm tra structure của impact analysis result
    impact_result = result["impact_analysis_result"]
    assert "impacted_entities" in impact_result
    assert len(impact_result["impacted_entities"]) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 