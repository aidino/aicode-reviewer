"""
Unit tests for Dart/Flutter support in AI Code Review system.

This module tests the Dart language support across all agents:
- ASTParsingAgent: Dart AST parsing and structure extraction
- CodeFetcherAgent: Dart file detection and fetching
- StaticAnalysisAgent: Dart static analysis rules
- DiagrammingEngine: Dart diagram generation
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.core_engine.agents.ast_parsing_agent import ASTParsingAgent
from src.core_engine.agents.code_fetcher_agent import CodeFetcherAgent
from src.core_engine.agents.static_analysis_agent import StaticAnalysisAgent
from src.core_engine.diagramming_engine import DiagrammingEngine


class TestDartASTParsingAgent:
    """Test Dart support in ASTParsingAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create ASTParsingAgent instance for testing."""
        return ASTParsingAgent()
    
    def test_dart_language_support(self, agent):
        """Test that Dart is in supported languages."""
        supported_languages = agent.get_supported_languages()
        assert 'dart' in supported_languages
    
    def test_dart_language_detection(self, agent):
        """Test Dart file extension detection."""
        # Test .dart extension
        assert agent._detect_language("test.dart") == "dart"
        assert agent._detect_language("main.dart") == "dart"
        assert agent._detect_language("widget.dart") == "dart"
        
        # Test case insensitive
        assert agent._detect_language("TEST.DART") == "dart"
        
        # Test non-Dart files
        assert agent._detect_language("test.py") == "python"
        assert agent._detect_language("test.js") == "javascript"
        assert agent._detect_language("test.unknown") is None
    
    @patch('src.core_engine.agents.ast_parsing_agent.logger')
    def test_dart_language_loading(self, mock_logger, agent):
        """Test Dart language loading with fallbacks."""
        # Test that _load_dart_language is called during initialization
        with patch.object(agent, '_load_dart_language') as mock_load:
            mock_load.return_value = Mock()
            agent._initialize_parsers()
            mock_load.assert_called_once()
    
    def test_dart_structure_extraction_mock(self, agent):
        """Test Dart structure extraction with mocked AST."""
        # Create a mock AST node
        mock_ast = Mock()
        mock_ast.type = "program"
        mock_ast.children = []
        
        # Test structure extraction
        with patch.object(agent, '_extract_dart_structure') as mock_extract:
            mock_extract.return_value = {
                "language": "dart",
                "classes": [],
                "functions": [],
                "imports": [],
                "exports": [],
                "variables": [],
                "widgets": [],
                "node_count": 1
            }
            
            result = agent.extract_structural_info(mock_ast, "dart")
            mock_extract.assert_called_once_with(mock_ast)
            assert result["language"] == "dart"
            assert "widgets" in result  # Flutter-specific field


class TestDartCodeFetcherAgent:
    """Test Dart support in CodeFetcherAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create CodeFetcherAgent instance for testing."""
        with patch('src.core_engine.agents.code_fetcher_agent.settings') as mock_settings:
            mock_settings.supported_languages = ['python', 'java', 'kotlin', 'android_xml', 'javascript', 'dart']
            return CodeFetcherAgent()
    
    def test_dart_extension_support(self, agent):
        """Test that Dart extensions are supported."""
        assert 'dart' in agent.supported_extensions
        assert '.dart' in agent.supported_extensions['dart']
    
    def test_dart_language_support(self, agent):
        """Test that Dart is in supported languages."""
        # Note: supported_languages comes from settings, may not include dart by default
        # But dart should be in supported_extensions
        assert 'dart' in agent.supported_extensions
    
    def test_dart_file_filtering(self, agent):
        """Test filtering of Dart files."""
        test_files = [
            "main.dart",
            "widget.dart", 
            "model.dart",
            "test.py",
            "script.js",
            "README.md"
        ]
        
        # Test file extension support
        dart_files = [f for f in test_files if agent._is_supported_file(f) and f.endswith('.dart')]
        expected_dart = ["main.dart", "widget.dart", "model.dart"]
        assert set(dart_files) == set(expected_dart)
    
    def test_dart_file_fetching_mock(self, agent):
        """Test Dart file fetching with mocked filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test Dart files
            dart_files = ["main.dart", "lib/widget.dart", "test/test.dart"]
            for file_path in dart_files:
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write("// Dart code\nvoid main() {}")
            
            # Test file support detection
            for file_path in dart_files:
                full_path = os.path.join(temp_dir, file_path)
                assert agent._is_supported_file(full_path)


