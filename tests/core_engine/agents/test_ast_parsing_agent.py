"""
Unit tests for ASTParsingAgent.

Tests the AST parsing functionality using Tree-sitter for Python code analysis.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the agent to test
from src.core_engine.agents.ast_parsing_agent import ASTParsingAgent


class TestASTParsingAgent:
    """Test cases for ASTParsingAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock tree-sitter to avoid dependency issues in tests
        self.mock_tree_sitter = Mock()
        self.mock_parser = Mock()
        self.mock_language = Mock()
        self.mock_node = Mock()
        
        # Configure mocks
        self.mock_tree_sitter.Parser.return_value = self.mock_parser
        self.mock_node.child_count = 3
        self.mock_node.has_error = False
        self.mock_node.start_point = (0, 0)
        self.mock_node.text = b"test_function"
        self.mock_node.type = "function_definition"
        self.mock_node.children = []
    
    @patch('src.core_engine.agents.ast_parsing_agent.tree_sitter')
    @patch('src.core_engine.agents.ast_parsing_agent.Parser')
    def test_init_success(self, mock_parser_class, mock_tree_sitter):
        """Test successful initialization of ASTParsingAgent."""
        # Arrange
        mock_tree_sitter.Parser = mock_parser_class
        mock_parser_instance = Mock()
        mock_parser_class.return_value = mock_parser_instance
        
        # Mock successful language loading
        with patch.object(ASTParsingAgent, '_load_python_language', return_value=self.mock_language):
            # Act
            agent = ASTParsingAgent()
            
            # Assert
            assert agent is not None
            assert 'python' in agent.supported_languages
            assert agent.parser is not None
            # Check that language property was set
            assert hasattr(mock_parser_instance, 'language')
    
    def test_init_no_tree_sitter(self):
        """Test initialization failure when tree-sitter is not available."""
        # Arrange & Act & Assert
        with patch('src.core_engine.agents.ast_parsing_agent.tree_sitter', None):
            with pytest.raises(ImportError, match="tree-sitter is not installed"):
                ASTParsingAgent()
    
    @patch('src.core_engine.agents.ast_parsing_agent.tree_sitter')
    @patch('src.core_engine.agents.ast_parsing_agent.Parser')
    def test_init_no_languages_loaded(self, mock_parser_class, mock_tree_sitter):
        """Test initialization failure when no language grammars can be loaded."""
        # Arrange
        mock_tree_sitter.Parser = mock_parser_class
        mock_parser_instance = Mock()
        mock_parser_class.return_value = mock_parser_instance
        
        # Mock failed language loading
        with patch.object(ASTParsingAgent, '_load_python_language', return_value=None):
            # Act & Assert
            with pytest.raises(Exception, match="No language grammars could be loaded"):
                ASTParsingAgent()
    
    def test_detect_language_python(self):
        """Test language detection for Python files."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
            agent.supported_languages = ['python']
        
        # Act & Assert
        assert agent._detect_language("test.py") == "python"
        assert agent._detect_language("test.pyx") == "python"
        assert agent._detect_language("test.pyi") == "python"
        assert agent._detect_language("test.java") is None  # Not supported
        assert agent._detect_language("test.txt") is None   # Not a code file
    
    def test_detect_language_case_insensitive(self):
        """Test that language detection is case insensitive."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
            agent.supported_languages = ['python']
        
        # Act & Assert
        assert agent._detect_language("Test.PY") == "python"
        assert agent._detect_language("TEST.PYX") == "python"
    
    @patch('src.core_engine.agents.ast_parsing_agent.tree_sitter')
    @patch('src.core_engine.agents.ast_parsing_agent.Parser')
    def test_parse_code_to_ast_success(self, mock_parser_class, mock_tree_sitter):
        """Test successful code parsing to AST."""
        # Arrange
        mock_tree_sitter.Parser = mock_parser_class
        mock_parser_instance = Mock()
        mock_parser_class.return_value = mock_parser_instance
        
        # Mock successful parsing
        mock_tree = Mock()
        mock_tree.root_node = self.mock_node
        mock_parser_instance.parse.return_value = mock_tree
        
        with patch.object(ASTParsingAgent, '_load_python_language', return_value=self.mock_language):
            agent = ASTParsingAgent()
            agent.parser = mock_parser_instance
            agent.languages = {'python': self.mock_language}
        
        # Act
        result = agent.parse_code_to_ast("def test(): pass", "python")
        
        # Assert
        assert result is not None
        assert result == self.mock_node
        # Check that language was set and parse was called
        mock_parser_instance.parse.assert_called_once()
    
    @patch('src.core_engine.agents.ast_parsing_agent.tree_sitter')
    @patch('src.core_engine.agents.ast_parsing_agent.Parser')
    def test_parse_code_to_ast_unsupported_language(self, mock_parser_class, mock_tree_sitter):
        """Test parsing with unsupported language."""
        # Arrange
        mock_tree_sitter.Parser = mock_parser_class
        mock_parser_instance = Mock()
        mock_parser_class.return_value = mock_parser_instance
        
        with patch.object(ASTParsingAgent, '_load_python_language', return_value=self.mock_language):
            agent = ASTParsingAgent()
            agent.parser = mock_parser_instance
            agent.languages = {'python': self.mock_language}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Language 'java' is not supported"):
            agent.parse_code_to_ast("public class Test {}", "java")
    
    @patch('src.core_engine.agents.ast_parsing_agent.tree_sitter')
    @patch('src.core_engine.agents.ast_parsing_agent.Parser')
    def test_parse_code_to_ast_parsing_failure(self, mock_parser_class, mock_tree_sitter):
        """Test handling of parsing failures."""
        # Arrange
        mock_tree_sitter.Parser = mock_parser_class
        mock_parser_instance = Mock()
        mock_parser_class.return_value = mock_parser_instance
        
        # Mock parsing failure
        mock_parser_instance.parse.return_value = None
        
        with patch.object(ASTParsingAgent, '_load_python_language', return_value=self.mock_language):
            agent = ASTParsingAgent()
            agent.parser = mock_parser_instance
            agent.languages = {'python': self.mock_language}
        
        # Act
        result = agent.parse_code_to_ast("invalid syntax $$", "python")
        
        # Assert
        assert result is None
    
    def test_parse_file_to_ast_success(self):
        """Test successful file parsing to AST."""
        # Arrange
        test_content = "def hello():\n    print('Hello, World!')"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            with patch.object(ASTParsingAgent, '_initialize_parsers'):
                agent = ASTParsingAgent()
                agent.supported_languages = ['python']
                
                # Mock the parse_code_to_ast method
                with patch.object(agent, 'parse_code_to_ast', return_value=self.mock_node) as mock_parse:
                    # Act
                    result = agent.parse_file_to_ast(temp_file_path)
                    
                    # Assert
                    assert result == self.mock_node
                    mock_parse.assert_called_once_with(test_content, 'python')
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_file_to_ast_unsupported_file(self):
        """Test parsing unsupported file type."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not code")
            temp_file_path = f.name
        
        try:
            with patch.object(ASTParsingAgent, '_initialize_parsers'):
                agent = ASTParsingAgent()
                agent.supported_languages = ['python']
                
                # Act
                result = agent.parse_file_to_ast(temp_file_path)
                
                # Assert
                assert result is None
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_file_to_ast_file_not_found(self):
        """Test parsing non-existent file."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
            agent.supported_languages = ['python']
        
        # Act
        result = agent.parse_file_to_ast("/nonexistent/file.py")
        
        # Assert
        assert result is None
    
    def test_extract_structural_info_python(self):
        """Test extraction of structural information from Python AST."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
        
        # Create a simple mock structure that will work with the traversal
        mock_root = Mock()
        mock_root.children = []
        
        # Mock the _count_nodes method to avoid recursion issues
        with patch.object(agent, '_count_nodes', return_value=10):
            # Mock the _traverse_python_ast method to simulate finding structures
            with patch.object(agent, '_traverse_python_ast') as mock_traverse:
                def mock_traverse_side_effect(node, structure):
                    # Simulate finding a class
                    structure["classes"].append({
                        "name": "TestClass",
                        "line": 1,
                        "methods": [{"name": "test_method", "line": 2}]
                    })
                    # Simulate finding a function
                    structure["functions"].append({
                        "name": "standalone_function",
                        "line": 6
                    })
                    # Simulate finding an import
                    structure["imports"].append({
                        "type": "import_statement",
                        "line": 1,
                        "text": "import os"
                    })
                
                mock_traverse.side_effect = mock_traverse_side_effect
                
                # Act
                result = agent.extract_structural_info(mock_root, "python")
        
        # Assert
        assert result["language"] == "python"
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "TestClass"
        assert len(result["classes"][0]["methods"]) == 1
        assert result["classes"][0]["methods"][0]["name"] == "test_method"
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "standalone_function"
        assert len(result["imports"]) == 1
        assert result["imports"][0]["text"] == "import os"
    
    def test_extract_structural_info_unsupported_language(self):
        """Test structural extraction for unsupported language."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
        
        # Act
        result = agent.extract_structural_info(self.mock_node, "java")
        
        # Assert
        assert result["language"] == "java"
        assert result["classes"] == []
        assert result["functions"] == []
        assert result["imports"] == []
        assert "node_count" in result
    
    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
            agent.supported_languages = ['python', 'java']
        
        # Act
        result = agent.get_supported_languages()
        
        # Assert
        assert result == ['python', 'java']
        # Ensure it returns a copy, not the original list
        result.append('kotlin')
        assert 'kotlin' not in agent.supported_languages
    
    def test_is_language_supported(self):
        """Test checking if a language is supported."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
            agent.supported_languages = ['python']
        
        # Act & Assert
        assert agent.is_language_supported('python') is True
        assert agent.is_language_supported('java') is False
        assert agent.is_language_supported('kotlin') is False
    
    def test_count_nodes(self):
        """Test AST node counting functionality."""
        # Arrange
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
        
        # Create a mock AST structure
        child1 = Mock()
        child1.children = []
        
        child2 = Mock()
        child2.children = [Mock(children=[]), Mock(children=[])]
        
        root = Mock()
        root.children = [child1, child2]
        
        # Act
        result = agent._count_nodes(root)
        
        # Assert
        # Root(1) + child1(1) + child2(1) + child2's children(2) = 5
        assert result == 5
    
    @patch('src.core_engine.agents.ast_parsing_agent.os.path.exists')
    def test_load_python_language_from_package(self, mock_exists):
        """Test loading Python language from tree-sitter-python package."""
        # Arrange
        mock_exists.return_value = False  # No grammar directories found
        
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
        
        # Mock successful import and Language constructor
        mock_capsule = Mock()
        mock_language_func = Mock(return_value=mock_capsule)
        
        # Mock the entire tree_sitter_python module
        mock_module = Mock()
        mock_module.language = mock_language_func
        
        with patch.dict('sys.modules', {'tree_sitter_python': mock_module}):
            with patch('src.core_engine.agents.ast_parsing_agent.Language', return_value=self.mock_language) as mock_lang_constructor:
                # Act
                result = agent._load_python_language()
                
                # Assert
                assert result == self.mock_language
                mock_language_func.assert_called_once()
                mock_lang_constructor.assert_called_once_with(mock_capsule)
    
    @patch('src.core_engine.agents.ast_parsing_agent.os.path.exists')
    def test_load_python_language_package_not_found(self, mock_exists):
        """Test handling when tree-sitter-python package is not found."""
        # Arrange
        mock_exists.return_value = False  # No grammar directories found
        
        with patch.object(ASTParsingAgent, '_initialize_parsers'):
            agent = ASTParsingAgent()
        
        # Mock ImportError for tree-sitter-python by patching the import
        with patch('builtins.__import__', side_effect=ImportError("No module named 'tree_sitter_python'")):
            # Act
            result = agent._load_python_language()
            
            # Assert
            assert result is None 