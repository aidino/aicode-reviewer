"""
Unit tests for ProjectScanningAgent.

This module contains comprehensive tests for the ProjectScanningAgent
including hierarchical summarization, project scanning, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

from src.core_engine.agents.project_scanning_agent import ProjectScanningAgent
from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent
from src.core_engine.agents.rag_context_agent import RAGContextAgent


class TestProjectScanningAgentInit:
    """Test ProjectScanningAgent initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        agent = ProjectScanningAgent()
        
        assert agent.max_files_for_direct_analysis == 50
        assert agent.max_lines_per_summary == 500
        assert isinstance(agent.llm_orchestrator, LLMOrchestratorAgent)
        assert isinstance(agent.rag_agent, RAGContextAgent)
    
    def test_init_with_custom_agents(self):
        """Test initialization with custom agents."""
        mock_llm = Mock(spec=LLMOrchestratorAgent)
        mock_rag = Mock(spec=RAGContextAgent)
        
        agent = ProjectScanningAgent(
            llm_orchestrator=mock_llm,
            rag_agent=mock_rag,
            max_files_for_direct_analysis=25,
            max_lines_per_summary=200
        )
        
        assert agent.llm_orchestrator is mock_llm
        assert agent.rag_agent is mock_rag
        assert agent.max_files_for_direct_analysis == 25
        assert agent.max_lines_per_summary == 200


