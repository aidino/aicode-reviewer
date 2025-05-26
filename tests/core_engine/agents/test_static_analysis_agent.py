"""
Unit tests for StaticAnalysisAgent.

This module contains comprehensive tests for the StaticAnalysisAgent class,
including tests for all implemented rules and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from tree_sitter import Node, Tree, Parser, Language

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
            with patch.object(StaticAnalysisAgent, '_initialize_python_language') as mock_init, \
                 patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None):
                mock_init.return_value = mock_python_language
                agent = StaticAnalysisAgent()
                assert agent.supported_languages == ['python']
                assert isinstance(agent.languages, dict)
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
            with patch.object(StaticAnalysisAgent, '_initialize_python_language') as mock_init, \
                 patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None):
                mock_init.return_value = Mock()
                agent = StaticAnalysisAgent()
                
                languages = agent.get_supported_languages()
                
                assert languages == ['python']
                # Ensure it returns a copy
                languages.append('java')
                assert agent.supported_languages == ['python']
    
    def test_is_language_supported(self, mock_tree_sitter):
        """Test checking if language is supported."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language') as mock_init, \
                 patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None):
                mock_init.return_value = Mock()
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
                                with patch.object(agent, '_check_empty_except_block', side_effect=Exception("Rule error")):
                                    with patch.object(agent, '_check_hardcoded_passwords', side_effect=Exception("Rule error")):
                                        with patch.object(agent, '_check_excessive_boolean_complexity', side_effect=Exception("Rule error")):
                                            with patch.object(agent, '_check_magic_numbers', side_effect=Exception("Rule error")):
                                                with patch.object(agent, '_check_todo_comments', side_effect=Exception("Rule error")):
                                                    findings = agent.analyze_python_ast(sample_ast_node)
                                                    
                                                    # Should still return the successful rule's findings
                                                    assert len(findings) == 1
                                                    assert findings[0]['rule_id'] == 'SUCCESS'
    
    def test_check_empty_except_block_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test empty except block rule when empty except is found."""
        # Mock captures for empty except block
        except_node = Mock()
        except_node.start_point = (5, 4)
        mock_captures = [(sample_ast_node, {'except': except_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_empty_except_block(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'EMPTY_EXCEPT_BLOCK'
                assert findings[0]['line'] == 6
                assert findings[0]['column'] == 5
                assert findings[0]['severity'] == 'Error'
                assert 'Empty except block found' in findings[0]['message']
                assert 'error_handling' == findings[0]['category']
    
    def test_check_empty_except_block_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test empty except block rule when except block has content."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=[]):
                findings = agent._check_empty_except_block(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_hardcoded_passwords_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test hardcoded password rule when password assignment is found."""
        # Mock captures for password assignment
        var_node = Mock()
        var_node.start_point = (10, 4)
        var_node.text = b"password"
        string_node = Mock()
        string_node.text = b'"secret123"'
        mock_captures = [(sample_ast_node, {'var_name': var_node, 'string_value': string_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_hardcoded_passwords(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'HARDCODED_PASSWORD'
                assert findings[0]['line'] == 11
                assert findings[0]['column'] == 5
                assert findings[0]['severity'] == 'Error'
                assert 'password' in findings[0]['message']
                assert 'security' == findings[0]['category']
    
    def test_check_hardcoded_passwords_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test hardcoded password rule when no password assignments are found."""
        # Mock captures for non-password assignment
        var_node = Mock()
        var_node.start_point = (10, 4)
        var_node.text = b"username"
        string_node = Mock()
        string_node.text = b'"john_doe"'
        mock_captures = [(sample_ast_node, {'var_name': var_node, 'string_value': string_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_hardcoded_passwords(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_excessive_boolean_complexity_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test boolean complexity rule when complex expression is found."""
        # Mock captures for complex boolean expression
        bool_op_node = Mock()
        bool_op_node.start_point = (15, 8)
        bool_op_node.id = 1
        parent_node = Mock()
        parent_node.type = 'boolean_operator'
        parent_node.id = 2
        grandparent_node = Mock()
        grandparent_node.type = 'boolean_operator'
        grandparent_node.id = 3
        great_grandparent_node = Mock()
        great_grandparent_node.type = 'boolean_operator'
        great_grandparent_node.id = 4
        
        bool_op_node.parent = parent_node
        parent_node.parent = grandparent_node
        grandparent_node.parent = great_grandparent_node
        
        mock_captures = [(sample_ast_node, {'bool_op': bool_op_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_excessive_boolean_complexity(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'EXCESSIVE_BOOLEAN_COMPLEXITY'
                assert findings[0]['line'] == 16
                assert findings[0]['column'] == 9
                assert findings[0]['severity'] == 'Warning'
                assert '4 operators' in findings[0]['message']
                assert 'complexity' == findings[0]['category']
    
    def test_check_excessive_boolean_complexity_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test boolean complexity rule when expression is simple."""
        # Mock captures for simple boolean expression
        bool_op_node = Mock()
        bool_op_node.start_point = (15, 8)
        bool_op_node.id = 1
        parent_node = Mock()
        parent_node.type = 'boolean_operator'
        parent_node.id = 2
        
        bool_op_node.parent = parent_node
        parent_node.parent = None
        
        mock_captures = [(sample_ast_node, {'bool_op': bool_op_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_excessive_boolean_complexity(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_magic_numbers_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test magic numbers rule when magic number is found."""
        # Mock captures for magic number
        number_node = Mock()
        number_node.start_point = (20, 12)
        number_node.text = b"42"
        parent_node = Mock()
        parent_node.type = 'binary_operator'  # Not assignment or parameters
        number_node.parent = parent_node
        
        mock_captures = [(sample_ast_node, {'number': number_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_magic_numbers(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'MAGIC_NUMBER'
                assert findings[0]['line'] == 21
                assert findings[0]['column'] == 13
                assert findings[0]['severity'] == 'Info'
                assert '42' in findings[0]['message']
                assert 'maintainability' == findings[0]['category']
    
    def test_check_magic_numbers_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test magic numbers rule when number is in acceptable context."""
        # Mock captures for acceptable number usage
        number_node = Mock()
        number_node.start_point = (20, 12)
        number_node.text = b"1"  # Common acceptable value
        parent_node = Mock()
        parent_node.type = 'assignment'  # Acceptable context
        number_node.parent = parent_node
        
        mock_captures = [(sample_ast_node, {'number': number_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_magic_numbers(sample_ast_node)
                
                assert len(findings) == 0
    
    def test_check_todo_comments_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test TODO comments rule when TODO/FIXME comment is found."""
        # Mock captures for TODO comment
        comment_node = Mock()
        comment_node.start_point = (25, 4)
        comment_node.text = b"# TODO: Implement error handling"
        
        mock_captures = [(sample_ast_node, {'comment': comment_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_todo_comments(sample_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'TODO_COMMENT_FOUND'
                assert findings[0]['line'] == 26
                assert findings[0]['column'] == 5
                assert findings[0]['severity'] == 'Info'
                assert 'TODO comment found' in findings[0]['message']
                assert 'documentation' == findings[0]['category']
    
    def test_check_todo_comments_not_found(self, mock_tree_sitter, mock_python_language, sample_ast_node):
        """Test TODO comments rule when no TODO/FIXME comments are found."""
        # Mock captures for regular comment
        comment_node = Mock()
        comment_node.start_point = (25, 4)
        comment_node.text = b"# This is a regular comment"
        
        mock_captures = [(sample_ast_node, {'comment': comment_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter', mock_tree_sitter):
            agent = StaticAnalysisAgent()
            agent.languages['python'] = mock_python_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_todo_comments(sample_ast_node)
                
                assert len(findings) == 0

@pytest.fixture
def mock_java_language():
    mock_lang = Mock(spec=Language)
    return mock_lang

@pytest.fixture
def mock_java_parser(mock_java_language):
    parser = Mock(spec=Parser)
    tree = Mock(spec=Tree)
    root_node = Mock(spec=Node)
    root_node.has_error = False
    root_node.children = []
    tree.root_node = root_node
    parser.parse.return_value = tree
    return parser

@pytest.fixture
def static_analysis_agent_with_java(mock_java_language, mock_java_parser):
    """Create StaticAnalysisAgent with mocked Java support."""
    with patch('src.core_engine.agents.static_analysis_agent.tree_sitter') as mock_tree_sitter:
        mock_tree_sitter.Parser = Mock(return_value=mock_java_parser)
        mock_tree_sitter.Language = Mock(return_value=mock_java_language)
        
        with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=mock_java_language), \
             patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None):
            agent = StaticAnalysisAgent()
            agent.languages = {'python': mock_java_language}  # Only Python initially
            agent.supported_languages = ['python']  # Only Python initially
            return agent

def test_java_grammar_loading():
    """Test that Java grammar loading is attempted."""
    with patch('src.core_engine.agents.static_analysis_agent.tree_sitter') as mock_tree_sitter:
        with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=Mock()), \
             patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=Mock()) as mock_java_init:
            agent = StaticAnalysisAgent()
            
            # Java initialization should have been attempted
            mock_java_init.assert_called_once()

def test_analyze_ast_with_java():
    """Test analyze_ast dispatch to Java rules when Java is supported."""
    with patch('src.core_engine.agents.static_analysis_agent.tree_sitter') as mock_tree_sitter:
        with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=Mock()), \
             patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=Mock()):
            agent = StaticAnalysisAgent()
            agent.supported_languages = ['python', 'java']  # Manually add Java support
            
            # Mock the Java AST analysis method
            with patch.object(agent, 'analyze_java_ast', return_value=[
                {'rule_id': 'TEST_JAVA_RULE', 'message': 'Test Java finding'}
            ]) as mock_java_analysis:
                
                findings = agent.analyze_ast(Mock(), 'Test.java', 'java')
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'TEST_JAVA_RULE'
                assert findings[0]['file'] == 'Test.java'
                mock_java_analysis.assert_called_once()

def test_check_java_system_out_println(static_analysis_agent_with_java):
    """Test detection of System.out.println() calls."""
    # Create mock AST nodes for System.out.println()
    println_node = Mock(spec=Node)
    println_node.type = 'method_invocation'
    println_node.start_point = (1, 0)
    
    sys_node = Mock(spec=Node)
    sys_node.type = 'identifier'
    sys_node.text = b'System'
    
    out_node = Mock(spec=Node)
    out_node.type = 'identifier'
    out_node.text = b'out'
    
    println_id_node = Mock(spec=Node)
    println_id_node.type = 'identifier'
    println_id_node.text = b'println'
    
    # Mock query captures
    static_analysis_agent_with_java._query_ast = Mock(return_value=[
        (None, {'call': println_node, 'sys': sys_node, 'out': out_node, 'println': println_id_node})
    ])
    
    findings = static_analysis_agent_with_java._check_java_system_out_println(Mock())
    
    assert len(findings) == 1
    assert findings[0]['rule_id'] == 'SYSTEM_OUT_PRINTLN_FOUND'
    assert 'proper logging' in findings[0]['suggestion']

def test_check_java_empty_catch_block(static_analysis_agent_with_java):
    """Test detection of empty catch blocks."""
    # Create mock AST nodes for empty catch block
    catch_node = Mock(spec=Node)
    catch_node.type = 'catch_clause'
    catch_node.start_point = (1, 0)
    
    body_node = Mock(spec=Node)
    body_node.type = 'block'
    body_node.start_point = (1, 0)
    body_node.children = [Mock(), Mock()]  # Just braces
    
    # Mock query captures
    static_analysis_agent_with_java._query_ast = Mock(return_value=[
        (None, {'catch': catch_node, 'catch_body': body_node})
    ])
    
    findings = static_analysis_agent_with_java._check_java_empty_catch_block(Mock())
    
    assert len(findings) == 1
    assert findings[0]['rule_id'] == 'EMPTY_CATCH_BLOCK'
    assert 'handle the exception' in findings[0]['suggestion']

def test_check_java_public_fields(static_analysis_agent_with_java):
    """Test detection of public fields."""
    # Create mock AST nodes for public field
    field_node = Mock(spec=Node)
    field_node.type = 'field_declaration'
    field_node.start_point = (1, 0)
    
    mod_node = Mock(spec=Node)
    mod_node.type = 'modifier'
    mod_node.text = b'public'
    
    field_name_node = Mock(spec=Node)
    field_name_node.type = 'identifier'
    field_name_node.text = b'myPublicField'
    
    # Mock query captures
    static_analysis_agent_with_java._query_ast = Mock(return_value=[
        (None, {'field': field_node, 'mod': mod_node, 'field_name': field_name_node})
    ])
    
    findings = static_analysis_agent_with_java._check_java_public_fields(Mock())
    
    assert len(findings) == 1
    assert findings[0]['rule_id'] == 'PUBLIC_FIELD'
    assert 'myPublicField' in findings[0]['message']
    assert 'private' in findings[0]['suggestion']

def test_analyze_java_ast(static_analysis_agent_with_java):
    """Test full Java AST analysis."""
    # Mock findings from individual rules
    static_analysis_agent_with_java._check_java_system_out_println = Mock(return_value=[
        {'rule_id': 'SYSTEM_OUT_PRINTLN_FOUND', 'message': 'Test println finding'}
    ])
    static_analysis_agent_with_java._check_java_empty_catch_block = Mock(return_value=[
        {'rule_id': 'EMPTY_CATCH_BLOCK', 'message': 'Test catch finding'}
    ])
    static_analysis_agent_with_java._check_java_public_fields = Mock(return_value=[
        {'rule_id': 'PUBLIC_FIELD', 'message': 'Test field finding'}
    ])
    
    findings = static_analysis_agent_with_java.analyze_java_ast(Mock())
    
    assert len(findings) == 3
    rule_ids = {f['rule_id'] for f in findings}
    assert rule_ids == {'SYSTEM_OUT_PRINTLN_FOUND', 'EMPTY_CATCH_BLOCK', 'PUBLIC_FIELD'}

def test_analyze_ast_with_java():
    """Test analyze_ast dispatch to Java rules when Java is supported."""
    with patch('src.core_engine.agents.static_analysis_agent.tree_sitter') as mock_tree_sitter:
        with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=Mock()), \
             patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=Mock()):
            agent = StaticAnalysisAgent()
            agent.supported_languages = ['python', 'java']  # Manually add Java support
            
            # Mock the Java AST analysis method
            with patch.object(agent, 'analyze_java_ast', return_value=[
                {'rule_id': 'TEST_JAVA_RULE', 'message': 'Test Java finding'}
            ]) as mock_java_analysis:
                
                findings = agent.analyze_ast(Mock(), 'Test.java', 'java')
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'TEST_JAVA_RULE'
                assert findings[0]['file'] == 'Test.java'
                mock_java_analysis.assert_called_once()

def test_analyze_ast_unsupported_language(static_analysis_agent_with_java):
    """Test analyze_ast with unsupported language."""
    findings = static_analysis_agent_with_java.analyze_ast(Mock(), 'test.kt', 'kotlin')
    assert len(findings) == 0

def test_analyze_ast_no_ast(static_analysis_agent_with_java):
    """Test analyze_ast with no AST."""
    findings = static_analysis_agent_with_java.analyze_ast(None, 'Test.java', 'java')
    assert len(findings) == 0

# Test cases for Kotlin and XML support
class TestKotlinXMLSupport:
    """Test cases for Kotlin and XML static analysis support."""
    
    @pytest.fixture
    def mock_kotlin_language(self):
        """Mock Kotlin language for tree-sitter."""
        mock_lang = Mock()
        mock_query = Mock()
        mock_lang.query.return_value = mock_query
        mock_query.captures.return_value = []
        return mock_lang
    
    @pytest.fixture
    def mock_xml_language(self):
        """Mock XML language for tree-sitter."""
        mock_lang = Mock()
        mock_query = Mock()
        mock_lang.query.return_value = mock_query
        mock_query.captures.return_value = []
        return mock_lang
    
    @pytest.fixture
    def sample_kotlin_ast_node(self):
        """Create a sample Kotlin AST node for testing."""
        mock_node = Mock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (10, 0)
        mock_node.text = b"class MainActivity : AppCompatActivity()"
        return mock_node
    
    @pytest.fixture
    def sample_xml_ast_node(self):
        """Create a sample XML AST node for testing."""
        mock_node = Mock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (5, 0)
        mock_node.text = b"<LinearLayout></LinearLayout>"
        return mock_node
    
    def test_kotlin_language_initialization(self, mock_kotlin_language):
        """Test Kotlin language initialization."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=None), \
                 patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None), \
                 patch.object(StaticAnalysisAgent, '_initialize_kotlin_language', return_value=mock_kotlin_language), \
                 patch.object(StaticAnalysisAgent, '_initialize_xml_language', return_value=None):
                agent = StaticAnalysisAgent()
                assert 'kotlin' in agent.supported_languages
                assert agent.languages['kotlin'] == mock_kotlin_language
    
    def test_xml_language_initialization(self, mock_xml_language):
        """Test XML language initialization."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            with patch.object(StaticAnalysisAgent, '_initialize_python_language', return_value=None), \
                 patch.object(StaticAnalysisAgent, '_initialize_java_language', return_value=None), \
                 patch.object(StaticAnalysisAgent, '_initialize_kotlin_language', return_value=None), \
                 patch.object(StaticAnalysisAgent, '_initialize_xml_language', return_value=mock_xml_language):
                agent = StaticAnalysisAgent()
                assert 'xml' in agent.supported_languages
                assert agent.languages['xml'] == mock_xml_language
    
    def test_analyze_kotlin_ast(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test analyzing Kotlin AST."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            agent.supported_languages = ['kotlin']
            
            with patch.object(agent, '_check_kotlin_hardcoded_strings', return_value=[]), \
                 patch.object(agent, '_check_kotlin_null_safety_violations', return_value=[]), \
                 patch.object(agent, '_check_kotlin_companion_object_constants', return_value=[]), \
                 patch.object(agent, '_check_kotlin_android_logging', return_value=[]):
                
                result = agent.analyze_kotlin_ast(sample_kotlin_ast_node)
                
                assert isinstance(result, list)
                assert len(result) == 0  # No findings from mocked rules
    
    def test_analyze_xml_ast(self, mock_xml_language, sample_xml_ast_node):
        """Test analyzing XML AST."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            agent.supported_languages = ['xml']
            
            with patch.object(agent, '_check_android_manifest_permissions', return_value=[]), \
                 patch.object(agent, '_check_android_layout_performance', return_value=[]), \
                 patch.object(agent, '_check_android_hardcoded_sizes', return_value=[]):
                
                result = agent.analyze_xml_ast(sample_xml_ast_node)
                
                assert isinstance(result, list)
                assert len(result) == 0  # No findings from mocked rules
    
    def test_check_kotlin_hardcoded_strings_found(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test Kotlin hardcoded strings rule when violations are found."""
        string_node = Mock()
        string_node.start_point = (5, 10)
        string_node.text = b'"Hello World"'
        mock_captures = [(sample_kotlin_ast_node, {'string': string_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_kotlin_hardcoded_strings(sample_kotlin_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'KOTLIN_HARDCODED_STRINGS'
                assert findings[0]['line'] == 6
                assert findings[0]['severity'] == 'Warning'
                assert 'hardcoded string' in findings[0]['message'].lower()
    
    def test_check_kotlin_null_safety_violations_found(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test Kotlin null safety violations rule when !! operator is found."""
        operator_node = Mock()
        operator_node.start_point = (8, 15)
        mock_captures = [(sample_kotlin_ast_node, {'not_null': operator_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_kotlin_null_safety_violations(sample_kotlin_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'KOTLIN_NULL_SAFETY_VIOLATION'
                assert findings[0]['line'] == 9
                assert findings[0]['severity'] == 'Error'
                assert 'Not-null assertion operator' in findings[0]['message']
    
    def test_check_kotlin_companion_object_constants_found(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test Kotlin companion object constants rule."""
        name_node = Mock()
        name_node.start_point = (12, 8)
        name_node.text = b'MY_CONSTANT'
        prop_node = Mock()
        prop_node.start_point = (12, 8)
        mock_captures = [(sample_kotlin_ast_node, {'name': name_node, 'prop': prop_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_kotlin_companion_object_constants(sample_kotlin_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'KOTLIN_COMPANION_OBJECT_CONSTANTS'
                assert findings[0]['line'] == 13
                assert findings[0]['severity'] == 'Info'
                assert 'companion object' in findings[0]['message'].lower()
    
    def test_check_kotlin_android_logging_found(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test Kotlin Android logging rule when Log.d/v calls are found."""
        log_method_node = Mock()
        log_method_node.text = b'd'
        call_node = Mock()
        call_node.start_point = (20, 4)
        mock_captures = [(sample_kotlin_ast_node, {'log_method': log_method_node, 'call': call_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_kotlin_android_logging(sample_kotlin_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'KOTLIN_ANDROID_LOGGING'
                assert findings[0]['line'] == 21
                assert findings[0]['severity'] == 'Warning'
                assert 'Log.d()' in findings[0]['message']
    
    def test_check_android_manifest_permissions_found(self, mock_xml_language, sample_xml_ast_node):
        """Test Android manifest permissions rule when dangerous permissions are found."""
        attr_value_node = Mock()
        attr_value_node.text = b'"android.permission.CAMERA"'
        element_node = Mock()
        element_node.start_point = (3, 4)
        mock_captures = [(sample_xml_ast_node, {'attr_value': attr_value_node, 'element': element_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_android_manifest_permissions(sample_xml_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'ANDROID_DANGEROUS_PERMISSION'
                assert findings[0]['line'] == 4
                assert findings[0]['severity'] == 'Warning'
                assert 'dangerous permission' in findings[0]['message'].lower()
    
    def test_check_android_layout_performance_found(self, mock_xml_language, sample_xml_ast_node):
        """Test Android layout performance rule when nested LinearLayouts are found."""
        outer_element_node = Mock()
        outer_element_node.start_point = (7, 8)
        mock_captures = [(sample_xml_ast_node, {'outer_element': outer_element_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_android_layout_performance(sample_xml_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'ANDROID_NESTED_LINEARLAYOUT'
                assert findings[0]['line'] == 8
                assert findings[0]['severity'] == 'Warning'
                assert 'Nested LinearLayouts' in findings[0]['message']
    
    def test_check_android_hardcoded_sizes_found(self, mock_xml_language, sample_xml_ast_node):
        """Test Android hardcoded sizes rule when hardcoded dp/px values are found."""
        attr_name_node = Mock()
        attr_name_node.text = b'android:layout_width'
        attr_value_node = Mock()
        attr_value_node.start_point = (11, 12)
        attr_value_node.text = b'"100dp"'
        mock_captures = [(sample_xml_ast_node, {'attr_name': attr_name_node, 'attr_value': attr_value_node})]
        
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            
            with patch.object(agent, '_query_ast', return_value=mock_captures):
                findings = agent._check_android_hardcoded_sizes(sample_xml_ast_node)
                
                assert len(findings) == 1
                assert findings[0]['rule_id'] == 'ANDROID_HARDCODED_SIZE'
                assert findings[0]['line'] == 12
                assert findings[0]['severity'] == 'Info'
                assert 'hardcoded size' in findings[0]['message'].lower()
    
    def test_analyze_ast_kotlin_dispatch(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test that analyze_ast correctly dispatches to Kotlin analysis."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            agent.supported_languages = ['python', 'kotlin']
            
            with patch.object(agent, 'analyze_kotlin_ast', return_value=[]) as mock_analyze:
                result = agent.analyze_ast(sample_kotlin_ast_node, "/test/file.kt", "kotlin")
                
                assert result == []
                mock_analyze.assert_called_once_with(sample_kotlin_ast_node)
    
    def test_analyze_ast_xml_dispatch(self, mock_xml_language, sample_xml_ast_node):
        """Test that analyze_ast correctly dispatches to XML analysis."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            agent.supported_languages = ['python', 'xml']
            
            with patch.object(agent, 'analyze_xml_ast', return_value=[]) as mock_analyze:
                result = agent.analyze_ast(sample_xml_ast_node, "/test/file.xml", "xml")
                
                assert result == []
                mock_analyze.assert_called_once_with(sample_xml_ast_node)
    
    def test_kotlin_rules_no_findings(self, mock_kotlin_language, sample_kotlin_ast_node):
        """Test all Kotlin rules when no violations are found."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            
            with patch.object(agent, '_query_ast', return_value=[]):
                # Test each rule individually
                assert agent._check_kotlin_hardcoded_strings(sample_kotlin_ast_node) == []
                assert agent._check_kotlin_null_safety_violations(sample_kotlin_ast_node) == []
                assert agent._check_kotlin_companion_object_constants(sample_kotlin_ast_node) == []
                assert agent._check_kotlin_android_logging(sample_kotlin_ast_node) == []
    
    def test_xml_rules_no_findings(self, mock_xml_language, sample_xml_ast_node):
        """Test all XML rules when no violations are found."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['xml'] = mock_xml_language
            
            with patch.object(agent, '_query_ast', return_value=[]):
                # Test each rule individually
                assert agent._check_android_manifest_permissions(sample_xml_ast_node) == []
                assert agent._check_android_layout_performance(sample_xml_ast_node) == []
                assert agent._check_android_hardcoded_sizes(sample_xml_ast_node) == []
    
    def test_kotlin_xml_error_handling(self, mock_kotlin_language, mock_xml_language, sample_kotlin_ast_node, sample_xml_ast_node):
        """Test error handling in Kotlin and XML analysis."""
        with patch('src.core_engine.agents.static_analysis_agent.tree_sitter'):
            agent = StaticAnalysisAgent()
            agent.languages['kotlin'] = mock_kotlin_language
            agent.languages['xml'] = mock_xml_language
            
            # Test Kotlin error handling
            with patch.object(agent, '_check_kotlin_hardcoded_strings', side_effect=Exception("Test error")):
                result = agent.analyze_kotlin_ast(sample_kotlin_ast_node)
                assert isinstance(result, list)  # Should handle error gracefully
            
            # Test XML error handling
            with patch.object(agent, '_check_android_manifest_permissions', side_effect=Exception("Test error")):
                result = agent.analyze_xml_ast(sample_xml_ast_node)
                assert isinstance(result, list)  # Should handle error gracefully 