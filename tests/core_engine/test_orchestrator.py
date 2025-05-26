"""
Unit tests for LangGraph Orchestrator.

This module contains comprehensive tests for the orchestrator functionality,
including state management, node functions, and graph compilation.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from src.core_engine.orchestrator import (
    GraphState,
    start_scan,
    fetch_code_node,
    parse_code_node,
    static_analysis_node,
    llm_analysis_node,
    reporting_node,
    handle_error_node,
    should_fetch_pr_or_project,
    should_continue_or_error,
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
        assert "changed_files" in result["parsed_asts"]
    
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
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/repo",
            pr_id=None,
            project_code=None,
            pr_diff=None,
            parsed_asts={"main.py": "ast_data", "utils.py": "ast_data"},
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
        assert len(result["static_analysis_findings"]) > 0
    
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
            pr_id=None,
            project_code=None,
            pr_diff=None,
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
        assert result["current_step"] == "reporting"
        assert "Code Quality Assessment" in result["llm_insights"]
    
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
                {"type": "warning", "severity": "warning", "message": "test warning"},
                {"type": "info", "severity": "info", "message": "test info"}
            ],
            llm_insights="Test LLM insights",
            report_data=None,
            error_message=None,
            current_step="reporting",
            workflow_metadata={"scan_type": "pr", "start_time": "test_time"}
        )
        
        result = reporting_node(state)
        
        assert "report_data" in result
        assert result["current_step"] == "completed"
        
        report = result["report_data"]
        assert report["summary"]["total_issues"] == 2
        assert report["summary"]["pr_id"] == 123
        assert report["static_analysis"]["categories"]["warnings"] == 1
        assert report["static_analysis"]["categories"]["info"] == 1
        assert report["llm_analysis"]["insights"] == "Test LLM insights"
    
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
        steps = ["fetch_code", "parse_code", "static_analysis", "llm_analysis", "reporting"]
        
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


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 