class TestProjectScanningAgentHelperMethods:
    """Test helper methods of ProjectScanningAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag
        )
    
    def test_group_files_by_directory(self):
        """Test grouping files by directory structure."""
        code_files = {
            'src/main.py': 'print("main")',
            'src/utils/helper.py': 'def help(): pass',
            'tests/test_main.py': 'import pytest',
            'README.md': '# Project'
        }
        
        grouped = self.agent._group_files_by_directory(code_files)
        
        assert 'src' in grouped
        assert 'src/utils' in grouped
        assert 'tests' in grouped
        assert 'root' in grouped
        
        assert 'src/main.py' in grouped['src']
        assert 'src/utils/helper.py' in grouped['src/utils']
        assert 'tests/test_main.py' in grouped['tests']
        assert 'README.md' in grouped['root']
    
    def test_calculate_complexity_metrics(self):
        """Test complexity metrics calculation."""
        code_files = {
            'app.py': 'line1\nline2\nline3',
            'utils.java': 'public class Utils {}',
            'main.kt': 'fun main() {}'
        }
        
        metrics = self.agent._calculate_complexity_metrics(code_files)
        
        assert metrics['total_files'] == 3
        assert metrics['total_lines'] == 5  # 3 + 1 + 1
        assert metrics['languages']['python'] == 1
        assert metrics['languages']['java'] == 1
        assert metrics['languages']['kotlin'] == 1
        assert metrics['average_file_size'] == 5 / 3
        assert len(metrics['largest_files']) == 3
    
    def test_calculate_complexity_metrics_empty(self):
        """Test complexity metrics with empty files."""
        metrics = self.agent._calculate_complexity_metrics({})
        
        assert metrics['total_files'] == 0
        assert metrics['total_lines'] == 0
        assert metrics['average_file_size'] == 0
        assert metrics['largest_files'] == []
    
    def test_format_largest_files(self):
        """Test formatting largest files for prompts."""
        largest_files = [
            {'file': 'big.py', 'lines': 500, 'bytes': 10000},
            {'file': 'medium.py', 'lines': 200, 'bytes': 4000}
        ]
        
        formatted = self.agent._format_largest_files(largest_files)
        
        assert "big.py: 500 lines" in formatted
        assert "medium.py: 200 lines" in formatted
    
    def test_format_largest_files_empty(self):
        """Test formatting empty largest files list."""
        formatted = self.agent._format_largest_files([])
        assert formatted == "No large files identified."
    
    def test_format_static_findings_summary(self):
        """Test formatting static findings summary."""
        static_findings = [
            {'severity': 'high', 'category': 'security'},
            {'severity': 'medium', 'category': 'style'}
        ]
        
        formatted = self.agent._format_static_findings_summary(static_findings)
        
        assert "Total: 2" in formatted
        assert "high" in formatted
        assert "medium" in formatted
    
    def test_format_static_findings_summary_none(self):
        """Test formatting None static findings."""
        formatted = self.agent._format_static_findings_summary(None)
        assert formatted == "No static analysis findings provided."


class TestProjectScanningAgentSummarization:
    """Test hierarchical summarization methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag,
            max_lines_per_summary=5
        )
    
    def test_hierarchical_summarize_file_level_small_files(self):
        """Test file-level summarization for small files."""
        code_files = {
            'small.py': 'line1\nline2',
            'tiny.py': 'print()'
        }
        
        summaries = self.agent._hierarchical_summarize(code_files, "file")
        
        # Small files should be included directly
        assert summaries['small.py'] == 'line1\nline2'
        assert summaries['tiny.py'] == 'print()'
        # LLM should not be called for small files
        self.mock_llm.invoke_llm.assert_not_called()
    
    def test_hierarchical_summarize_file_level_large_files(self):
        """Test file-level summarization for large files."""
        large_content = '\n'.join([f'line{i}' for i in range(10)])
        code_files = {'large.py': large_content}
        
        self.mock_llm.invoke_llm.return_value = "Summary of large file"
        
        summaries = self.agent._hierarchical_summarize(code_files, "file")
        
        assert summaries['large.py'] == "Summary of large file"
        self.mock_llm.invoke_llm.assert_called_once()
    
    def test_summarize_large_file(self):
        """Test individual file summarization."""
        content = "def function():\n    return 'test'"
        self.mock_llm.invoke_llm.return_value = "Function definition file"
        
        summary = self.agent._summarize_large_file('test.py', content)
        
        assert summary == "Function definition file"
        self.mock_llm.invoke_llm.assert_called_once()
        
        # Check that prompt contains file path and content
        call_args = self.mock_llm.invoke_llm.call_args[0][0]
        assert 'test.py' in call_args
        assert content in call_args
    
    def test_summarize_large_file_error_fallback(self):
        """Test file summarization with LLM error."""
        content = "def function():\n    return 'test'"
        self.mock_llm.invoke_llm.side_effect = Exception("LLM error")
        
        summary = self.agent._summarize_large_file('test.py', content)
        
        assert 'test.py' in summary
        assert 'Lines: 2' in summary
        assert 'Large file requiring detailed analysis' in summary
    
    def test_summarize_directory(self):
        """Test directory summarization."""
        file_summaries = {
            'dir/file1.py': 'Summary 1',
            'dir/file2.py': 'Summary 2'
        }
        self.mock_llm.invoke_llm.return_value = "Directory summary"
        
        summary = self.agent._summarize_directory('src/utils', file_summaries)
        
        assert summary == "Directory summary"
        self.mock_llm.invoke_llm.assert_called_once()
        
        call_args = self.mock_llm.invoke_llm.call_args[0][0]
        assert 'src/utils' in call_args
        assert 'Summary 1' in call_args
        assert 'Summary 2' in call_args
    
    def test_summarize_directory_error_fallback(self):
        """Test directory summarization with LLM error."""
        file_summaries = {'file1.py': 'Summary 1'}
        self.mock_llm.invoke_llm.side_effect = Exception("LLM error")
        
        summary = self.agent._summarize_directory('src', file_summaries)
        
        assert 'src' in summary
        assert 'Files: 1' in summary
    
    def test_summarize_project(self):
        """Test project-level summarization."""
        directory_summaries = {
            'src': 'Source directory summary',
            'tests': 'Test directory summary'
        }
        self.mock_llm.invoke_llm.return_value = "Project overview"
        
        summary = self.agent._summarize_project(directory_summaries)
        
        assert summary == "Project overview"
        self.mock_llm.invoke_llm.assert_called_once()
        
        call_args = self.mock_llm.invoke_llm.call_args[0][0]
        assert 'Source directory summary' in call_args
        assert 'Test directory summary' in call_args
    
    def test_create_fallback_summaries_file_level(self):
        """Test fallback summaries at file level."""
        code_files = {
            'file1.py': 'line1\nline2',
            'file2.py': 'single line'
        }
        
        summaries = self.agent._create_fallback_summaries(code_files, "file")
        
        assert 'file1.py (2 lines)' in summaries['file1.py']
        assert 'file2.py (1 lines)' in summaries['file2.py']
    
    def test_create_fallback_summaries_directory_level(self):
        """Test fallback summaries at directory level."""
        code_files = {
            'src/main.py': 'line1\nline2',
            'tests/test.py': 'test'
        }
        
        summaries = self.agent._create_fallback_summaries(code_files, "directory")
        
        assert 'src' in summaries
        assert 'tests' in summaries
        assert '1 files' in summaries['src']
        assert '1 files' in summaries['tests']
    
    def test_hierarchical_summarize_error_fallback(self):
        """Test hierarchical summarization with error fallback."""
        code_files = {'test.py': 'content'}
        
        # Mock the _summarize_large_file to raise an exception
        with patch.object(self.agent, '_summarize_large_file', side_effect=Exception("Test error")):
            summaries = self.agent._hierarchical_summarize(code_files, "file")
        
        # Should fall back to simple summaries
        assert 'test.py' in summaries


