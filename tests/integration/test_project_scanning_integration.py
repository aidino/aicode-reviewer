"""
Integration tests for Project Scanning workflow.

This module tests the complete project scanning workflow including:
- ProjectScanningAgent integration with other agents
- Full project scan workflow through orchestrator
- End-to-end project analysis
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.core_engine.orchestrator import (
    GraphState,
    compile_graph,
    project_scanning_node
)


class TestProjectScanningIntegration:
    """Integration tests for project scanning workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_project_code = {
            "main.py": """
def main():
    print("Hello World")
    user_input = input("Enter your name: ")
    process_user_data(user_input)

def process_user_data(data):
    # Potential security issue: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{data}'"
    return query
""",
            "utils.py": """
import os
import subprocess

def read_file(filename):
    # Potential security issue: path traversal
    with open(filename, 'r') as f:
        return f.read()

def execute_command(cmd):
    # Potential security issue: command injection
    return subprocess.run(cmd, shell=True, capture_output=True)

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        self.data.append(item)
    
    def process_all(self):
        for item in self.data:
            yield item.upper()
""",
            "config.py": """
# Configuration file
DATABASE_URL = "sqlite:///app.db"
SECRET_KEY = "your-secret-key-here"  # Should be in environment variable
DEBUG = True

ALLOWED_HOSTS = ["*"]  # Potential security issue: too permissive
""",
            "tests/test_main.py": """
import unittest
from main import main, process_user_data

class TestMain(unittest.TestCase):
    def test_process_user_data(self):
        result = process_user_data("john")
        self.assertIn("john", result)
"""
        }
        
        self.sample_static_findings = [
            {
                "rule_id": "SQL_INJECTION",
                "severity": "High",
                "category": "Security",
                "message": "Potential SQL injection vulnerability in query construction",
                "file_path": "main.py",
                "line_number": 8,
                "code_snippet": "query = f\"SELECT * FROM users WHERE name = '{data}'\""
            },
            {
                "rule_id": "COMMAND_INJECTION", 
                "severity": "High",
                "category": "Security",
                "message": "Command execution with shell=True poses security risk",
                "file_path": "utils.py",
                "line_number": 12,
                "code_snippet": "subprocess.run(cmd, shell=True, capture_output=True)"
            },
            {
                "rule_id": "PATH_TRAVERSAL",
                "severity": "Medium",
                "category": "Security",
                "message": "Potential path traversal vulnerability",
                "file_path": "utils.py",
                "line_number": 6,
                "code_snippet": "with open(filename, 'r') as f:"
            },
            {
                "rule_id": "HARDCODED_SECRET",
                "severity": "Medium",
                "category": "Security",
                "message": "Hardcoded secret key should be in environment variable",
                "file_path": "config.py",
                "line_number": 3,
                "code_snippet": "SECRET_KEY = \"your-secret-key-here\""
            }
        ]
    
    @patch('src.core_engine.agents.rag_context_agent.RAGContextAgent')
    @patch('src.core_engine.agents.llm_orchestrator_agent.LLMOrchestratorAgent')
    def test_project_scanning_node_full_integration(self, mock_llm_class, mock_rag_class):
        """Test complete project scanning node integration."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_llm.invoke_llm.return_value = """
        ## Architectural Analysis
        
        This is a Python web application with the following characteristics:
        
        **Architecture Pattern**: Simple modular structure with separate concerns
        **Key Components**:
        - Main application logic (main.py)
        - Utility functions (utils.py) 
        - Configuration management (config.py)
        - Basic test coverage (tests/)
        
        **Security Concerns**: Multiple high-severity security vulnerabilities identified
        **Code Quality**: Basic structure with room for improvement in error handling
        """
        
        mock_rag = Mock()
        mock_rag_class.return_value = mock_rag
        mock_rag.query_knowledge_base.return_value = [
            {
                "content": "Database interaction patterns and SQL query construction",
                "file_path": "main.py",
                "score": 0.85
            },
            {
                "content": "File system operations and subprocess execution",
                "file_path": "utils.py", 
                "score": 0.82
            }
        ]
        
        # Create test state
        state = GraphState(
            scan_request_data={"repo_url": "https://github.com/test/project"},
            repo_url="https://github.com/test/project",
            pr_id=None,  # Project scan, not PR scan
            project_code=self.sample_project_code,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=self.sample_static_findings,
            llm_insights=None,
            project_scan_result=None,
            report_data=None,
            markdown_report=None,
            json_report=None,
            error_message=None,
            current_step="project_scanning",
            workflow_metadata={
                "scan_type": "project",
                "total_files": len(self.sample_project_code)
            }
        )
        
        # Execute project scanning node
        result = project_scanning_node(state)
        
        # Verify successful execution
        assert result["current_step"] == "reporting"
        assert "project_scan_result" in result
        assert result["workflow_metadata"]["project_scan_completed"] is True
        
        # Verify project scan result structure
        scan_result = result["project_scan_result"]
        assert "scan_type" in scan_result
        assert "complexity_metrics" in scan_result
        assert "risk_assessment" in scan_result
        assert "recommendations" in scan_result
        assert "architectural_analysis" in scan_result
        
        # Verify complexity metrics
        complexity = scan_result["complexity_metrics"]
        assert complexity["total_files"] == 4
        assert complexity["total_lines"] > 0
        assert "python" in complexity["languages"]
        
        # Verify risk assessment 
        risk_assessment = scan_result["risk_assessment"]
        assert "overall_risk_level" in risk_assessment
        assert "security_issues_count" in risk_assessment
        assert risk_assessment["security_issues_count"] == 4  # Our sample findings
        
        # Verify recommendations are generated
        recommendations = scan_result["recommendations"]
        assert len(recommendations) > 0
        assert any("security" in rec["title"].lower() for rec in recommendations)
        
        # Verify architectural analysis
        assert "Architectural Analysis" in scan_result["architectural_analysis"]
        
        # Verify LLM was called for architectural analysis
        mock_llm.invoke_llm.assert_called()
        
        # Verify RAG context was built and queried
        mock_rag.build_knowledge_base.assert_called_once_with(self.sample_project_code)
        mock_rag.query_knowledge_base.assert_called()
    
    @patch('src.core_engine.agents.project_scanning_agent.ProjectScanningAgent')
    def test_project_scanning_node_error_handling(self, mock_agent_class):
        """Test project scanning node error handling."""
        # Setup mock to raise exception
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.scan_entire_project.side_effect = Exception("Scanning failed")
        
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/project",
            pr_id=None,
            project_code=self.sample_project_code,
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=[],
            llm_insights=None,
            project_scan_result=None,
            report_data=None,
            markdown_report=None,
            json_report=None,
            error_message=None,
            current_step="project_scanning",
            workflow_metadata={}
        )
        
        # Execute and verify error handling
        result = project_scanning_node(state)
        
        assert result["current_step"] == "error"
        assert "Failed to scan project" in result["error_message"]
        assert "Scanning failed" in result["error_message"]
    
    def test_project_scanning_node_no_project_code(self):
        """Test project scanning node with no project code."""
        state = GraphState(
            scan_request_data={},
            repo_url="https://github.com/test/project",
            pr_id=None,
            project_code={},  # Empty project code
            pr_diff=None,
            parsed_asts=None,
            static_analysis_findings=[],
            llm_insights=None,
            project_scan_result=None,
            report_data=None,
            markdown_report=None,
            json_report=None,
            error_message=None,
            current_step="project_scanning",
            workflow_metadata={}
        )
        
        # Execute and verify error handling
        result = project_scanning_node(state)
        
        assert result["current_step"] == "error"
        assert "No project code available for scanning" in result["error_message"]
    
    @pytest.mark.integration
    def test_graph_compilation_with_project_scanning(self):
        """Test that the graph compiles successfully with project scanning node."""
        # This tests that all nodes and edges are properly configured
        app = compile_graph()
        
        # Verify the app is compiled and ready
        assert app is not None
        assert hasattr(app, 'invoke')
        
        # The graph should include project_scanning node and related edges
        # This is a structural test to ensure integration is complete


class TestProjectScanningWorkflowScenarios:
    """Test different project scanning workflow scenarios."""
    
    def test_small_project_direct_analysis(self):
        """Test that small projects use direct analysis instead of hierarchical."""
        # Create a small project (< 10 files)
        small_project = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass"
        }
        
        from src.core_engine.agents.project_scanning_agent import ProjectScanningAgent
        
        with patch.object(ProjectScanningAgent, '_analyze_project_architecture') as mock_analyze:
            mock_analyze.return_value = "Direct analysis result"
            
            agent = ProjectScanningAgent()
            
            # Should detect small project and use direct analysis
            with patch.object(agent, '_hierarchical_summarize') as mock_hierarchical:
                mock_hierarchical.return_value = {}
                
                result = agent.scan_entire_project(small_project, [])
                
                # Should not call hierarchical summarization for small projects
                mock_hierarchical.assert_not_called()
    
    def test_large_project_hierarchical_analysis(self):
        """Test that large projects use hierarchical analysis."""
        # Create a large project (> 50 files)
        large_project = {f"module_{i}.py": f"def func_{i}(): pass" for i in range(60)}
        
        from src.core_engine.agents.project_scanning_agent import ProjectScanningAgent
        
        with patch.object(ProjectScanningAgent, '_hierarchical_summarize') as mock_hierarchical:
            mock_hierarchical.return_value = {
                "file_summaries": {},
                "directory_summaries": {},
                "project_summary": {}
            }
            
            with patch.object(ProjectScanningAgent, '_analyze_project_architecture') as mock_analyze:
                mock_analyze.return_value = "Hierarchical analysis result"
                
                agent = ProjectScanningAgent()
                result = agent.scan_entire_project(large_project, [])
                
                # Should call hierarchical summarization for large projects (3 times: file, directory, project levels)
                assert mock_hierarchical.call_count == 3
                
                # Verify the calls are for different levels
                call_args = [call.args[1] for call in mock_hierarchical.call_args_list]
                assert 'file' in call_args
                assert 'directory' in call_args
                assert 'project' in call_args


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"]) 