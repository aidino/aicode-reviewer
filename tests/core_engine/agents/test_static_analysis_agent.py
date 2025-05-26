"""
Unit tests for StaticAnalysisAgent.

This module contains comprehensive tests for the StaticAnalysisAgent class,
including tests for all implemented rules and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Mock tree_sitter if not available
try:
    import tree_sitter
    from tree_sitter import Language, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    tree_sitter = None
    Language = None
    Node = None
    TREE_SITTER_AVAILABLE = False

from src.core_engine.agents.static_analysis_agent import StaticAnalysisAgent


class TestStaticAnalysisAgent:
    """Test cases for StaticAnalysisAgent class."""
    
    @pytest.fixture
    def mock_tree_sitter(self):
        """Mock tree-sitter components for testing."""
        if not TREE_SITTER_AVAILABLE:
            with patch('src.core_engine.agents.static_analysis_agent.tree_sitter') as mock_ts:
                mock_ts.Language = Mock()
                mock_ts.Node = Mock()
                yield mock_ts
        else:
            yield tree_sitter
    
    @pytest.fixture
    def mock_python_language(self):
        """Mock Python language for tree-sitter."""
        mock_lang = Mock()
        mock_query = Mock()
        mock_lang.query.return_value = mock_query
        mock_query.captures.return_value = []
        return mock_lang
    
    @pytest.fixture
    def sample_ast_node(self):
        """Create a sample AST node for testing."""
        mock_node = Mock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (10, 0)
        mock_node.text = b"sample_code"
        return mock_node
    
    def test_init_success(self, mock_tree_sitter, mock_python_language):
        """Test successful initialization of StaticAnalysisAgent."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language') as mock_init:
                agent = StaticAnalysisAgent()
                
                assert agent.supported_languages == ['python']
                assert agent.languages == {}
                mock_init.assert_called_once()
    
    def test_init_no_tree_sitter(self):
        """Test initialization failure when tree-sitter is not available."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', None):
            with pytest.raises(ImportError, match="tree-sitter is not installed"):
                StaticAnalysisAgent()
    
    def test_initialize_python_language_success(self, mock_tree_sitter):
        """Test successful Python language initialization."""
        mock_language_func = Mock()
        mock_language_func.return_value = Mock()
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch('tree_sitter_python.language', mock_language_func):
                with patch('src.core_engine.agents.static_analysis_agent.Language') as mock_lang_class:
                    mock_lang_instance = Mock()
                    mock_lang_class.return_value = mock_lang_instance
                    
                    agent = StaticAnalysisAgent()
                    
                    assert agent.languages['python'] == mock_lang_instance
    
    def test_initialize_python_language_fallback(self, mock_tree_sitter):
        """Test Python language initialization fallback when package not found."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch('tree_sitter_python.language', side_effect=ImportError()):
                agent = StaticAnalysisAgent()
                
                assert agent.languages['python'] is None
    
    def test_query_ast_success(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test successful AST querying."""
        mock_captures = [(sample_ast_node, {'test': sample_ast_node})]
        mock_query = Mock()
        mock_query.captures.return_value = mock_captures
        mock_python_language.query.return_value = mock_query
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            result = agent._query_ast(sample_ast_node, "test query")
            
            assert result == mock_captures
            mock_python_language.query.assert_called_once_with("test query")
    
    def test_query_ast_no_language(self, mock_tree_sitter, sample_ast_node):
        """Test AST querying when language is not available."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = None
            
            result = agent._query_ast(sample_ast_node, "test query")
            
            assert result == []
    
    def test_query_ast_error(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test AST querying with error handling."""
        mock_python_language.query.side_effect = Exception("Query error")
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            result = agent._query_ast(sample_ast_node, "test query")
            
            assert result == []
    
    def test_check_rule_pdb_set_trace_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test pdb.set_trace() rule when debugging statement is found."""
        # Mock captures for pdb.set_trace() call
        call_node = Mock()
        call_node.start_point = (5, 10)
        mock_captures = [(sample_ast_node, {'call': call_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_rule_pdb_set_trace(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'PDB_TRACE_FOUND'
                assert findings[0]['line'] == 6  # start_point[0] + 1
                assert findings[0]['column'] == 11  # start_point[1] + 1
                assert findings[0]['severity'] == 'Warning'
                assert 'pdb.set_trace()' in findings[0]['message']
    
    def test_check_rule_pdb_set_trace_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test pdb.set_trace() rule when no debugging statement is found."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=[]):
                findings = agent._check_rule_pdb_set_trace(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_rule_print_statements_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test print statement rule when print() calls are found."""
        # Mock captures for print() call
        call_node = Mock()
        call_node.start_point = (10, 5)
        mock_captures = [(sample_ast_node, {'call': call_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_rule_print_statements(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'PRINT_STATEMENT_FOUND'
                assert findings[0]['line'] == 11
                assert findings[0]['severity'] == 'Info'
                assert 'print()' in findings[0]['message']
    
    def test_check_rule_function_too_long_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test function too long rule when long function is found."""
        # Mock captures for long function
        func_node = Mock()
        func_node.start_point = (0, 0)
        func_node.end_point = (60, 0)  # 61 lines total (>50)
        func_name_node = Mock()
        func_name_node.text = b"long_function"
        mock_captures = [(sample_ast_node, {'func_def': func_node, 'func_name': func_name_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_rule_function_too_long(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'FUNCTION_TOO_LONG'
                assert findings[0]['severity'] == 'Warning'
                assert 'long_function' in findings[0]['message']
                assert '61 lines long' in findings[0]['message']
    
    def test_check_rule_function_too_long_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test function too long rule when function is acceptable length."""
        # Mock captures for short function
        func_node = Mock()
        func_node.start_point = (0, 0)
        func_node.end_point = (30, 0)  # 31 lines total (<50)
        func_name_node = Mock()
        func_name_node.text = b"short_function"
        mock_captures = [(sample_ast_node, {'func_def': func_node, 'func_name': func_name_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_rule_function_too_long(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_rule_class_too_long_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test class too long rule when long class is found."""
        # Mock captures for long class
        class_node = Mock()
        class_node.start_point = (0, 0)
        class_node.end_point = (250, 0)  # 251 lines total (>200)
        class_name_node = Mock()
        class_name_node.text = b"LongClass"
        mock_captures = [(sample_ast_node, {'class_def': class_node, 'class_name': class_name_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_rule_class_too_long(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'CLASS_TOO_LONG'
                assert findings[0]['severity'] == 'Warning'
                assert 'LongClass' in findings[0]['message']
                assert '251 lines long' in findings[0]['message']
    
    def test_check_rule_simple_unused_imports_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test unused imports rule when unused import is found."""
        # Mock import statement
        import_node = Mock()
        import_node.text = b"unused_module"
        import_stmt_node = Mock()
        import_stmt_node.start_point = (0, 0)
        
        # Mock identifier usage (not including the unused import)
        identifier_node = Mock()
        identifier_node.text = b"used_function"
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            def mock_query_side_effect(ast_node, query_string):
                if "import_statement" in query_string:
                    return [(sample_ast_node, {'import_name': import_node, 'import_stmt': import_stmt_node})]
                elif "import_from_statement" in query_string:
                    return []
                elif "identifier" in query_string:
                    return [(sample_ast_node, {'identifier': identifier_node})]
                return []
            
            with patch.object(agent, '_query_ast', side_effect=mock_query_side_effect):
                findings = agent._check_rule_simple_unused_imports(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'POTENTIALLY_UNUSED_IMPORT'
                assert 'unused_module' in findings[0]['message']
                assert findings[0]['severity'] == 'Info'
    
    def test_analyze_python_ast_success(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test successful Python AST analysis."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            # Mock each rule to return one finding
            mock_finding = {'rule_id': 'TEST_RULE', 'message': 'Test finding'}
            
            with patch.object(agent, '_check_rule_pdb_set_trace', return_value=[mock_finding]):
                with patch.object(agent, '_check_rule_print_statements', return_value=[]):
                    with patch.object(agent, '_check_rule_function_too_long', return_value=[]):
                        with patch.object(agent, '_check_rule_class_too_long', return_value=[]):
                            with patch.object(agent, '_check_rule_simple_unused_imports', return_value=[]):
                                findings = agent.analyze_python_ast(sample_ast_node)
                                
                                assert len(findings) == 1
                                assert findings[0] == mock_finding
    
    def test_analyze_file_ast_success(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test successful file AST analysis."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            mock_finding = {'rule_id': 'TEST_RULE', 'message': 'Test finding'}
            
            with patch.object(agent, 'analyze_python_ast', return_value=[mock_finding]):
                findings = agent.analyze_file_ast(sample_ast_node, 'test.py', 'python')
                
                assert len(findings) == 1
                assert findings[0]['file'] == 'test.py'
                assert findings[0]['rule_id'] == 'TEST_RULE'
    
    def test_analyze_file_ast_unsupported_language(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test file AST analysis with unsupported language."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            findings = agent.analyze_file_ast(sample_ast_node, 'test.java', 'java')
            
            assert len(findings) == 0
    
    def test_analyze_file_ast_no_ast_node(self, mock_tree_sitter, mock_python_language):
        """Test file AST analysis with no AST node."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            findings = agent.analyze_file_ast(None, 'test.py', 'python')
            
            assert len(findings) == 0
    
    def test_get_supported_languages(self, mock_tree_sitter):
        """Test getting supported languages."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language'):
                agent = StaticAnalysisAgent()
                
                languages = agent.get_supported_languages()
                
                assert languages == ['python']
                # Ensure it returns a copy
                languages.append('java')
                assert agent.supported_languages == ['python']
    
    def test_is_language_supported(self, mock_tree_sitter):
        """Test checking if language is supported."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language'):
                agent = StaticAnalysisAgent()
                
                assert agent.is_language_supported('python') is True
                assert agent.is_language_supported('java') is False
                assert agent.is_language_supported('kotlin') is False
    
    def test_rule_error_handling(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test error handling in individual rules."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            # Mock _query_ast to raise an exception
            with patch.object(agent, '_query_ast', side_effect=Exception("Query error")):
                # Each rule should handle the error gracefully and return empty list
                assert agent._check_rule_pdb_set_trace(sample_ast_node) == []
                assert agent._check_rule_print_statements(sample_ast_node) == []
                assert agent._check_rule_function_too_long(sample_ast_node) == []
                assert agent._check_rule_class_too_long(sample_ast_node) == []
                assert agent._check_rule_simple_unused_imports(sample_ast_node) == []
    
    def test_analyze_python_ast_rule_error_handling(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test error handling in analyze_python_ast when individual rules fail."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            # Mock one rule to succeed and others to fail
            with patch.object(agent, '_check_rule_pdb_set_trace', return_value=[{'rule_id': 'SUCCESS'}]):
                with patch.object(agent, '_check_rule_print_statements', side_effect=Exception("Rule error")):
                    with patch.object(agent, '_check_rule_function_too_long', side_effect=Exception("Rule error")):
                        with patch.object(agent, '_check_rule_class_too_long', side_effect=Exception("Rule error")):
                            with patch.object(agent, '_check_rule_simple_unused_imports', side_effect=Exception("Rule error")):
                                findings = agent.analyze_python_ast(sample_ast_node)
                                
                                # Should still return the successful rule's findings
                                assert len(findings) == 1
                                assert findings[0]['rule_id'] == 'SUCCESS' 