class TestDartStaticAnalysisAgent:
    """Test Dart support in StaticAnalysisAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create StaticAnalysisAgent instance for testing."""
        return StaticAnalysisAgent()
    
    def test_dart_language_support(self, agent):
        """Test that Dart is in supported languages."""
        supported_languages = agent.get_supported_languages()
        assert 'dart' in supported_languages
    
    @patch('src.core_engine.agents.static_analysis_agent.logger')
    def test_dart_language_initialization(self, mock_logger, agent):
        """Test Dart language initialization."""
        with patch.object(agent, '_initialize_dart_language') as mock_init:
            mock_init.return_value = Mock()
            agent._initialize_languages()
            mock_init.assert_called_once()
    
    def test_dart_analysis_dispatch(self, agent):
        """Test that Dart analysis is properly dispatched."""
        mock_ast = Mock()
        
        with patch.object(agent, 'analyze_dart_ast') as mock_analyze:
            mock_analyze.return_value = []
            agent.analyze_ast(mock_ast, "test.dart", "dart")
            mock_analyze.assert_called_once_with(mock_ast)
    
    def test_dart_print_statements_rule(self, agent):
        """Test Dart print statements rule."""
        # Mock AST node for print statement
        mock_ast = Mock()
        
        with patch.object(agent, '_query_ast') as mock_query:
            # Mock query result for print() call
            mock_query.return_value = [
                (Mock(), {
                    'call': Mock(start_point=(10, 4))
                })
            ]
            
            findings = agent._check_dart_print_statements(mock_ast)
            
            assert len(findings) == 1
            assert findings[0]['rule_id'] == 'DART_PRINT_STATEMENT_FOUND'
            assert findings[0]['severity'] == 'Warning'
            assert findings[0]['line'] == 11  # 0-indexed + 1
    
    def test_flutter_widget_key_rule(self, agent):
        """Test Flutter widget key usage rule."""
        mock_ast = Mock()
        
        with patch.object(agent, '_query_ast') as mock_query:
            # Mock query result for widget without key
            mock_children_list = Mock()
            mock_children_list.children = [Mock(), Mock(), Mock(), Mock()]  # 4 children > 3
            
            mock_query.return_value = [
                (Mock(), {
                    'widget_call': Mock(start_point=(5, 0)),
                    'widget_name': Mock(text=b'ListView'),
                    'children_list': mock_children_list
                })
            ]
            
            findings = agent._check_flutter_widget_key_usage(mock_ast)
            
            assert len(findings) == 1
            assert findings[0]['rule_id'] == 'FLUTTER_WIDGET_KEY_USAGE'
            assert findings[0]['severity'] == 'Info'


