"""
Unit tests for ReportingAgent.

This module contains comprehensive tests for the ReportingAgent class,
including tests for report data generation, Markdown formatting, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.core_engine.agents.reporting_agent import ReportingAgent
from src.core_engine.diagramming_engine import DiagrammingEngine


class TestReportingAgent:
    """Test cases for ReportingAgent class."""
    
    @pytest.fixture
    def sample_static_findings(self):
        """Sample static analysis findings for testing."""
        return [
            {
                "rule_id": "PDB_TRACE_FOUND",
                "message": "pdb.set_trace() found",
                "line": 10,
                "column": 5,
                "severity": "Warning",
                "category": "debugging",
                "file": "main.py",
                "suggestion": "Remove pdb.set_trace() before production"
            },
            {
                "rule_id": "PRINT_STATEMENT_FOUND",
                "message": "print() statement found",
                "line": 15,
                "column": 1,
                "severity": "Info",
                "category": "logging",
                "file": "utils.py",
                "suggestion": "Use proper logging instead of print()"
            },
            {
                "rule_id": "FUNCTION_TOO_LONG",
                "message": "Function is 75 lines long",
                "line": 20,
                "column": 1,
                "severity": "Warning",
                "category": "complexity",
                "file": "main.py",
                "suggestion": "Break down function into smaller components"
            }
        ]
    
    @pytest.fixture
    def sample_llm_insights(self):
        """Sample LLM insights for testing."""
        return """# Mock LLM Analysis Results

## Code Quality Assessment
- The code structure appears well-organized
- Variable naming follows conventions

## Security Considerations
- Debugging statements detected that should not be in production
- Remove all pdb.set_trace() calls before deployment

## Performance Analysis
- Performance concerns detected
- Large functions may impact maintainability

## Best Practices
- Logging issues detected
- Replace print() statements with proper logging