class TestProjectScanningAgentRAGAndAnalysis:
    """Test RAG context and analysis methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag
        )
    
    def test_get_project_rag_context(self):
        """Test getting RAG context for project."""
        complexity_metrics = {
            'languages': {'python': 5, 'java': 2}
        }
        
        # Mock RAG responses
        mock_context = [
            {'file_path': 'main.py', 'chunk_index': 0, 'score': 0.9, 'content': 'main function'},
            {'file_path': 'utils.py', 'chunk_index': 1, 'score': 0.8, 'content': 'utility functions'}
        ]
        self.mock_rag.query_knowledge_base.return_value = mock_context
        
        context = self.agent._get_project_rag_context(complexity_metrics)
        
        # Should return combined context from multiple queries
        assert len(context) >= 0
        # Should have made queries for general patterns and language-specific patterns
        assert self.mock_rag.query_knowledge_base.call_count >= 5  # 4 general + 2 language specific
    
    def test_get_project_rag_context_error(self):
        """Test RAG context retrieval with error."""
        complexity_metrics = {'languages': {}}
        self.mock_rag.query_knowledge_base.side_effect = Exception("RAG error")
        
        context = self.agent._get_project_rag_context(complexity_metrics)
        
        assert context == []
    
    def test_analyze_project_architecture(self):
        """Test project architectural analysis."""
        complexity_metrics = {
            'total_files': 10,
            'total_lines': 1000,
            'languages': {'python': 8, 'java': 2},
            'average_file_size': 100,
            'largest_files': [{'file': 'big.py', 'lines': 500, 'bytes': 10000}]
        }
        
        self.mock_llm.invoke_llm.return_value = "Comprehensive architectural analysis"
        
        analysis = self.agent._analyze_project_architecture(
            complexity_metrics=complexity_metrics,
            file_summaries={},
            directory_summaries={},
            project_summary={},
            static_findings=[],
            rag_context=[]
        )
        
        assert analysis == "Comprehensive architectural analysis"
        self.mock_llm.invoke_llm.assert_called_once()
        
        # Check that prompt contains key metrics
        call_args = self.mock_llm.invoke_llm.call_args[0][0]
        assert 'Total files: 10' in call_args
        assert 'Total lines of code: 1000' in call_args
    
    def test_analyze_project_architecture_error(self):
        """Test architectural analysis with LLM error."""
        self.mock_llm.invoke_llm.side_effect = Exception("LLM analysis error")
        
        analysis = self.agent._analyze_project_architecture(
            complexity_metrics={},
            file_summaries={},
            directory_summaries={},
            project_summary={},
            static_findings=[],
            rag_context=[]
        )
        
        assert "Architectural analysis failed" in analysis
        assert "LLM analysis error" in analysis


class TestProjectScanningAgentRiskAssessment:
    """Test risk assessment methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag
        )
    
    def test_assess_project_risks_low_complexity(self):
        """Test risk assessment for low complexity project."""
        complexity_metrics = {
            'total_files': 10,
            'average_file_size': 50
        }
        static_findings = [
            {'severity': 'low', 'category': 'style'},
            {'severity': 'medium', 'category': 'performance'}
        ]
        
        self.mock_llm.invoke_llm.return_value = "Low risk project analysis"
        
        risks = self.agent._assess_project_risks(
            complexity_metrics, "architectural analysis", static_findings
        )
        
        assert risks['overall_risk_level'] == 'low'
        assert len(risks['risk_factors']) == 0  # No high-complexity risks
        assert 'llm_risk_analysis' in risks
    
    def test_assess_project_risks_high_complexity(self):
        """Test risk assessment for high complexity project."""
        complexity_metrics = {
            'total_files': 150,  # High file count
            'average_file_size': 400  # Large files
        }
        static_findings = [
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'security'},  # 11 high severity issues
        ]
        
        risks = self.agent._assess_project_risks(
            complexity_metrics, "architectural analysis", static_findings
        )
        
        assert risks['overall_risk_level'] == 'high'
        assert len(risks['risk_factors']) >= 1  # Should have complexity and quality risks
        assert len(risks['maintainability_risks']) >= 1  # Large file size risk
        assert len(risks['security_risks']) >= 1  # Security findings
    
    def test_assess_project_risks_medium_severity(self):
        """Test risk assessment with medium severity issues."""
        complexity_metrics = {'total_files': 20, 'average_file_size': 100}
        static_findings = [
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'performance'},
            {'severity': 'high', 'category': 'maintainability'},
            {'severity': 'high', 'category': 'style'},
            {'severity': 'high', 'category': 'complexity'},
            {'severity': 'high', 'category': 'documentation'},  # 6 high severity issues
        ]
        
        risks = self.agent._assess_project_risks(
            complexity_metrics, "architectural analysis", static_findings
        )
        
        assert risks['overall_risk_level'] == 'medium'
    
    def test_assess_project_risks_error_handling(self):
        """Test risk assessment with error handling."""
        with patch.object(self.agent, '_llm_risk_analysis', side_effect=Exception("Risk analysis error")):
            risks = self.agent._assess_project_risks({}, "analysis", [])
        
        assert 'error' in risks
        assert "Risk analysis error" in risks['error']
    
    def test_llm_risk_analysis(self):
        """Test LLM-based risk analysis."""
        complexity_metrics = {'total_files': 50, 'total_lines': 5000, 'languages': {'python': 30}}
        self.mock_llm.invoke_llm.return_value = "Detailed risk analysis from LLM"
        
        analysis = self.agent._llm_risk_analysis(
            complexity_metrics, "architectural analysis", []
        )
        
        assert analysis == "Detailed risk analysis from LLM"
        self.mock_llm.invoke_llm.assert_called_once()
        
        call_args = self.mock_llm.invoke_llm.call_args[0][0]
        assert 'Files: 50' in call_args
        assert 'Lines: 5000' in call_args
    
    def test_llm_risk_analysis_error(self):
        """Test LLM risk analysis with error."""
        self.mock_llm.invoke_llm.side_effect = Exception("LLM risk error")
        
        analysis = self.agent._llm_risk_analysis({}, "analysis", [])
        
        assert analysis == "LLM risk analysis unavailable"