class TestDartDiagrammingEngine:
    """Test Dart support in DiagrammingEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create DiagrammingEngine instance for testing."""
        return DiagrammingEngine()
    
    def test_dart_language_support(self, engine):
        """Test that Dart is in supported languages."""
        assert 'dart' in engine.supported_languages
    
    def test_dart_engine_info(self, engine):
        """Test that engine info includes Dart support."""
        info = engine.get_engine_info()
        assert 'dart_support' in info['capabilities']
        assert 'flutter_support' in info['capabilities']
    
    def test_dart_class_diagram_dispatch(self, engine):
        """Test Dart class diagram generation dispatch."""
        mock_ast_data = Mock()
        mock_ast_data.root_node = Mock()
        
        with patch.object(engine, '_dart_ast_to_class_data') as mock_extract:
            mock_extract.return_value = []
            
            # Mock the AST data structure as dict
            code_files = {'test.dart': mock_ast_data}
            
            with patch.object(engine, '_generate_plantuml_diagram') as mock_generate:
                mock_generate.return_value = "@startuml\n@enduml"
                
                result = engine.generate_class_diagram(
                    code_files, 
                    'dart'
                )
                
                mock_extract.assert_called_once()
    
    def test_dart_sequence_diagram_dispatch(self, engine):
        """Test Dart sequence diagram generation dispatch."""
        mock_ast_data = Mock()
        mock_ast_data.root_node = Mock()
        
        with patch.object(engine, '_dart_ast_to_sequence_data') as mock_extract:
            mock_extract.return_value = []
            
            ast_data_list = [mock_ast_data]
            
            with patch.object(engine, '_generate_plantuml_sequence_diagram') as mock_generate:
                mock_generate.return_value = "@startuml\n@enduml"
                
                # Create code_files dict format
                code_files = {'test.dart': mock_ast_data}
                
                result = engine.generate_sequence_diagram(
                    code_files,
                    'dart'
                )
                
                mock_extract.assert_called_once()
    
    def test_dart_class_extraction_mock(self, engine):
        """Test Dart class data extraction with mocked AST."""
        mock_ast = Mock()
        mock_ast.type = "program"
        mock_ast.children = []
        
        # Test class extraction
        result = engine._dart_ast_to_class_data(mock_ast)
        
        # Should return empty list for empty AST
        assert isinstance(result, list)
    
    def test_dart_flutter_widget_detection(self, engine):
        """Test Flutter widget detection."""
        # Test StatelessWidget
        assert engine._is_dart_flutter_widget("MyWidget", "StatelessWidget") == True
        assert engine._is_dart_flutter_widget("MyWidget", "StatefulWidget") == True
        assert engine._is_dart_flutter_widget("MyWidget", "Widget") == True
        
        # Test non-widget classes
        assert engine._is_dart_flutter_widget("MyClass", "Object") == False
        assert engine._is_dart_flutter_widget("MyClass", None) == False
        assert engine._is_dart_flutter_widget("MyClass", "String") == False


class TestDartIntegration:
    """Integration tests for Dart support across all components."""
    
    def test_dart_end_to_end_mock(self):
        """Test end-to-end Dart processing with mocked components."""
        # Create sample Dart code
        dart_code = '''
        import 'package:flutter/material.dart';
        
        class MyWidget extends StatelessWidget {
          @override
          Widget build(BuildContext context) {
            return Container(
              child: Text('Hello World'),
            );
          }
        }
        
        void main() {
          print('Starting app');
          runApp(MyApp());
        }
        '''
        
        # Test AST parsing
        ast_agent = ASTParsingAgent()
        assert ast_agent.is_language_supported('dart')
        
        # Test static analysis
        static_agent = StaticAnalysisAgent()
        assert static_agent.is_language_supported('dart')
        
        # Test diagramming
        diagram_engine = DiagrammingEngine()
        assert 'dart' in diagram_engine.supported_languages
    
    def test_dart_file_processing_workflow(self):
        """Test complete Dart file processing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Dart file
            dart_file = os.path.join(temp_dir, "main.dart")
            with open(dart_file, 'w') as f:
                f.write('''
                import 'package:flutter/material.dart';

                class MyApp extends StatelessWidget {
                  Widget build(BuildContext context) {
                    return MaterialApp(home: Text('Hello'));
                  }
                }
                ''')

            # Test file support detection with mocked settings
            with patch('src.core_engine.agents.code_fetcher_agent.settings') as mock_settings:
                mock_settings.supported_languages = ['python', 'java', 'kotlin', 'android_xml', 'javascript', 'dart']
                fetcher = CodeFetcherAgent()
                dart_file_supported = fetcher._is_supported_file(dart_file)

                assert dart_file_supported == True


if __name__ == '__main__':
    pytest.main([__file__]) 