## Specific Recommendations
1. Remove debugging statements
2. Implement proper logging
3. Refactor large functions"""
    
    @pytest.fixture
    def sample_scan_details(self):
        """Sample scan details for testing."""
        return {
            "repo_url": "https://github.com/test/repo",
            "pr_id": 123,
            "branch": "feature/test",
            "scan_type": "pr",
            "total_files": 5,
            "successful_parses": 4,
            "scan_id": "test_scan_123"
        }
    
    def test_init(self):
        """Test ReportingAgent initialization."""
        agent = ReportingAgent()
        
        assert agent.supported_formats == ['json', 'markdown', 'html']
        assert agent.report_version == "1.0.0"
    
    def test_generate_report_data_complete(self, sample_static_findings, sample_llm_insights, sample_scan_details):
        """Test complete report data generation."""
        agent = ReportingAgent()
        
        report_data = agent.generate_report_data(
            static_findings=sample_static_findings,
            llm_insights=sample_llm_insights,
            scan_details=sample_scan_details
        )
        
        # Check overall structure
        assert "scan_info" in report_data
        assert "summary" in report_data
        assert "static_analysis_findings" in report_data
        assert "llm_review" in report_data
        assert "diagrams" in report_data
        assert "metadata" in report_data
        
        # Check scan info
        scan_info = report_data["scan_info"]
        assert scan_info["repository"] == "https://github.com/test/repo"
        assert scan_info["pr_id"] == 123
        assert scan_info["scan_type"] == "pr"
        assert scan_info["report_version"] == "1.0.0"
        
        # Check summary
        summary = report_data["summary"]
        assert summary["total_findings"] == 3
        assert summary["scan_status"] == "completed"
        assert summary["has_llm_analysis"] is True
        
        # Check severity breakdown
        severity_breakdown = summary["severity_breakdown"]
        assert severity_breakdown["Warning"] == 2
        assert severity_breakdown["Info"] == 1
        assert severity_breakdown["Error"] == 0
        
        # Check category breakdown
        category_breakdown = summary["category_breakdown"]
        assert category_breakdown["debugging"] == 1
        assert category_breakdown["logging"] == 1
        assert category_breakdown["complexity"] == 1
        
        # Check static analysis findings
        assert report_data["static_analysis_findings"] == sample_static_findings
        
        # Check LLM review
        llm_review = report_data["llm_review"]
        assert llm_review["insights"] == sample_llm_insights
        assert llm_review["has_content"] is True
        assert "sections" in llm_review
    
    def test_generate_report_data_empty_findings(self, sample_scan_details):
        """Test report generation with no findings."""
        agent = ReportingAgent()
        
        report_data = agent.generate_report_data(
            static_findings=[],
            llm_insights="",
            scan_details=sample_scan_details
        )
        
        summary = report_data["summary"]
        assert summary["total_findings"] == 0
        assert summary["has_llm_analysis"] is False
        assert summary["severity_breakdown"]["Warning"] == 0
        assert summary["severity_breakdown"]["Info"] == 0
        assert summary["severity_breakdown"]["Error"] == 0
    
    def test_generate_report_data_error_handling(self):
        """Test error handling in report data generation."""
        agent = ReportingAgent()
        
        # Test with invalid input
        report_data = agent.generate_report_data(
            static_findings=None,  # Invalid input
            llm_insights="test",
            scan_details={}
        )
        
        # Should still return a valid structure
        assert "scan_info" in report_data
        assert "summary" in report_data
        assert report_data["summary"]["total_findings"] == 0
    
    def test_calculate_severity_stats(self, sample_static_findings):
        """Test severity statistics calculation."""
        agent = ReportingAgent()
        
        stats = agent._calculate_severity_stats(sample_static_findings)
        
        assert stats["Warning"] == 2
        assert stats["Info"] == 1
        assert stats["Error"] == 0
        assert stats["Unknown"] == 0
    
    def test_calculate_category_stats(self, sample_static_findings):
        """Test category statistics calculation."""
        agent = ReportingAgent()
        
        stats = agent._calculate_category_stats(sample_static_findings)
        
        assert stats["debugging"] == 1
        assert stats["logging"] == 1
        assert stats["complexity"] == 1
    
    def test_process_llm_insights(self, sample_llm_insights):
        """Test LLM insights processing."""
        agent = ReportingAgent()
        
        processed = agent._process_llm_insights(sample_llm_insights)
        
        assert processed["has_content"] is True
        assert processed["insights"] == sample_llm_insights
        assert "sections" in processed
        assert "word_count" in processed
        assert "line_count" in processed
        
        # Check sections parsing
        sections = processed["sections"]
        assert "code_quality_assessment" in sections
        assert "security_considerations" in sections
        assert "specific_recommendations" in sections
    
    def test_process_llm_insights_empty(self):
        """Test processing empty LLM insights."""
        agent = ReportingAgent()
        
        processed = agent._process_llm_insights("")
        
        assert processed["has_content"] is False
        assert processed["insights"] == ""
    
    def test_format_markdown_report_complete(self, sample_static_findings, sample_llm_insights, sample_scan_details):
        """Test complete Markdown report formatting."""
        agent = ReportingAgent()
        
        # Generate report data first
        report_data = agent.generate_report_data(
            static_findings=sample_static_findings,
            llm_insights=sample_llm_insights,
            scan_details=sample_scan_details
        )
        
        # Format as Markdown
        markdown = agent.format_markdown_report(report_data)
        
        # Check main sections
        assert "# Code Review Report:" in markdown
        assert "## 📋 Executive Summary" in markdown
        assert "## 🔍 Static Analysis Results" in markdown
        assert "## 🤖 AI Analysis & Insights" in markdown
        assert "## 💡 Key Recommendations" in markdown
        assert "## 🔧 Technical Details" in markdown
        
        # Check content
        assert "Total Issues Found:** 3" in markdown
        assert "PDB_TRACE_FOUND" in markdown
        assert "PRINT_STATEMENT_FOUND" in markdown
        assert "FUNCTION_TOO_LONG" in markdown
        assert "main.py" in markdown
        assert "utils.py" in markdown
    
    def test_format_markdown_report_no_findings(self, sample_scan_details):
        """Test Markdown formatting with no findings."""
        agent = ReportingAgent()
        
        report_data = agent.generate_report_data(
            static_findings=[],
            llm_insights="",
            scan_details=sample_scan_details
        )
        
        markdown = agent.format_markdown_report(report_data)
        
        assert "✅ **No issues found!**" in markdown
        assert "No static analysis issues detected" in markdown
    
    def test_format_header(self, sample_scan_details):
        """Test header formatting."""
        agent = ReportingAgent()
        
        scan_info = {
            "repository": "https://github.com/test/repo",
            "pr_id": 123,
            "scan_type": "pr",
            "scan_id": "test_123",
            "timestamp": "2023-01-01T12:00:00",
            "report_version": "1.0.0",
            "branch": "main"
        }
        
        header = agent._format_header(scan_info)
        
        assert "# Code Review Report: repo - PR #123" in header
        assert "**Scan ID:** `test_123`" in header
        assert "**Repository:** https://github.com/test/repo" in header
        assert "**Pull Request:** #123" in header
        assert "**Branch:** `main`" in header
    
    def test_format_summary(self, sample_scan_details):
        """Test summary formatting."""
        agent = ReportingAgent()
        
        summary = {
            "total_findings": 5,
            "severity_breakdown": {"Warning": 3, "Info": 2, "Error": 0},
            "has_llm_analysis": True
        }
        
        scan_info = {"scan_type": "pr"}
        
        summary_md = agent._format_summary(summary, scan_info)
        
        assert "📊 **Total Issues Found:** 5" in summary_md
        assert "🟡 **Warning:** 3" in summary_md
        assert "🔵 **Info:** 2" in summary_md
        assert "🔍 **Analysis Type:** Pull Request review" in summary_md
        assert "🤖 **AI Analysis:** Included" in summary_md
    
    def test_format_static_findings(self, sample_static_findings):
        """Test static findings formatting."""
        agent = ReportingAgent()
        
        summary = {
            "category_breakdown": {"debugging": 1, "logging": 1, "complexity": 1}
        }
        
        findings_md = agent._format_static_findings(sample_static_findings, summary)
        
        assert "## 🔍 Static Analysis Results" in findings_md
        assert "### Findings by Category" in findings_md
        assert "🐛 **Debugging:** 1 issue(s)" in findings_md
        assert "📝 **Logging:** 1 issue(s)" in findings_md
        assert "⚡ **Complexity:** 1 issue(s)" in findings_md
        assert "#### 📄 `main.py`" in findings_md
        assert "#### 📄 `utils.py`" in findings_md
        assert "**🟡 PDB_TRACE_FOUND**" in findings_md
    
    def test_format_llm_insights(self, sample_llm_insights):
        """Test LLM insights formatting."""
        agent = ReportingAgent()
        
        llm_review = {
            "insights": sample_llm_insights,
            "word_count": 50
        }
        
        insights_md = agent._format_llm_insights(llm_review)
        
        assert "## 🤖 AI Analysis & Insights" in insights_md
        assert sample_llm_insights in insights_md
        assert "Analysis contains 50 words" in insights_md
    
    def test_format_recommendations(self, sample_static_findings):
        """Test recommendations formatting."""
        agent = ReportingAgent()
        
        llm_review = {
            "sections": {
                "specific_recommendations": "1. Remove debugging statements\n2. Use proper logging"
            }
        }
        
        rec_md = agent._format_recommendations(sample_static_findings, llm_review)
        
        assert "## 💡 Key Recommendations" in rec_md
        assert "### From AI Analysis" in rec_md
        assert "### From Static Analysis" in rec_md
        assert "Remove pdb.set_trace() before production" in rec_md
    
    def test_format_technical_details(self):
        """Test technical details formatting."""
        agent = ReportingAgent()
        
        metadata = {
            "total_files_analyzed": 10,
            "successful_parses": 9,
            "generation_time": "2023-01-01T12:00:00",
            "agent_versions": {
                "reporting_agent": "1.0.0",
                "static_analysis": "1.0.0"
            }
        }
        
        tech_md = agent._format_technical_details(metadata)
        
        assert "## 🔧 Technical Details" in tech_md
        assert "**Files Analyzed:** 10" in tech_md
        assert "**Successfully Parsed:** 9" in tech_md
        assert "### Agent Versions" in tech_md
        assert "**Reporting Agent:** 1.0.0" in tech_md
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        agent = ReportingAgent()
        
        # Test valid ISO timestamp
        formatted = agent._format_timestamp("2023-01-01T12:00:00")
        assert "2023-01-01 12:00:00 UTC" in formatted
        
        # Test empty timestamp
        formatted = agent._format_timestamp("")
        assert formatted == "Unknown"
        
        # Test invalid timestamp
        formatted = agent._format_timestamp("invalid")
        assert formatted == "invalid"
    
    def test_export_json(self, sample_static_findings, sample_llm_insights, sample_scan_details):
        """Test JSON export functionality."""
        agent = ReportingAgent()
        
        report_data = agent.generate_report_data(
            static_findings=sample_static_findings,
            llm_insights=sample_llm_insights,
            scan_details=sample_scan_details
        )
        
        json_str = agent.export_json(report_data)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        
        assert parsed["summary"]["total_findings"] == 3
        assert parsed["scan_info"]["repository"] == "https://github.com/test/repo"
        assert len(parsed["static_analysis_findings"]) == 3
    
    def test_export_json_error(self):
        """Test JSON export error handling."""
        agent = ReportingAgent()
        
        # Create data that can't be serialized
        invalid_data = {"circular": None}
        invalid_data["circular"] = invalid_data  # Circular reference
        
        json_str = agent.export_json(invalid_data)
        
        # Should return error JSON
        parsed = json.loads(json_str)
        assert "error" in parsed
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        agent = ReportingAgent()
        
        formats = agent.get_supported_formats()
        
        assert formats == ['json', 'markdown', 'html']
        # Ensure it returns a copy
        formats.append('pdf')
        assert agent.supported_formats == ['json', 'markdown', 'html']
    
    def test_error_report_generation(self):
        """Test error report generation."""
        agent = ReportingAgent()
        
        error_report = agent._generate_error_report("Test error", {"repo_url": "test"})
        
        assert error_report["scan_info"]["scan_type"] == "error"
        assert error_report["summary"]["scan_status"] == "error"
        assert error_report["summary"]["error_message"] == "Test error"
        assert error_report["summary"]["total_findings"] == 0
    
    def test_error_markdown_generation(self):
        """Test error Markdown generation."""
        agent = ReportingAgent()
        
        error_md = agent._generate_error_markdown("Test error", {})
        
        assert "# Code Review Report - Error" in error_md
        assert "❌ Report Generation Error" in error_md
        assert "**Error:** Test error" in error_md
    
    def test_format_markdown_report_error(self):
        """Test Markdown formatting error handling."""
        agent = ReportingAgent()
        
        # Test with malformed report data
        with patch.object(agent, '_format_header', side_effect=Exception("Test error")):
            markdown = agent.format_markdown_report({})
            
            assert "Code Review Report - Error" in markdown
            assert "Test error" in markdown
    
    def test_severity_stats_unknown(self):
        """Test severity stats with unknown severity."""
        agent = ReportingAgent()
        
        findings = [
            {"severity": "Critical"},  # Unknown severity
            {"severity": "Warning"},
            {}  # No severity
        ]
        
        stats = agent._calculate_severity_stats(findings)
        
        assert stats["Warning"] == 1
        assert stats["Unknown"] == 2
    
    def test_category_stats_missing(self):
        """Test category stats with missing categories."""
        agent = ReportingAgent()
        
        findings = [
            {"category": "test"},
            {}  # No category
        ]
        
        stats = agent._calculate_category_stats(findings)
        
        assert stats["test"] == 1
        assert stats["uncategorized"] == 1
    
    def test_init_with_diagramming_engine(self):
        """Test ReportingAgent initialization with custom DiagrammingEngine."""
        mock_engine = Mock(spec=DiagrammingEngine)
        agent = ReportingAgent(diagramming_engine=mock_engine)
        
        assert agent.diagramming_engine == mock_engine
    
    def test_generate_diagrams_with_code_files(self, sample_static_findings):
        """Test diagram generation with code files."""
        agent = ReportingAgent()
        
        # Mock AST data
        mock_ast = Mock()
        mock_ast.root_node = Mock()
        
        code_files = {
            'test.py': mock_ast,
            'models.py': mock_ast
        }
        
        with patch.object(agent.diagramming_engine, 'generate_class_diagram') as mock_generate:
            mock_generate.side_effect = [
                '@startuml\nclass TestClass\n@enduml',  # PlantUML
                'classDiagram\n  class TestClass'  # Mermaid
            ]
            
            diagrams = agent._generate_diagrams(code_files, sample_static_findings)
            
            assert len(diagrams) == 2
            
            # Check PlantUML diagram
            plantuml_diagram = diagrams[0]
            assert plantuml_diagram['type'] == 'class_diagram'
            assert plantuml_diagram['language'] == 'python'
            assert plantuml_diagram['format'] == 'plantuml'
            assert '@startuml' in plantuml_diagram['content']
            assert 'test.py' in plantuml_diagram['files_included']
            assert 'models.py' in plantuml_diagram['files_included']
            
            # Check Mermaid diagram
            mermaid_diagram = diagrams[1]
            assert mermaid_diagram['type'] == 'class_diagram'
            assert mermaid_diagram['language'] == 'python'
            assert mermaid_diagram['format'] == 'mermaid'
            assert 'classDiagram' in mermaid_diagram['content']
            
            # Should have been called twice
            assert mock_generate.call_count == 2
    
    def test_generate_diagrams_no_code_files(self):
        """Test diagram generation with no code files."""
        agent = ReportingAgent()
        
        diagrams = agent._generate_diagrams(None, [])
        
        assert diagrams == []
    
    def test_generate_diagrams_error_handling(self, sample_static_findings):
        """Test diagram generation error handling."""
        agent = ReportingAgent()
        
        # Mock AST data
        mock_ast = Mock()
        mock_ast.root_node = Mock()
        
        code_files = {'test.py': mock_ast}
        
        with patch.object(agent.diagramming_engine, 'generate_class_diagram') as mock_generate:
            mock_generate.side_effect = Exception("Test error")
            
            diagrams = agent._generate_diagrams(code_files, sample_static_findings)
            
            assert len(diagrams) == 1
            assert diagrams[0]['type'] == 'error'
            assert 'Test error' in diagrams[0]['content']
    
    def test_generate_diagrams_non_python_files(self):
        """Test diagram generation with non-Python files."""
        agent = ReportingAgent()
        
        # Mock AST data for non-Python files
        mock_ast = Mock()
        mock_ast.root_node = Mock()
        
        code_files = {
            'test.java': mock_ast,
            'test.js': mock_ast
        }
        
        with patch.object(agent.diagramming_engine, 'generate_class_diagram') as mock_generate:
            diagrams = agent._generate_diagrams(code_files, [])
            
            # Should not generate diagrams for non-Python files
            assert diagrams == []
            assert mock_generate.call_count == 0
    
    def test_generate_report_data_with_diagrams(self, sample_static_findings, sample_llm_insights, sample_scan_details):
        """Test report data generation with diagram integration."""
        agent = ReportingAgent()
        
        # Mock AST data
        mock_ast = Mock()
        mock_ast.root_node = Mock()
        
        code_files = {'test.py': mock_ast}
        
        with patch.object(agent, '_generate_diagrams') as mock_generate_diagrams:
            mock_generate_diagrams.return_value = [
                {
                    'type': 'class_diagram',
                    'format': 'plantuml',
                    'content': '@startuml\nclass TestClass\n@enduml'
                }
            ]
            
            report_data = agent.generate_report_data(
                static_findings=sample_static_findings,
                llm_insights=sample_llm_insights,
                scan_details=sample_scan_details,
                code_files=code_files
            )
            
            # Check that diagrams are included
            assert "diagrams" in report_data
            assert len(report_data["diagrams"]) == 1
            assert report_data["diagrams"][0]['type'] == 'class_diagram'
            
            # Verify _generate_diagrams was called with correct parameters
            mock_generate_diagrams.assert_called_once_with(code_files, sample_static_findings)
    
    def test_diagram_engine_format_switching(self, sample_static_findings):
        """Test that diagram engine format is properly switched during generation."""
        mock_engine = Mock(spec=DiagrammingEngine)
        agent = ReportingAgent(diagramming_engine=mock_engine)
        
        # Mock AST data
        mock_ast = Mock()
        mock_ast.root_node = Mock()
        
        code_files = {'test.py': mock_ast}
        
        mock_engine.generate_class_diagram.side_effect = [
            '@startuml\nclass TestClass\n@enduml',  # PlantUML
            'classDiagram\n  class TestClass'  # Mermaid
        ]
        
        diagrams = agent._generate_diagrams(code_files, sample_static_findings)
        
        # Verify format switching calls
        calls = mock_engine.set_diagram_format.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == 'mermaid'  # Switch to Mermaid
        assert calls[1][0][0] == 'plantuml'  # Reset to PlantUML
        
        # Verify generate_class_diagram was called twice
        assert mock_engine.generate_class_diagram.call_count == 2 