class TestProjectScanningAgentStaticFindingsAndRecommendations:
    """Test static findings and recommendations methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag
        )
    
    def test_summarize_static_findings_none(self):
        """Test summarizing None static findings."""
        summary = self.agent._summarize_static_findings(None)
        
        assert summary['total'] == 0
        assert summary['by_severity'] == {}
        assert summary['by_category'] == {}
    
    def test_summarize_static_findings_with_data(self):
        """Test summarizing static findings with data."""
        static_findings = [
            {'severity': 'high', 'category': 'security'},
            {'severity': 'high', 'category': 'performance'},
            {'severity': 'medium', 'category': 'style'},
            {'severity': 'low', 'category': 'documentation'}
        ]
        
        summary = self.agent._summarize_static_findings(static_findings)
        
        assert summary['total'] == 4
        assert summary['by_severity']['high'] == 2
        assert summary['by_severity']['medium'] == 1
        assert summary['by_severity']['low'] == 1
        assert summary['by_category']['security'] == 1
        assert summary['by_category']['performance'] == 1
        assert len(summary['top_issues']) == 4
    
    def test_generate_project_recommendations_small_project(self):
        """Test recommendations for small project."""
        complexity_metrics = {
            'total_files': 10,
            'average_file_size': 50,
            'languages': {'python': 5}
        }
        risk_assessment = {'overall_risk_level': 'low'}
        
        recommendations = self.agent._generate_project_recommendations(
            complexity_metrics, "architectural analysis", risk_assessment
        )
        
        # Should have minimal recommendations for small, low-risk project
        assert len(recommendations) >= 0
    
    def test_generate_project_recommendations_large_project(self):
        """Test recommendations for large project."""
        complexity_metrics = {
            'total_files': 75,  # Large project
            'average_file_size': 250,  # Large files
            'languages': {'python': 60, 'java': 15}
        }
        risk_assessment = {'overall_risk_level': 'high'}
        
        recommendations = self.agent._generate_project_recommendations(
            complexity_metrics, "architectural analysis", risk_assessment
        )
        
        # Should have multiple recommendations
        assert len(recommendations) >= 3
        
        # Check for expected recommendation categories
        categories = [rec['category'] for rec in recommendations]
        assert 'organization' in categories  # Large project recommendation
        assert 'maintainability' in categories  # Large file recommendation
        assert 'risk_mitigation' in categories  # High risk recommendation


class TestProjectScanningAgentFullScan:
    """Test the complete project scanning workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMOrchestratorAgent)
        self.mock_rag = Mock(spec=RAGContextAgent)
        self.agent = ProjectScanningAgent(
            llm_orchestrator=self.mock_llm,
            rag_agent=self.mock_rag,
            max_files_for_direct_analysis=5  # Low threshold for testing
        )
    
    def test_scan_entire_project_small_project(self):
        """Test scanning small project (direct analysis)."""
        code_files = {
            'main.py': 'def main(): pass',
            'utils.py': 'def helper(): return True',
            'test.py': 'import pytest'
        }
        static_findings = [
            {'severity': 'medium', 'category': 'style'}
        ]
        
        # Setup mocks
        self.mock_rag.build_knowledge_base.return_value = None
        self.mock_rag.query_knowledge_base.return_value = []
        self.mock_llm.invoke_llm.return_value = "Mock analysis response"
        
        report = self.agent.scan_entire_project(code_files, static_findings)
        
        assert report['scan_type'] == 'project'
        assert report['use_hierarchical_analysis'] is False  # Small project
        assert report['complexity_metrics']['total_files'] == 3
        assert 'architectural_analysis' in report
        assert 'risk_assessment' in report
        assert 'recommendations' in report
        
        # Should build RAG knowledge base
        self.mock_rag.build_knowledge_base.assert_called_once_with(code_files)
    
    def test_scan_entire_project_large_project(self):
        """Test scanning large project (hierarchical analysis)."""
        # Create code files that exceed the threshold
        code_files = {}
        for i in range(10):  # Exceeds max_files_for_direct_analysis=5
            code_files[f'file_{i}.py'] = f'def function_{i}(): pass'
        
        # Setup mocks
        self.mock_rag.build_knowledge_base.return_value = None
        self.mock_rag.query_knowledge_base.return_value = []
        self.mock_llm.invoke_llm.return_value = "Mock hierarchical analysis"
        
        report = self.agent.scan_entire_project(code_files)
        
        assert report['scan_type'] == 'project'
        assert report['use_hierarchical_analysis'] is True  # Large project
        assert report['complexity_metrics']['total_files'] == 10
        assert 'directory_summaries' in report
        assert 'project_summary' in report
        
        # Should have called LLM for summarization
        assert self.mock_llm.invoke_llm.call_count >= 1
    
    def test_scan_entire_project_with_rag_context(self):
        """Test project scan with RAG context."""
        code_files = {'main.py': 'def main(): pass'}
        
        # Setup RAG mock to return context
        mock_context = [
            {'file_path': 'main.py', 'chunk_index': 0, 'score': 0.9, 'content': 'main function'}
        ]
        self.mock_rag.query_knowledge_base.return_value = mock_context
        self.mock_llm.invoke_llm.return_value = "Analysis with context"
        
        report = self.agent.scan_entire_project(code_files)
        
        assert 'rag_context' in report
        assert len(report['rag_context']) >= 0
        
        # Should have queried RAG for context
        assert self.mock_rag.query_knowledge_base.call_count >= 1
    
    def test_scan_entire_project_error_handling(self):
        """Test project scan with error handling."""
        code_files = {'test.py': 'content'}
        
        # Make RAG fail
        self.mock_rag.build_knowledge_base.side_effect = Exception("RAG failed")
        
        report = self.agent.scan_entire_project(code_files)
        
        assert report['scan_type'] == 'project'
        assert 'error' in report
        assert 'RAG failed' in report['error']
        assert 'partial_results' in report
        assert 'complexity_metrics' in report['partial_results']
    
    def test_scan_entire_project_no_static_findings(self):
        """Test project scan without static findings."""
        code_files = {'main.py': 'def main(): pass'}
        
        self.mock_rag.build_knowledge_base.return_value = None
        self.mock_rag.query_knowledge_base.return_value = []
        self.mock_llm.invoke_llm.return_value = "Clean project analysis"
        
        report = self.agent.scan_entire_project(code_files, None)
        
        assert report['static_findings_summary']['total'] == 0
        assert 'architectural_analysis' in report
        assert 'risk_assessment' in report
    
    @patch('src.core_engine.agents.project_scanning_agent.logger')
    def test_scan_entire_project_logging(self, mock_logger):
        """Test that project scan includes proper logging."""
        code_files = {'main.py': 'def main(): pass'}
        
        self.mock_rag.build_knowledge_base.return_value = None
        self.mock_rag.query_knowledge_base.return_value = []
        self.mock_llm.invoke_llm.return_value = "Analysis"
        
        self.agent.scan_entire_project(code_files)
        
        # Should log various stages
        assert mock_logger.info.call_count >= 4  # Start, metrics, RAG, LLM, complete


class TestProjectScanningAgentIntegration:
    """Integration tests for ProjectScanningAgent."""
    
    def test_integration_with_real_agents(self):
        """Test integration with real LLM and RAG agents."""
        # Use real agents but with mock providers
        real_llm = LLMOrchestratorAgent(llm_provider='mock')
        
        # Mock RAG to avoid external dependencies
        mock_rag = Mock(spec=RAGContextAgent)
        mock_rag.build_knowledge_base.return_value = None
        mock_rag.query_knowledge_base.return_value = []
        
        agent = ProjectScanningAgent(
            llm_orchestrator=real_llm,
            rag_agent=mock_rag
        )
        
        code_files = {
            'main.py': 'def main():\n    print("Hello, World!")\n    return 0',
            'utils.py': 'def helper_function():\n    return True'
        }
        
        report = agent.scan_entire_project(code_files)
        
        assert report['scan_type'] == 'project'
        assert 'complexity_metrics' in report
        assert 'architectural_analysis' in report
        assert len(report['complexity_metrics']) > 0 